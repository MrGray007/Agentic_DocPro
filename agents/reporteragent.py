from datetime import datetime

class ReporterAgent:
    def run(self,state):
        """
        Aggregates all agent traces, extraction, validation, and redaction
        into a single structured report.
        """
        report = {}
        report['file_name']=state.get('file_name')

        report['classified_output']=state.get('classifier_output')

        # ------------------------
        # Document Summary
        # ------------------------
        report["doc_type"] = state.get("doc_type")
        report["extraction_confidence"] = state.get("extraction_json", {}).get("confidence")
        #report["invoice_number"] = state.get("extraction_json", {}).get("invoice_details", {}).get("invoice_number")

        # ------------------------
        # Validation Summary
        # ------------------------
        validation_report = state.get("validation_report", {})
        report["validation"] = {
            "is_valid": validation_report.get("is_valid", False),
            "errors": validation_report.get("validation_errors", [])
        }

        # ------------------------
        # Redaction Summary
        # ------------------------
        redaction_report = state.get("redacted_report", {})
        report["redaction"] = {
            "pii_metrics": redaction_report.get("pii_metrics"),
            "pii_tag_counts": redaction_report.get("pii_tag_counts"),
            "total_masks": redaction_report.get("total_masks")
        }

        # ------------------------
        # Repair / Self-Repair Summary
        # ------------------------
        if 'repair_attempts' in state:
            report["self_repair"] = {
                "attempts": state["repair_attempts"],
                "last_trace": state.get("self_repair")
            }

        # ------------------------
        # Agent Traces
        # ------------------------
        report["agent_traces"] = state.get("traces", [])

        # ------------------------
        # Optional: Full extraction and redacted JSON for reference
        # ------------------------
        report["extracted_json"] = state.get("extraction_json")
        report["redacted_json"] = redaction_report.get("redacted_json")

        report['token_usage']=state.get('token_usage',[])

        # ------------------------
        # Add timestamp
        # ------------------------
        import datetime
        report["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

        # Store in state for later reference or export
        state["report"] = report

        print(f"ReporterAgent generated report for doc_type: {state.get('doc_type')}")
        return state
