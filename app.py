import streamlit as st
import requests
import json

# -----------------------------
# 1) PAGE SETTINGS (looks professional)
# -----------------------------
st.set_page_config(
    page_title="Dental Disease Assistant (DDA)",
    layout="centered"
)

st.title("🦷 Dental Disease Assistant (DDA)")
st.caption(
    "A retrieval-augmented clinical decision support prototype grounded in AAP, AAE, and ADA guidelines."
)

with st.expander("ℹ️ About this prototype"):
    st.markdown(
        """
        **Dental Disease Assistant (DDA)** is a Retrieval-Augmented Generation (RAG) system.
        It retrieves relevant passages from a curated knowledge base (AAP/AAE/ADA) and then generates
        a structured response with references.

        **Safety:** If no supporting evidence is retrieved, the system returns an *Insufficient Evidence* response.
        """
    )

# -----------------------------
# 2) PUT YOUR DIFY SETTINGS HERE
# -----------------------------
# ✅ Replace these with your real values (or keep your existing ones from old app.py)
DIFY_URL = "https://api.dify.ai/v1/chat-messages"
DIFY_API_KEY = "app-zGyqZOv41RDBmUcbRB1tsf9n"

# -----------------------------
# 3) USER INPUTS
# -----------------------------
st.subheader("Select Audience")
role = st.radio(
    "Who is this response for?",
    ["Clinician", "Patient"],
    horizontal=True
)

st.subheader("Clinical Question")
query = st.text_area(
    "Enter your question:",
    placeholder="e.g., What does bleeding during brushing usually indicate?"
)

st.subheader("Optional Findings (JSON)")
findings_json = st.text_area(
    "If you have structured findings, paste them here (optional):",
    placeholder='{"tooth": "30", "finding": "bone loss", "severity": "moderate"}'
)

# -----------------------------
# 4) RUN BUTTON
# -----------------------------
if st.button("Run Dental Disease Assistant"):
    if not query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving guideline-based evidence..."):
            payload = {
                "inputs": {
                    "query": query,
                    "role": role,
                    "findings_json": findings_json
                }
            }

            headers = {
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    DIFY_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                st.subheader("Assistant Response")

                # -----------------------------
                # 5) PRETTY OUTPUT (not raw JSON)
                # -----------------------------
                try:
                    data = response.json()
                    answer = data.get("answer") or data.get("output") or response.text
                    st.markdown(answer)
                except json.JSONDecodeError:
                    st.markdown(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# -----------------------------
# 6) SAFETY DISCLAIMER
# -----------------------------
st.divider()
st.warning(
    "⚠️ **Clinical Disclaimer**\n\n"
    "This tool is for educational decision support only. "
    "It does NOT diagnose, prescribe, or replace the judgment of a licensed dental professional."
)
