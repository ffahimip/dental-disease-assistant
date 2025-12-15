import streamlit as st
import requests
import json

# =====================================================
# 1) PAGE SETTINGS
# =====================================================
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

        It retrieves relevant passages from authoritative dental guidelines (AAP, AAE, ADA)
        and generates structured, evidence-linked responses.

        **Safety behavior:**  
        If no relevant evidence is found in the knowledge base, the assistant explicitly
        returns an *Insufficient Evidence* response instead of guessing.
        """
    )

# =====================================================
# 2) DIFY CONFIGURATION (SAFE — FROM STREAMLIT SECRETS)
# =====================================================
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

if "DIFY_API_KEY" not in st.secrets:
    st.error(
        "Missing DIFY_API_KEY in Streamlit Secrets.\n\n"
        "Go to App Settings → Secrets and add:\n\n"
        'DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"\n\n'
        "Then Save and Reboot the app."
    )
    st.stop()

DIFY_API_KEY = str(st.secrets["DIFY_API_KEY"]).strip()

# Basic validation (no printing of key)
if not DIFY_API_KEY.startswith("app-"):
    st.error(
        "Invalid DIFY_API_KEY format.\n\n"
        'It must look like:  DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"\n'
        "Do NOT add 'app-' twice."
    )
    st.stop()

# =====================================================
# 3) USER INPUTS
# =====================================================
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

# Optional JSON validation (warning only)
if findings_json.strip():
    try:
        json.loads(findings_json)
        st.caption("✅ Optional findings JSON looks valid.")
    except json.JSONDecodeError:
        st.warning("⚠️ Optional findings is not valid JSON. You may leave it empty or fix formatting.")

# =====================================================
# 4) RUN BUTTON — CALL DIFY
# =====================================================
if st.button("Run Dental Disease Assistant"):
    if not query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving guideline-based evidence..."):
            headers = {
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            }

            # IMPORTANT:
            # - query must be TOP-LEVEL
            # - inputs must match Dify Start-node variable names
            payload = {
                "inputs": {
                    "role": role,
                    "findings_json": findings_json
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

                st.subheader("Assistant Response")

                if response.status_code != 200:
                    st.error(f"Dify API error {response.status_code}")
                    st.code(response.text)
                else:
                    data = response.json()
                    answer = data.get("answer", "")

                    if answer:
                        st.markdown(answer)
                    else:
                        st.warning("No 'answer' field returned. Full response shown below:")
                        st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# =====================================================
# 5) SAFETY DISCLAIMER
# =====================================================
st.divider()
st.warning(
    "⚠️ **Clinical Disclaimer**\n\n"
    "This tool is for educational decision support only. "
    "It does NOT diagnose, prescribe, or replace the judgment of a licensed dental professional."
)
