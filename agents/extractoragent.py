from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from log_trace.logtrace import log_agent_trace
from prompts.extractor_prompt import prompt_map
from langchain_core.exceptions import OutputParserException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)

class ExtractorAgent:
    """
    Agent responsible for extracting structured information from classified documents
    using a Groq-hosted language model.

    This agent:
    - Filters relevant document chunks based on predicted document type.
    - Builds contextual input from raw text and tables.
    - Selects the appropriate extraction prompt dynamically.
    - Invokes the LLM with enforced JSON output.
    - Parses and stores structured extraction results.
    - Tracks token usage and logs trace metadata for observability.
    """
    def __init__(self,api_key,model):
        """
        Initialize the ExtractorAgent.

        Args:
            api_key (str): API key used to authenticate with the Groq LLM service.
            model (str): Name of the Groq model to use for extraction.
        """
        self.model=model
        #self.temperature=temperature
        self.api_key = api_key
    def filter_relevant_chunks(self,chunk_docs, predicted_doc_type):
        """
        Filter document chunks that contain signals relevant to the predicted document type.

        The method parses each chunk's JSON content and selects chunks
        based on predefined signal categories per document type.

        Args:
            chunk_docs (list): List of LangChain Document objects containing
                JSON-formatted page_content.
            predicted_doc_type (str): The classified document type
                (e.g., "contract", "resume", "invoice").

        Returns:
            list: A list of filtered Document objects considered relevant
            for extraction.
        """
        """
        Filter chunks that contain signals relevant to the predicted document type.
        """
        relevant_chunks = []
        for doc in chunk_docs:
            parser = JsonOutputParser()
            chunk_json = parser.parse(doc.page_content)
            
            signals = chunk_json.get("document_signals", {})
            include_chunk = False
            
            if predicted_doc_type == "contract":
                # legal, financial, compliance signals are most relevant
                for sig in ["legal", "financial", "compliance"]:
                    if signals.get(sig):
                        include_chunk = True
                        break
            elif predicted_doc_type == "resume":
                # employment, identity signals
                for sig in ["employment", "identity",'technical']:
                    if signals.get(sig):
                        include_chunk = True
                        break
            elif predicted_doc_type == "invoice":
                # employment, identity signals
                for sig in ["legal", "financial", "compliance",'technical']:
                    if signals.get(sig):
                        include_chunk = True
                        break
            else:
                # fallback: include any chunk with non-empty signals
                if any(v for v in signals.values()):
                    include_chunk = True
                    
            if include_chunk:
                relevant_chunks.append(doc)
        
        return relevant_chunks
    def query_gen(self,lan_docs,doc_type):
        """
        Generate a consolidated textual context from relevant document chunks.

        This method:
        - Filters relevant chunks using document signals.
        - Extracts raw text and HTML tables from metadata.
        - Concatenates them into a single context string.

        Args:
            lan_docs (list): List of LangChain Document objects containing metadata.
            doc_type (str): The classified document type.

        Returns:
            str: Aggregated context string used as LLM input.
        """    
        query=''
        relavent_docs=self.filter_relevant_chunks(lan_docs,doc_type)
        for i in relavent_docs:
            text=i.metadata['original_content']['raw_text']
            table=i.metadata['original_content']['tables_html']
            if text:
                query+=text+"\n"
            if table:
                query+=' '.join(table)+"\n"
        return query
    
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
    def run(self,state) :
        """
        Execute the extraction workflow.

        This method:
        - Selects the correct extraction prompt based on document type.
        - Generates contextual input from raw document data.
        - Invokes the Groq LLM with enforced JSON response format.
        - Parses the structured output.
        - Updates shared pipeline state with extraction results.
        - Tracks token usage.
        - Logs trace information for Responsible AI observability.

        The method automatically retries (up to 3 times) on:
        - OutputParserException
        - ValueError
        - ConnectionError
        - TimeoutError

        Args:
            state (dict): Shared pipeline state containing:
                - 'doc_type' (str): Predicted document type.
                - 'raw_data' (list): List of raw LangChain Document objects.
                - 'agg_json' (dict or str): Aggregated document data.
                - 'token_usage' (list): List to append token usage metadata.
                - Optional 'traces' (list): Existing trace entries.

        Returns:
            dict: Updated state including:
                - 'extraction_json': Parsed extraction output.
                - 'context': Aggregated context string.
                - Updated 'token_usage'.
                - Appended 'traces' entry.
        """
        llm = ChatGroq(model=self.model, api_key=self.api_key,model_kwargs={
            "response_format": {"type": "json_object"}  # 🔥 CRITICAL
        })

        doc_type = state.get('doc_type')
        prompt_text = prompt_map.get(doc_type)
        if not prompt_text:
            raise ValueError(f"No prompt template found for doc_type: {doc_type}")

        # Build PromptTemplate with the actual prompt string
        prompt = PromptTemplate(template=prompt_text, input_variables=['context','agg_json'])

        # Generate query from raw documents
        query = self.query_gen(state.get('raw_data', []),doc_type)

        # Build chain
        parser = JsonOutputParser()
        chain = prompt | llm 

        # Invoke chain
        result_not_parsed = chain.invoke({"context": query,'agg_json':state['agg_json']})  # returns dict
        token_usage=result_not_parsed.usage_metadata
        state['token_usage'].append({
                                    'extractor_agent':token_usage,
                                    'model_name':self.model})
        result=parser.parse(result_not_parsed.content)
        state['extraction_json'] = result
        state['context']=query
        #logging for responsible AI
        trace_entry = log_agent_trace(
            agent_name="ExtractorAgent",
            input_data={
                "doc_type": doc_type,
                "context_preview": query[:500]
            },
            output_data={
                "confidence": result.get("confidence"),
                "top_level_fields": list(result.keys())
            },
            metadata={
                "model": self.model,
                "extracted_field_count": len(result)
            }
        )

        # Append trace to state["traces"] list instead of overwriting
        if "traces" not in state or state["traces"] is None:
            state["traces"] = []
        state["traces"].append(trace_entry)

        return state