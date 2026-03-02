import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from log_trace.logtrace import log_agent_trace
from pydantic import ValidationError
from schemas.validator_schemas import SCHEMA_MAP,NUMERIC_FIELDS_MAP
from typing import List,Dict

class ValidatorAgent:
    """
    Agent responsible for validating and cleaning extracted structured data.

    This agent:
    - Cleans numeric fields in the extracted JSON using regex.
    - Validates the cleaned JSON against a Pydantic schema.
    - Generates a structured validation report indicating validity and errors.
    """
    def __init__(self,api_key,model="openai/gpt-oss-120b"):
        """
        Initialize the ValidatorAgent.

        Args:
            api_key (str): API key for Groq or LLM usage (optional for validation).
            model (str, optional): LLM model name if needed. Defaults to "openai/gpt-oss-120b".
        """
        self.model=model
        #self.temperature=temperature
        self.api_key = api_key
    def clean_numeric_field(self,value: str) -> str:
        """
        Remove all non-digit and non-dot characters from a numeric string.

        Args:
            value (str): Input string to clean.

        Returns:
            str: Cleaned numeric string.
        """

        """Remove all non-digit/non-dot characters from numeric strings"""
        if isinstance(value, str):
            return re.sub(r"[^\d\.]", "", value)
        return value

    def clean_numeric_fields_recursive(self,data, field_path_list):
        """
        Recursively clean numeric fields in nested dict or list structures.

        Args:
            data (dict or list): Nested data structure containing the fields.
            field_path_list (list): List of dot-separated field paths to clean.

        Returns:
            dict or list: Data with specified numeric fields cleaned.
        """
        if isinstance(data, list):
            return [self.clean_numeric_fields_recursive(item, field_path_list) for item in data]

        if not isinstance(data, dict):
            return data

        for field_path in field_path_list:
            parts = field_path.split(".")
            current = data
            for i, part in enumerate(parts):
                if part in current:
                    if i == len(parts) - 1:
                        # last part: clean
                        current[part] = self.clean_numeric_field(current[part])
                    else:
                        # go deeper
                        current[part] = self.clean_numeric_fields_recursive(current[part], [".".join(parts[i+1:])])
        return data
    def run(self,state):
        """
        Validate the extracted JSON against the schema after cleaning numeric fields.

        Steps:
        - Determine schema type based on document type.
        - Clean numeric fields in the extracted JSON recursively.
        - Validate the cleaned JSON using the Pydantic schema.
        - Populate 'validation_report' in the pipeline state with:
            - is_valid (bool)
            - validation_errors (list of structured errors)
            - validated_json (dict if valid, None if invalid)

        Args:
            state (dict): Shared pipeline state containing:
                - 'extraction_json' (dict): Extracted data to validate.
                - 'doc_type' (str): Document type to determine schema.
        
        Returns:
            dict: Updated state with validation results in 'validation_report'.
        """
        schema_type=state.get('doc_type')
        schema_cls = SCHEMA_MAP.get(schema_type.lower())
        if not schema_cls:
            raise ValueError(f"Unsupported schema_type: {schema_type}")
        extracted_json=state['extraction_json']
        numeric_fields = NUMERIC_FIELDS_MAP.get(schema_type.lower(), [])
        cleaned_extracted_json = self.clean_numeric_fields_recursive(extracted_json, numeric_fields)
        print("validating")
        try:
            # Validate JSON against Pydantic schema
            validated_obj = schema_cls.model_validate(cleaned_extracted_json)
            state['validation_report']={
                "is_valid": True,
                "validation_errors": [],
                "validated_json": validated_obj.dict()
            }
            return state
        except ValidationError as e:
            # Convert Pydantic errors into structured list
            errors: List[Dict] = []
            print(e.errors())
            for err in e.errors():
                errors.append({
                    "loc": ".".join([str(loc) for loc in err["loc"]]),
                    "msg": err["msg"],
                    "type": err["type"]
                })
            state['validation_report']= {

                "is_valid": False,
                "validation_errors": errors,
                "validated_json": None
            }
            return state