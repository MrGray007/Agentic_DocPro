from agents.classifieragent import ClassifierAgent
from agents.extractoragent import ExtractorAgent
from agents.validatoragent import ValidatorAgent
from agents.self_repair_extractor import SelfRepairExtractorAgent
from agents.redactagent import RedactAgent
from agents.reporteragent import ReporterAgent
from states.state import DocProc
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


# classifier_agent=ClassifierAgent(Groq_api.api)
# extractor_agent=ExtractorAgent(Groq_api.api)
# validator_agent=ValidatorAgent(Groq_api.api)
# selfrepairextractor_agent=SelfRepairExtractorAgent(Groq_api.api)
# redact_agent=RedactAgent(Groq_api.api)
# reporter_agent=ReporterAgent()

        # model_config = {
        #     "classification": classifier_model,
        #     "extractor": extractor_model,
        #     "redactor": redactor_model
        # }

def classifier_node(state:DocProc):
    """
    Node for document classification.
    Initializes ClassifierAgent with configured model and runs classification on state.
    """
    agent=ClassifierAgent(model=state.get('model_config',{}).get("classification","openai/gpt-oss-120b"),api_key=api_key)
    return agent.run(state)

def extractor_node(state:DocProc):
    """
    Node for document extraction.
    Initializes ExtractorAgent with configured model and runs extraction on state.
    """
    agent=ExtractorAgent(model=state.get('model_config',{}).get("extractor","openai/gpt-oss-120b"),api_key=api_key)
    return agent.run(state)

def validator_node(state:DocProc):
    """
    Node for document validation.
    Initializes ValidatorAgent and validates the extracted JSON in state.
    """

    agent=ValidatorAgent(api_key)
    return agent.run(state)

def selfrepairextractor_node(state:DocProc):
    """
    Node for self-repair extraction.
    Initializes SelfRepairExtractorAgent and runs self-repair on state.
    """
    agent=SelfRepairExtractorAgent(api_key)
    return agent.run(state)

def redact_node(state:DocProc):
    """
    Node for redaction.
    Initializes RedactAgent with configured model and performs PII redaction on state.
    """
    agent=RedactAgent(model=state.get('model_config',{}).get("redactor","openai/gpt-oss-120b"),api_key=api_key)
    return agent.run(state)

def report_node(state:DocProc):
    """
    Node for reporting.
    Initializes ReporterAgent and generates final report from the state.
    """
    agent=ReporterAgent()
    return agent.run(state)