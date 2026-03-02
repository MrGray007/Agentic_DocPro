from prompts.redact_prompts import PII_FIELD_MAP,REDACTION_PROMPT,MASK_TAGS
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from log_trace.logtrace import log_agent_trace
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import json
class RedactAgent:
    """
    Agent responsible for performing PII redaction on extracted structured data
    using a Groq-hosted language model and evaluating the redaction quality.

    This agent:
    - Sends extracted JSON to an LLM for PII masking.
    - Parses structured redacted output.
    - Evaluates redaction performance using schema-based expectations.
    - Computes precision, recall, and F1 metrics.
    - Tracks token usage and logs Responsible AI traces.
    """
    def __init__(self,api_key,model="llama-3.1-8b-instant"):
        """
        Initialize the RedactAgent.

        Args:
            api_key (str): API key used to authenticate with the Groq LLM service.
            model (str, optional): Groq model name for redaction.
                Defaults to "llama-3.1-8b-instant".
        """
        self.model=model
        #self.temperature=temperature
        self.api_key = api_key
    def get_nested(self,data, path):
        """
        Retrieve a nested value from a dictionary using dot-separated path notation.

        Supports both dictionary traversal and shallow list handling.

        Args:
            data (dict): Input dictionary.
            path (str): Dot-separated key path (e.g., "user.contact.email").

        Returns:
            Any: The retrieved value, a list of values (if traversing list items),
            or None if the path does not exist.
        """
        keys = path.split(".")
        obj = data

        for key in keys:
            if isinstance(obj, list):
                values = []
                for item in obj:
                    if key in item:
                        values.append(item[key])
                return values

            if not isinstance(obj, dict):
                return None

            obj = obj.get(key)

        return obj
    def evaluate_redaction(self,original_json, redacted_json, doc_type):
        """
        Evaluate the quality of PII redaction using schema-based expectations.

        This method compares expected masked fields (based on document type)
        against the LLM-generated redacted output and computes:
        - True Positives (TP)
        - False Positives (FP)
        - False Negatives (FN)
        - Precision
        - Recall
        - F1 Score

        Args:
            original_json (dict): The original extracted JSON before redaction.
            redacted_json (dict): The LLM-generated redacted JSON.
            doc_type (str): The classified document type.

        Returns:
            dict: Dictionary containing evaluation metrics and counts.
        """

        field_map = PII_FIELD_MAP.get(doc_type, {})

        TP = 0
        FN = 0
        total_expected = 0

        for path, expected_tag in field_map.items():

            orig_val = self.get_nested(original_json, path)
            red_val = self.get_nested(redacted_json, path)

            # -------- Handle list fields safely --------
            if isinstance(orig_val, list):

                red_val = red_val if isinstance(red_val, list) else []

                for i, o in enumerate(orig_val):

                    if not o:
                        continue

                    total_expected += 1

                    r = red_val[i] if i < len(red_val) else None

                    if r == expected_tag:
                        TP += 1
                    else:
                        FN += 1

            # -------- Handle single value --------
            else:
                if orig_val:

                    total_expected += 1

                    if red_val == expected_tag:
                        TP += 1
                    else:
                        FN += 1

        # Count all predicted masks
        total_predicted = sum(
            str(redacted_json).count(tag) for tag in MASK_TAGS
        )

        FP = max(total_predicted - TP, 0)

        precision = TP/(TP+FP) if TP+FP else 0
        recall = TP/(TP+FN) if TP+FN else 0
        f1 = 2*precision*recall/(precision+recall) if precision+recall else 0

        return {
            "tp": TP,
            "fp": FP,
            "fn": FN,
            "precision": round(precision,3),
            "recall": round(recall,3),
            "f1": round(f1,3),
            "total_expected": total_expected,
            "total_predicted": total_predicted
        }
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def run(self,state):
        """
        Execute LLM-based PII redaction and compute evaluation metrics.

        This method:
        - Converts extracted structured data into formatted JSON text.
        - Sends it to the LLM for PII masking.
        - Parses structured redacted output.
        - Computes redaction quality metrics.
        - Tracks token usage.
        - Logs Responsible AI trace metadata.

        Automatically retries up to 3 times with fixed wait if failure occurs.

        Args:
            state (dict): Shared pipeline state containing:
                - 'extraction_json' (dict): Extracted structured data.
                - 'doc_type' (str): Document classification type.
                - 'token_usage' (list): Token usage tracking list.
                - Optional 'traces' (list): Trace log entries.

        Returns:
            dict: Updated state containing:
                - 'redacted_report' with redacted JSON and metrics.
                - Updated 'token_usage'.
                - Appended 'traces' entry.
        """

        """
        LLM-based redaction + schema-based evaluation
        """
        original_json = state["extraction_json"]
        doc_type = state["doc_type"]

        # Convert dict to string for LLM
        document_text = json.dumps(original_json, indent=2)

        prompt = PromptTemplate(
            input_variables=["document_text"],
            template=REDACTION_PROMPT
        )

        formatted_prompt = prompt.format(document_text=document_text)

        # LLM call
        llm = ChatGroq(model=self.model,api_key=self.api_key, model_kwargs={
            "response_format": {"type": "json_object"}  # 🔥 CRITICAL
        }
    )
        result_not_parsed = llm.invoke(formatted_prompt)
        
        # redacted_json = parser.parse(redacted_str.content)
        token_usage=result_not_parsed.usage_metadata
        state['token_usage'].append({
                                    'redactor_agent':token_usage,
                                    'model_name':self.model})
        parser = JsonOutputParser()
        redacted_json=parser.parse(result_not_parsed.content)
        # ------------------------------
        # Compute Metrics
        # ------------------------------
        metrics = self.evaluate_redaction(
            original_json,
            redacted_json,
            doc_type
        )

        MASK_TAGS = ['[NAME]', '[EMAIL]', '[PHONE]', '[ADDRESS]', '[ID]',
                    '[BANK]', '[DOB]', '[CARD]', '[SIGNATURE]']

        # Use string representation of JSON for counting
        redacted_preview_str = json.dumps(redacted_json)

        tag_counts = {tag: redacted_preview_str.count(tag) for tag in MASK_TAGS}

        state["redacted_report"] = {
            "redacted_json": redacted_json,
            "pii_tag_counts": tag_counts,
            "total_masks": sum(tag_counts.values()),
            "pii_metrics": metrics
        }

        # Responsible AI trace logging
        trace_entry = log_agent_trace(
        agent_name="RedactAgent",
        input_data={
            "extracted_preview": str(original_json)[:500],
            "doc_type": doc_type
        },
        output_data={
            "redacted_preview": str(redacted_json)[:500],
            "pii_metrics": metrics,
            "mask_counts": tag_counts
        },
        metadata={
            "attempt": state.get("redaction_attempts", 1)
        }
    )

    # Append trace instead of overwriting
        if "traces" not in state or state["traces"] is None:
            state["traces"] = []
        state["traces"].append(trace_entry)

        return state