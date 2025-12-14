import json
import requests
import streamlit as st

st.set_page_config(page_title="Dental Disease Assistant", layout="centered")

st.title("Dental Disease Assistant (Prototype)")

st.markdown("""
This interface sends your question plus optional clinical findings to the Dify RAG agent.

**Grounding sources only:**
- AAP 2018 (Periodontology)
- AAE 2013 (Endodontics)
- ADA 2024 (Caries & Restorative)
- Patient education materials

⚠️ This tool is educational and does **not** diagnose or prescribe.
""")

audience = st.radio(
    "Audience",
    ["clinician", "patient"],
    index=0,
    horizontal=True
)

findings_json = st.text_area(
    "Optional findings_json (paste AI or chart data: bone_loss_pct, CAL_mm, furcation_class, mobility, etc.)",
    height=150,
    placeholder='[{"tooth":"30","bone_loss_pct":40,"furcation_class":"II","mobility":"Class I","diabetes":true}]'
)

query = st.text_input(
    "Your question to the assistant",
    placeholder="Example: Map this bone loss to Stage/Grade and explain why."
)

# --- Secrets (Streamlit Cloud) ---
DIFY_URL = st.secrets.get("DIFY_URL", "")
DIFY_API_KEY = st.secrets.get("DIFY_API_KEY", "")

if st.button("Ask"):
    if not DIFY_URL or not DIFY_API_KEY:
        st.error("Missing DIFY_URL or DIFY_API_KEY in Streamlit Secrets.")
    elif not query.strip():
        st.error("Please enter a question.")
    else:
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": {
                "audience": audience,
                "findings_json": findings_json
            },
            "query": query,
            "response_mode": "blocking"
        }

        try:
            r = requests.post(DIFY_URL, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()

            st.subheader("Assistant Response")
            st.write(data.get("answer", data))

        except Exception as e:
            st.error(f"Error contacting backend: {e}")
else:
    st.info("Add DIFY_URL and DIFY_API_KEY in Streamlit Cloud Secrets to go live.")
