import streamlit as st
import requests
import json

# =========================================
# 1) PAGE SETTINGS / HEADER
# =========================================
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

        It retrieves relevant passages from a curated knowledge base (AAP/AAE/ADA + internal mapping sheets)
        and generates a structured response with references.

        **Safety behavior:** If no supporting evidence is retrieved from the knowledge base,
        the assistant returns an *Insufficient Evidence* response (no guessing).
        """
    )

with st.expander("✅ Example prompts (copy/paste)"):
    st.markdown(
        """
        **Clinician example**
        - “Tooth #30 has ~40% radiographic bone loss, Class II furcation, PD 6 mm, CAL 7 mm.  
          Provide likely Stage/Grade and confirmatory steps.”

        **Patient example**
        - “My gums bleed when I brush. What could that mean and what should I ask my dentist?”
        """
    )

# =========================================
# 2) DIFY CONFIG (SAFE: key comes from Secrets)
# =========================================
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

# Streamlit Cloud -> App Settings -> Secrets (TOML):
# DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"
if "DIFY_API_KEY" not in st.secrets:
    st.error(
        "Missing DIFY_API_KEY in Streamlit Secrets.\n\n"
        "Fix:\n"
        "1) Go to App Settings → Secrets\n"
        '2) Paste exactly this (TOML):  DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"\n'
        "3) Save and Reboot the app\n"
    )
    st.stop()

DIFY_API_KEY = str(st.secrets["DIFY_API_KEY"]).strip()

# Basic validation (does not print the key)
if not DIFY_API_KEY.startswith("app-") or len(DIFY_API_KEY) < 10:
    st.error(
        "DIFY_API_KEY is present but appears invalid.\n\n"
        'It must look like:  DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"\n'
        "Do NOT use app-app-... (double prefix).\n"
    )
    st.stop()

# =========================================
# 3) INPUTS
# =========================================
st.subheader("Who is this response for?")
role = st.radio(
    label="",
    options=["Clinician", "Patient"],
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

# Validate JSON (optional — warning only)
if findings_json.strip():
    try:
        json.loads(findings_json)
        st.caption("✅ JSON looks valid.")
    except json.JSONDecodeError:
        st.warning("⚠️ Optional Findings is not valid JSON. You can leave it empty or fix formatting.")

# =========================================
# 4) RUN BUTTON (CALL DIFY)
# =========================================
if st.button("Run Dental Disease Assistant"):
    if not query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("R
