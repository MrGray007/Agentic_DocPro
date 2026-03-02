from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from log_trace.logtrace import log_agent_trace
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import time
from prompts.self_repair_extractor_prompts import selfrepair_prompts

class SelfRepairExtractorAgent:
    """
    Agent responsible for repairing invalid or schema-noncompliant extracted JSON
    using LLM-based self-correction with fallback model support.

    This agent:
    - Detects validation errors from prior extraction steps.
    - Generates a repair prompt based on document type.
    - Attempts correction using multiple fallback LLMs sequentially.
    - Parses corrected JSON output.
    - Logs repair attempts for Responsible AI traceability.
    """
    def __init__(self,api_key):
        """
        Initialize the SelfRepairExtractorAgent.

        Args:
            api_key (str): API key for authenticating LLM calls.
        """

        #self.temperature=temperature
        self.api_key = api_key
        self.FALLBACK_LLMS = ["openai/gpt-oss-120b",'llama-3.1-8b-instant',"llama-3.3-70b-versatile"]

    def llm_invoke(self,model_name, prompt):
        """
        Invoke a single LLM with the given prompt.

        Args:
            model_name (str): Name of the LLM model to use.
            prompt (str): Prompt string to send to the LLM.

        Returns:
            str: The LLM-generated output content.
        """
        llm=ChatGroq(model=model_name,api_key=self.api_key )
        response=llm.invoke(prompt)
        return response.content
    def call_fallback_llms(self,prompt) -> str:
        """
        Attempt to call multiple fallback LLMs in sequence until one succeeds.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            tuple: A tuple containing the LLM response string and the model name used.

        Raises:
            Exception: If all fallback LLMs fail.
        """

        """
        Try multiple LLMs in sequence until one succeeds.
        """
        for model_name in self.FALLBACK_LLMS:
            try:
                # Replace with your actual LLM invocation code
                response = self.llm_invoke(model_name, prompt)  
                return response,model_name
            except Exception as e:
                print(f"{model_name} failed: {e}, trying next LLM...")
                time.sleep(1)
        raise Exception("All fallback LLMs failed.")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
    def run(self,state):#,extracted_json: dict, validation_errors: list, resume_text: str,doc_type:str) -> dict:
        """
    Perform self-repair on extracted resume JSON using LLMs with fallback support.

    This method:
    - Retrieves validation errors from the pipeline state.
    - Selects the appropriate self-repair prompt based on the document type.
    - Calls multiple LLMs in sequence until one succeeds in generating corrected JSON.
    - Parses the corrected JSON string into a Python dictionary.
    - Updates the pipeline state with the corrected extraction.
    - Logs Responsible AI trace information including model used and repair attempt.
    - Increments the repair attempt counter in the state.

    Args:
        state (dict): Shared pipeline state containing:
            - 'extraction_json' (dict): The current extracted data.
            - 'validation_report' (dict): Contains 'validation_errors' list.
            - 'doc_type' (str): The type of document being processed.
            - 'context' (str): Optional context string for prompt generation.
            - 'self_repair' (list): Trace logs for self-repair steps.
            - 'repair_attempts' (int): Counter for repair attempts.

    Returns:
        dict: Updated pipeline state including:
            - Corrected 'extraction_json'.
            - Appended self-repair trace entry.
            - Incremented 'repair_attempts'.
        """
        
        """
        SelfRepairNode for resume JSON using LLM.
        """
        validation_errors=state['validation_report'].get('validation_errors')
        doc_type=state['doc_type']
        prompt = selfrepair_prompts.get(doc_type).invoke(
            {"extracted_json":state['extraction_json'],
            "validation_errors":validation_errors,
            'context':state['context']}
        )
        
        corrected_json_str,model_used = self.call_fallback_llms(prompt)
        
        # Convert corrected string to dict
        parser=JsonOutputParser()
        #print(corrected_json_str)
        corrected_json = parser.parse(corrected_json_str)
        state['extraction_json']=corrected_json
        
        # Optional: validate with Pydantic
        # from schemas import ResumeSchema
        # validated_resume = ResumeSchema.parse_obj(corrected_json)
        
        # Responsible AI logging
        state['self_repair'].append(log_agent_trace(
            agent_name="SelfRepairNode",
            input_data={
                "extracted_preview": str(state['extraction_json'])[:500],
                "validation_errors": validation_errors
            },
            output_data={
                "corrected_preview": str(corrected_json)[:500]
            },
            metadata={
                "model_used": model_used,
                "repair_attempt": state['repair_attempts'],
                "doc_type": doc_type
            }
        ))
        state["repair_attempts"]+=1
        print('Repair completed')
        return state
