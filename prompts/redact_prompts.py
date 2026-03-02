MASK_TAGS = [
    "[NAME]", "[EMAIL]", "[PHONE]", "[ADDRESS]",
    "[ID]", "[BANK]", "[DOB]", "[CARD]", "[SIGNATURE]"
]
PII_FIELD_MAP = {

    "resume": {
        "candidate.full_name": "[NAME]",
        "candidate.email": "[EMAIL]",
        "candidate.phone": "[PHONE]",
        "candidate.location": "[ADDRESS]",
        "candidate.linkedin": "[ID]",
        "candidate.portfolio": "[ID]",
    },

    "invoice": {
        "vendor.name": "[NAME]",
        "vendor.address": "[ADDRESS]",
        "vendor.phone": "[PHONE]",
        "vendor.email": "[EMAIL]",
        "vendor.tax_id": "[ID]",

        "bill_to.name": "[NAME]",
        "bill_to.address": "[ADDRESS]",
        "bill_to.phone": "[PHONE]",
        "bill_to.email": "[EMAIL]",

        "payment_details.bank_name": "[BANK]",
        "payment_details.account_number": "[ID]",
        "payment_details.iban": "[BANK]",
        "payment_details.swift": "[BANK]",
    },

    "medical": {
        "patient.full_name": "[NAME]",
        "patient.date_of_birth": "[DOB]",
        "patient.address": "[ADDRESS]",
        "patient.phone": "[PHONE]",
        "patient.email": "[EMAIL]",
        "patient.patient_id": "[ID]",
        "physician.name": "[NAME]",
    },

    "contract": {
        "parties.name": "[NAME]",
        "parties.address": "[ADDRESS]",
        "parties.phone": "[PHONE]",
        "parties.email": "[EMAIL]",
        "signatures.name": "[NAME]"
    }
}


REDACTION_PROMPT = """
You are a strict PII Redaction Engine.

The input is a structured JSON document.

Your job:
1. Inspect EVERY field value in the JSON.
2. If a field contains personally identifiable information (PII),
   replace ONLY the VALUE with the correct tag.
3. Keep the JSON structure identical.
4. Do NOT remove keys.
5. Do NOT change numeric non-PII fields.
6. Do NOT add or remove fields.
7. Do NOT summarize.
8. Return VALID JSON only.

Mask using EXACT tags:

[NAME] → names 
[EMAIL] → email addresses
[PHONE] → phone numbers
[ADDRESS] → physical addresses, city/state info
[ID] → tax IDs, account numbers, patient IDs, invoice IDs, passport, etc, Links like github and linkdein.
[BANK] → bank names, IBAN, SWIFT
[DOB] → dates of birth
[CARD] → credit/debit card numbers
[SIGNATURE] → signatures or signed names

Important:
- If the original value is already null, keep it null.
- Do NOT mask non-sensitive business names unless clearly personal.
- Do NOT modify numeric financial amounts.
- Preserve formatting and return STRICT JSON.

JSON INPUT:
{document_text}
"""