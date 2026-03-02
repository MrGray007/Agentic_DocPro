classifier_prompt = """
    You are a document classification AI. You are given structured evidence 
    about a document aggregated from its sections.

    Aggregated Evidence (JSON):
    {aggregated_json}

    Instructions:
    1. Classify this document into one of the following types:
    - invoice
    - contract
    - resume
    - other
    2. Use the signals in the JSON to make your decision.
    3. Do NOT hallucinate. If evidence is insufficient, return "other".
    4. Return structured JSON as follows:

    {{
    "predicted_document_type": "...",
    "confidence": 0.0,
    "reasoning": "brief explanation based on signals"
    }}
    """