# from classifieragent import ClassifierAgent
# from extractoragent import ExtractorAgent
# from validatoragent import ValidatorAgent
# from self_repair_extractor import SelfRepairExtractorAgent
# from redactagent import RedactAgent
# from reporteragent import ReporterAgent
from langgraph.graph import StateGraph,START,END
# from api import Groq_api
from states.state import DocProc
from typing import Literal
from node.nodes import (classifier_node,
                  extractor_node,
                  validator_node,
                  selfrepairextractor_node,
                  redact_node,
                  report_node)


def check_condition(state:DocProc)->Literal['self_repair_extractor','redact_agent']:
    """
    Determine the next node after validation in the workflow.

    Logic:
    - If validation report is valid, proceed to redaction.
    - If maximum self-repair attempts reached, force redaction.
    - Otherwise, route to self-repair extractor for correction.

    Args:
        state (DocProc): Current pipeline state.

    Returns:
        Literal['self_repair_extractor', 'redact_agent']: Next node name.
    """
    MAX_REPAIR=3
    if state['validation_report'].get('is_valid'):
        return 'redact_agent'
     
    if state["repair_attempts"]>=MAX_REPAIR:
        print('MAX repair reached---->forcing Redact')
        return 'redact_agent'
    return 'self_repair_extractor'
def create_workflow():
    """
    Create the document processing workflow as a StateGraph.

    Nodes in the workflow:
    - classifier
    - extractor
    - validator
    - self_repair_extractor
    - redact_agent
    - reporter_agent

    Edges and conditions:
    - Linear flow from classifier → extractor → validator
    - Conditional edge from validator using `check_condition`
    - Loop back from self_repair_extractor to validator
    - Linear flow from redact_agent → reporter_agent → END

    Returns:
        StateGraph: Configured workflow graph.
    """
    graph=StateGraph(DocProc)
    graph.add_node('classifier',classifier_node)
    graph.add_node('extractor',extractor_node)
    graph.add_node('validator',validator_node)
    graph.add_node('self_repair_extractor',selfrepairextractor_node)
    graph.add_node('redact_agent',redact_node)
    graph.add_node('reporter_agent',report_node)

    graph.add_edge(START,'classifier')
    graph.add_edge('classifier','extractor')
    graph.add_edge('extractor','validator')
    #graph.add_edge('validator',END)
    graph.add_conditional_edges('validator',check_condition)

    graph.add_edge('self_repair_extractor','validator')
    graph.add_edge('redact_agent','reporter_agent')
    graph.add_edge('reporter_agent',END)
    return graph





