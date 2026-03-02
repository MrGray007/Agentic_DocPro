
from langchain_core.prompts import PromptTemplate
RESUME_SELFREPAIR=PromptTemplate(template='''You are a Self-Repair AI for Resumes.

You received the following extracted JSON from a resume:
{extracted_json}

Validator errors:
{validation_errors}

Here is the FULL resume text:
{context}

CRITICAL RULES:
1. Correct only the invalid or missing fields listed in "validation_errors" using the text above.
2. Preserve all valid extracted fields exactly.
3. Do NOT invent skills, experience, education, or projects that are not explicitly present.
4. Preserve dates exactly as written.
5. Return ONLY valid JSON in the original schema.
6. Confidence must be a number between 0.0 and 1.0.

Schema:
{{
  "candidate": {{
    "full_name": null,
    "email": null,
    "phone": null,
    "location": null,
    "linkedin": null,
    "portfolio": null
  }},
  "summary": null,
  "education": [
    {{
      "degree": null,
      "field_of_study": null,
      "institution": null,
      "location": null,
      "start_date": null,
      "end_date": null
    }}
  ],
  "experience": [
    {{
      "job_title": null,
      "company": null,
      "location": null,
      "start_date": null,
      "end_date": null,
      "responsibilities": []
    }}
  ],
  "skills": {{
    "technical": [],
    "soft": [],
    "tools": []
  }},
  "certifications": [
    {{
      "name": null,
      "issuer": null,
      "date": null
    }}
  ],
  "projects": [
    {{
      "name": null,
      "description": null,
      "technologies": []
    }}
  ],
  "languages": [],
  "confidence": 0.0
}}

Return corrected JSON only.
''',input_variable=["extracted_json","validation_errors","context"])


INVOICE_SELFREPAIR=PromptTemplate(template='''You are a Self-Repair AI for Invoices.

You received the following extracted JSON from an invoice:
{extracted_json}

Validator errors:
{validation_errors}

Here is the FULL invoice text:
{context}

CRITICAL RULES:
1. Correct only the invalid or missing fields listed in "validation_errors" using the text above.
2. Preserve all valid extracted fields exactly.
3. Preserve invoice numbers, monetary values, and dates exactly as written.
4. Do NOT calculate totals or infer missing fields not explicitly shown.
5. Return ONLY valid JSON in the original schema.
6. Confidence must be a number between 0.0 and 1.0.

Schema:
{{
  "invoice_details": {{
    "invoice_number": null,
    "invoice_date": null,
    "due_date": null,
    "purchase_order_number": null,
    "currency": null
  }},
  "vendor": {{
    "name": null,
    "address": null,
    "phone": null,
    "email": null,
    "tax_id": null
  }},
  "bill_to": {{
    "name": null,
    "address": null,
    "phone": null,
    "email": null
  }},
  "line_items": [
    {{
      "description": null,
      "quantity": null,
      "unit_price": null,
      "total": null
    }}
  ],
  "amounts": {{
    "subtotal": null,
    "tax": null,
    "discount": null,
    "shipping": null,
    "total_amount": null,
    "amount_due": null
  }},
  "payment_details": {{
    "bank_name": null,
    "account_number": null,
    "iban": null,
    "swift": null,
    "payment_terms": null
  }},
  "contains_signature": true,
  "confidence": 0.0
}}

Return corrected JSON only.
''',input_variables=["extracted_json","validation_errors",'context'])
MEDIACAL_SELFREPAIR=PromptTemplate(template='''You are a Self-Repair AI for Medical Records.

You received the following extracted JSON from a medical record:
{extracted_json}

Validator errors:
{validation_errors}

Here is the FULL medical record text:
{context}

CRITICAL RULES:
1. Correct only invalid or missing fields using the text above.
2. Preserve all valid extracted fields exactly.
3. Preserve patient identifiers and dates exactly as written.
4. Do NOT invent diagnoses, medications, lab results, or procedures that are not explicitly present.
5. Return ONLY valid JSON in the original schema.
6. Confidence must be a number between 0.0 and 1.0.

Schema:
{{
  "patient": {{
    "full_name": null,
    "date_of_birth": null,
    "gender": null,
    "address": null,
    "phone": null,
    "email": null,
    "patient_id": null
  }},
  "medical_summary": null,
  "diagnoses": [
    {{
      "condition": null,
      "diagnosis_date": null,
      "severity": null
    }}
  ],
  "medications": [
    {{
      "name": null,
      "dosage": null,
      "frequency": null,
      "start_date": null,
      "end_date": null
    }}
  ],
  "allergies": [
    {{
      "allergen": null,
      "reaction": null,
      "severity": null
    }}
  ],
  "lab_results": [
    {{
      "test_name": null,
      "result": null,
      "unit": null,
      "reference_range": null,
      "date": null
    }}
  ],
  "procedures": [
    {{
      "procedure_name": null,
      "procedure_date": null,
      "outcome": null
    }}
  ],
  "physician": {{
    "name": null,
    "department": null,
    "contact": null
  }},
  "hospital": {{
    "name": null,
    "address": null,
    "phone": null
  }},
  "confidence": 0.0
}}

Return corrected JSON only.
''',input_variable=["extracted_json","validation_errors",'context'])
CONTRACT_SELFREPAIR=PromptTemplate(template='''You are a Self-Repair AI for Contracts.

You received the following extracted JSON from a contract:
{extracted_json}

Validator errors:
{validation_errors}

Here is the FULL contract text:
{context}

CRITICAL RULES:
1. Correct only invalid or missing fields using the text above.
2. Preserve all valid extracted fields exactly.
3. Preserve contract numbers, party names, and dates exactly as written.
4. Do NOT invent obligations, clauses, or signatures not explicitly present.
5. Return ONLY valid JSON in the original schema.
6. Confidence must be a number between 0.0 and 1.0.

Schema:
{{
  "contract_details": {{
    "contract_number": null,
    "title": null,
    "start_date": null,
    "end_date": null,
    "renewal_terms": null,
    "governing_law": null
  }},
  "parties": [
    {{
      "role": null,
      "name": null,
      "address": null,
      "contact_person": null,
      "phone": null,
      "email": null
    }}
  ],
  "payment_terms": {{
    "currency": null,
    "amount": null,
    "due_date": null,
    "payment_schedule": null
  }},
  "obligations": [
    {{
      "party": null,
      "description": null
    }}
  ],
  "termination_clauses": [
    {{
      "clause": null,
      "description": null
    }}
  ],
  "confidentiality_clauses": [
    {{
      "clause": null,
      "description": null
    }}
  ],
  "signatures": [
    {{
      "party": null,
      "name": null,
      "title": null,
      "date_signed": null
    }}
  ],
  "contains_signature": true,
  "confidence": 0.0
}}

Return corrected JSON only.
''',input_variable=["extracted_json","validation_errors",'context'])

selfrepair_prompts={
    'resume':RESUME_SELFREPAIR,
    'invoice':INVOICE_SELFREPAIR,
    'contract':CONTRACT_SELFREPAIR
}