import streamlit as st
import requests
import json

# -----------------------------
# PAGE SETTINGS
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
        It retrieves relevant passages from a curated knowledge base and generates a structured response
        with references.

        **Safety:** If no supporting evidence is retrieved, the system returns an *Insufficient Evidence* response.
        """
    )

# -----------------------------
# DIFY SETTINGS
# -----------------------------
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

# Read API Key from Streamlit Secrets (Streamlit Cloud -> App settings -> Secrets)
# Add this in Secrets (TOML):
# DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"
try:
    DIFY_API_KEY = st.secrets["app-Vg5HnRRHlmhZUlL7T7ud9ofA"]
except Exception:
    st.error("Missing DIFY_API_KEY in Streamlit Secrets. Add it in App Settings → Secrets.")
    st.stop()

# -----------------------------
# INPUTS
# -----------------------------
st.subheader("Who is this response for?")
role = st.radio(
    "",
    ["Clinician", "Patient"],
    horizontal=True
)

st.subheader("Clinical Question")
query = st.text_area(
    "Enter your question:",
    placeholder="e.g., What defines periodontitis according to AAP 2018?"
)

st.subheader("Optional Findings (JSON)")
findings_json = st.text_area(
    "If you have structured findings, paste them here (optional):",
    placeholder='{"tooth":"30","finding":"bone loss","severity":"moderate"}'
)

# Optional: validate JSON if user typed something
parsed_findings = None
if findings_json.strip():
    try:
        parsed_findings = json.loads(findings_json)
    except json.JSONDecodeError:
        st.warning("Optional Findings is not valid JSON. You can leave it empty or fix the formatting.")

# -----------------------------
# RUN BUTTON
# -----------------------------
if st.button("Run Dental Disease Assistant"):
    if not query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving guideline-based evidence..."):
            headers = {
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            }

            # ✅ Correct Dify Chat API payload:
            payload = {
                "inputs": {
                    # These must match your Dify Start-node variables:
                    "role": role,
                    "findings_json": findings_json  # keep as string; Dify will receive it as provided
                },
                "query": query,
                "response_mode": "blocking",
                "user": "streamlit-user"
            }

            try:
                response = requests.post(
                    DIFY_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code != 200:
                    st.error(f"Dify API error {response.status_code}")
                    st.code(response.text)
                else:
                    data = response.json()
                    answer = data.get("answer", "")

                    st.subheader("Assistant Response")
                    if answer:
                        st.markdown(answer)
                    else:
                        st.warning("No 'answer' field returned. Showing full JSON response:")
                        st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# -----------------------------
# SAFETY DISCLAIMER
# -----------------------------
st.divider()
st.warning(
    "⚠️ **Clinical Disclaimer**\n\n"
    "This tool is for educational decision support only. "
    "It does NOT diagnose, prescribe, or replace the judgment of a licensed dental professional."
)
