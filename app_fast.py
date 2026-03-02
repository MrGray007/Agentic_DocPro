# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json

# ----------------------
# Config
# ----------------------
API_URL = "http://localhost:8000"  # FastAPI backend URL
MODEL_OPTIONS = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]
st.title("Agentic DocPro")
st.header(" Agentic Document Processor (FastAPI Backend)")

# Load model metrics
model_val = pd.read_csv(r'model_metrics.csv')
model_val = model_val.set_index('model_name')

# ----------------------
# File uploader
# ----------------------
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "doc", "docx"])

if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")

    # Model selection
    st.subheader("Model Selection")
    classifier_model = st.selectbox("Classifier Model", MODEL_OPTIONS, index=2)
    extractor_model = st.selectbox("Extractor Model", MODEL_OPTIONS, index=1)
    redactor_model = st.selectbox("Redactor Model", MODEL_OPTIONS, index=0)

    if st.button("Process Document"):
        # Save file temporarily
        temp_file_path = uploaded_file.name
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Send file + model config to FastAPI
        with open(temp_file_path, "rb") as f:
            files = {"file": (uploaded_file.name, f, uploaded_file.type)}
            data = {
                "classifier_model": classifier_model,
                "extractor_model": extractor_model,
                "redactor_model": redactor_model
            }
            try:
                response = requests.post(f"{API_URL}/process", files=files, data=data)
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"Error processing document: {e}")
                result = {}

        # ----------------------
        # Display outputs
        # ----------------------
        st.subheader("Extracted JSON")
        st.json(result.get("extracted_json", {}))

        st.subheader("Redacted JSON")
        st.json(result.get("redacted_json", {}))

        st.subheader("Redacted metrics")
        st.json(result.get("redaction", {}).get("pii_metrics", {}))

        st.subheader("Token usage")
        st.json(result.get("token_usage", []))

        st.subheader("Self Repair")
        st.json(result.get("self_repair", {}))

        st.subheader("Agent Traces")
        st.json(result.get("agent_traces", []))

        st.subheader("Latency")
        st.metric("Processing Time (seconds)", result.get("latency_seconds", "N/A"))

        st.subheader("Latency Breakdown")
        st.json(result.get("step_timings", {}))

        # ----------------------
        # Model valuation & plots
        # ----------------------
        if not model_val.empty:
            st.subheader("Model Valuation")
            st.dataframe(model_val)

            st.subheader("Model Performance Comparison")
            fig, ax = plt.subplots(figsize=(15, 10))
            model_val.plot(kind="bar", ax=ax)
            ax.set_xlabel("Model")
            ax.set_ylabel("Score (%)")
            ax.set_title("Extraction & PII Performance by Model")
            ax.set_ylim(0, 110)
            ax.legend(title="Metrics")
            st.pyplot(fig)

            st.subheader("Model Performance Breakdown")
            for metric in model_val.columns:
                st.write(f"### {metric}")
                st.bar_chart(model_val[metric])

            # Quick insights
            st.subheader("🏆 Quick Insights From Model Evaluation")
            best_extraction = model_val["Extraction_accuracy"].idxmax()
            best_precision = model_val["PII_precision"].idxmax()
            best_recall = model_val["PII_recall"].idxmax()
            best_f1 = model_val["PII_F1"].idxmax()

            st.markdown(f"""
            🥇 **Best Extraction Accuracy** → **{best_extraction}** ({model_val['Extraction_accuracy'].max():.2f}%)
            🥇 **Best PII Precision** → **{best_precision}** ({model_val['PII_precision'].max():.2f}%)
            🥇 **Best PII Recall** → **{best_recall}** ({model_val['PII_recall'].max():.2f}%)
            🥇 **Best F1 Overall** → **{best_f1}** ({model_val['PII_F1'].max():.2f}%)
            """)