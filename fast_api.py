from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pipeline import run_pipeline
import pandas as pd
import os
import glob
import time
from typing import List

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="Agentic Document Processor")


# Temporary upload folder
TEMP_FOLDER = "temp_uploads"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Model metrics CSV
MODEL_METRICS_PATH = "model_metrics.csv"

# ----------------------
# Helper functions
# ----------------------
def cleanup_temp_files(max_age_seconds=3600):
    """Delete temporary files older than max_age_seconds."""
    for f in glob.glob(f"{TEMP_FOLDER}/*"):
        if time.time() - os.path.getmtime(f) > max_age_seconds:
            os.remove(f)

# ----------------------
# API Endpoints
# ----------------------
@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    classifier_model: str = Form("llama-3.1-8b-instant"),
    extractor_model: str = Form("openai/gpt-oss-120b"),
    redactor_model: str = Form("llama-3.3-70b-versatile")
):
    """
    Accept a PDF/DOC upload, run the document processing pipeline,
    return extracted JSON, redacted JSON, metrics, and latency info.
    """
    try:

        # Save uploaded file
        file_path = os.path.join(TEMP_FOLDER, file.filename)
        # with open(file_path, "wb") as f:
        #     f.write(await file.read())

        # Model configuration
        model_config = {
            "classification": classifier_model,
            "extractor": extractor_model,
            "redactor": redactor_model
        }

        # Run pipeline
        report = run_pipeline(file_path, model_config=model_config)
        ##cleanup_temp_files()
        return report

    except Exception as e:
        import traceback
        print("Pipeline error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
