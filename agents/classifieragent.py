
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from log_trace.logtrace import log_agent_trace
from langchain_core.exceptions import OutputParserException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    before_sleep_log
)
from prompts.classifier_prompt import classifier_prompt 


class ClassifierAgent:
    """
    Agent responsible for classifying aggregated document data into a predicted
    document type using a Groq-hosted language model.

    This agent:
    - Builds a classification prompt template.
    - Invokes the LLM with structured JSON output enforcement.
    - Parses and validates the JSON response.
    - Updates shared pipeline state with classification results.
    - Tracks token usage.
    - Logs trace information for Responsible AI observability.
    """
    def __init__(self,api_key,model):
        """
        Initialize the ClassifierAgent.

        Args:
            api_key (str): API key used to authenticate with the Groq LLM service.
            model (str): Name of the Groq model to use for classification.
        """
        self.model=model
        #self.temperature=temperature
        self.api_key = api_key
    def llm_classifier_prompt(self):
        """
        Construct and return the prompt template used for document classification.

        Returns:
            PromptTemplate: A LangChain PromptTemplate configured with the
            classifier prompt and expecting 'aggregated_json' as input.
        """
        prompt = classifier_prompt
        return PromptTemplate(template=prompt,input_variable=["aggregated_json"])
    
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
    retry=retry_if_exception_type((
        OutputParserException,
        ValueError,
        ConnectionError,
        TimeoutError,
    )),
    #before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
    )
    def run(self,state):
        """
        Execute the classification workflow.

        This method:
        - Builds the prompt.
        - Invokes the Groq LLM with JSON response enforcement.
        - Parses the model output into structured JSON.
        - Updates the pipeline state with classification results.
        - Tracks token usage.
        - Logs trace data for auditability and Responsible AI compliance.

        The method is retried automatically (up to 3 times) in case of:
        - OutputParserException
        - ValueError
        - ConnectionError
        - TimeoutError

        Args:
            state (dict): Shared pipeline state containing:
                - 'agg_json' (dict or str): Aggregated document data.
                - 'token_usage' (list): List to append token usage metadata.
                - Optional 'traces' (list): Existing trace entries.

        Returns:
            dict: Updated state containing:
                - 'classifier_output': Parsed classification result.
                - 'doc_type': Predicted document type.
                - Updated 'token_usage'.
                - Appended 'traces' entry.
        """

        prompt=self.llm_classifier_prompt()
        llm=ChatGroq(model=self.model,api_key=self.api_key,model_kwargs={
            "response_format": {"type": "json_object"}  # 🔥 CRITICAL
        }
    )
        parser=JsonOutputParser()
        chain=prompt|llm
        result_not_parsed=chain.invoke({"aggregated_json":state['agg_json']})
        token_usage=result_not_parsed.usage_metadata
        state['token_usage'].append({
                                    'classifier_agent':token_usage,
                                    'model_name':self.model})
        # if "reasoning" in result_not_parsed and not isinstance(result_not_parsed["reasoning"], str):
        #     result_not_parsed["reasoning"] = str(result_not_parsed["reasoning"])

        # Parse JSON
        result = parser.parse(result_not_parsed.content)
        state['classifier_output']=result
        state['doc_type']=result.get('predicted_document_type')
        #logging for responsible AI
        trace_entry = log_agent_trace(
            agent_name="ClassifierAgent",
            input_data=state['agg_json'],
            output_data={
                "predicted_document_type": result.get("predicted_document_type"),
                "confidence": result.get("confidence")
            },
            metadata={"reasoning": result.get("reasoning")}
        )

        # Initialize traces list if missing
        if "traces" not in state or state["traces"] is None:
            state["traces"] = []

        # Append trace instead of overwriting
        state["traces"].append(trace_entry)

        return state

if __name__=='__main__':
    print(log_agent_trace('i',"d",'d','f'))
        