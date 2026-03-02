table_prompt=""" From tables, detect:
                - column headers
                - key-value pairs
                - totals or balances
                - itemized rows
                - structured forms
                        """
image_prompt=""" From images, detect:
                - logos or brand identifiers
                - government insignia
                - signatures (digital or handwritten)
                - stamps or seals
                - ID cards or licenses
                - medical imagery
                - financial tables
                - forms or checkboxes
                """
text_prompt="""
            ##The document may belong to ANY domain.
            Do not assume document type.
            Extract signals objectively.###

            You are analyzing ONE section of a document.

            Your task is NOT to write a human-friendly summary.
            Your task is to extract structured signals that help:

            - document classification
            - downstream structured extraction
            - PII detection
            - compliance validation

            CRITICAL RULES:
            - Do NOT remove or modify numbers.
            - Preserve IDs, reference numbers, dates, and monetary values EXACTLY.
            - Do NOT infer missing values.
            - If uncertain, return null.
            - Output ONLY valid JSON.

            --------------------------------------------------
            SECTION TEXT:
            {}
            --------------------------------------------------
"""

output_structure_prompt="""
                Return JSON in this exact structure:

                {
                "section_intent": "brief purpose of this section",
                "document_signals": {
                    "financial": ["terms, amounts, balances"],
                    "legal": ["clauses, agreements, obligations"],
                    "medical": ["diagnosis, prescription, patient info"],
                    "employment": ["job title, salary, employer"],
                    "identity": ["ID number, passport, license"],
                    "correspondence": ["sender, recipient, subject"],
                    "reporting": ["findings, metrics, analysis"],
                    "compliance": ["regulatory rules, policy references, audits"],
                    "technical": ["specifications, logs, technical measurements"]
                    "logistics": ["shipping info, tracking, inventory, supply chain"]
                    "other": ["anything not captured above"]

                },
                "entities": {
                    "persons": ["names"],
                    "organizations": ["company names"],
                    "locations": ["addresses or cities"]
                },
                "dates": ["YYYY-MM-DD or raw"],
                "identifiers": ["invoice numbers, contract IDs, reference numbers"],
                "monetary_values": ["exact amounts with currency"],
                "pii_detected": true if personal or sensitive info present,
                "contains_signature_section": true if signatures/stamps present,
                "contains_table": true if any table exists,
                "risk_level":"low", "medium", "high" based on sensitive info,
                "confidence": 0.0–1.0 reflecting certainty
        }

        ###If the provided section has no meaningful text, tables, or images,
        return JSON with "section_intent": "empty_section" 
        and empty lists for signals. Do NOT fail.###


        """