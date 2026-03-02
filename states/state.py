from typing import TypedDict, List, Literal, Optional, Dict, Any

# -------------------------------
# TypedDict for aggregated document signals
# -------------------------------
class DocumentSignals(TypedDict):
    financial: List[str]
    legal: List[str]
    medical: List[str]
    employment: List[str]
    identity: List[str]
    other: List[str]

class Entities(TypedDict):
    persons: List[str]
    organizations: List[str]
    locations: List[str]

class AggJson(TypedDict):

    section_intent: str
    document_signals: DocumentSignals
    entities: Entities
    dates: List[str]
    identifiers: List[str]
    monetary_values: List[str]
    pii_detected: bool
    contains_signature_section: bool
    contains_table: bool
    risk_level: Literal["low", "medium", "high"]
    confidence: float  # 0.0–1.0
    


class DocProc(TypedDict):
    raw_data: list  # List[Document]
    agg_json: dict  # Your AggJson dict
    file_name:str
    model_config:Dict[str,str]
    doc_type: Optional[str]
    classifier_output: Optional[dict]
    extraction_json: Optional[dict]
    validation_report: Optional[dict]
    context:str
    repair_attempts:int
    redacted_report:Optional[dict]
    token_usage:Optional[List[Dict[str,Any]]]
    trace:Optional[dict]
    redacted_report: Optional[Dict[str, Any]]
    traces: Optional[List[Dict[str, Any]]]  # <- multiple agent traces
    self_repair: Optional[List[Dict[str, Any]]]
    report:Optional[dict]
