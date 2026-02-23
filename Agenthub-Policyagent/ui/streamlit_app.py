import json
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="AgentHub Policy Agent", layout="wide")
st.title("AgentHub – Internal Policy Q&A Agent")

tab1, tab2, tab3, tab4 = st.tabs(["Ask Policy Agent", "Audit Viewer", "Health", "Metrics & Monitoring"])

with tab1:
    st.subheader("Ask a policy question (RAG + citations + guardrails)")

    col1, col2 = st.columns([1, 2])

    with col1:
        user_role = st.selectbox("Your role", ["employee", "manager", "hr", "legal"])
        st.caption("RBAC is enforced at retrieval time based on AllowedRoles in docs.")

    with col2:
        question = st.text_input("Question", placeholder="e.g., What is the PTO carryover policy?")

    if st.button("Run Agent", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            payload = {"user_role": user_role, "question": question}
            resp = requests.post(f"{API_BASE}/run", json=payload, timeout=60)
            if resp.status_code != 200:
                st.error(f"Backend error: {resp.status_code} {resp.text}")
            else:
                data = resp.json()
                st.success(f"Status: {data.get('status')}  |  Run ID: {data.get('run_id')}")

                st.markdown("### Answer")
                st.write(data.get("answer", ""))

                flags = data.get("guardrail_flags", [])
                if flags:
                    st.markdown("### Guardrail Flags")
                    st.write(flags)

                citations = data.get("citations", [])
                st.markdown("### Citations")
                if not citations:
                    st.info("No citations returned.")
                else:
                    st.json(citations)

with tab2:
    st.subheader("Audit Viewer (runs + governance visibility)")
    limit = st.slider("Number of runs", min_value=5, max_value=50, value=20, step=5)

    if st.button("Refresh Runs"):
        resp = requests.get(f"{API_BASE}/audit/runs", params={"limit": limit}, timeout=30)
        if resp.status_code != 200:
            st.error(f"Backend error: {resp.status_code} {resp.text}")
        else:
            runs = resp.json().get("runs", [])
            st.write(runs)

    st.markdown("### View Run Details")
    run_id = st.text_input("Enter Run ID")
    if st.button("Fetch Run"):
        if not run_id.strip():
            st.warning("Enter a Run ID.")
        else:
            resp = requests.get(f"{API_BASE}/audit/runs/{run_id}", timeout=30)
            if resp.status_code != 200:
                st.error(f"Backend error: {resp.status_code} {resp.text}")
            else:
                st.json(resp.json())

with tab3:
    st.subheader("Health Check")
    if st.button("Ping backend"):
        resp = requests.get(f"{API_BASE}/health", timeout=10)
        st.write(resp.json())

with tab4:
    st.subheader("Enterprise Monitoring Dashboard")

    if st.button("Load Metrics"):
        resp = requests.get(f"{API_BASE}/metrics", timeout=10)
        if resp.status_code != 200:
            st.error(f"Failed to fetch metrics: {resp.status_code}")
        else:
            data = resp.json()

            colA, colB, colC, colD = st.columns(4)
            colA.metric("Total Runs", data["total_runs"])
            colB.metric("Answered", data["answered"])
            colC.metric("Refused", data["refused"])
            colD.metric("Guardrail Triggered", data["guardrail_flagged"])

            st.divider()

            col1, col2, col3 = st.columns(3)
            col1.metric("Success Rate (%)", data["success_rate_percent"])
            col2.metric("Refusal Rate (%)", data["refusal_rate_percent"])
            col3.metric("Guardrail Trigger Rate (%)", data["guardrail_trigger_rate_percent"])
