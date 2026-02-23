# 🏦 AgentHub-  Enterprise Policy Agent (Governance-First Agentic AI Demo)

AgentHub is a governance-first internal Policy Q&A agent built to demonstrate how enterprise-ready Agentic AI platforms should be designed.

It prioritizes:
- 🔐 Role-Based Access Control (RBAC)
- 📚 Source-required answers (No hallucinations)
- 🛡 Guardrails (Prompt injection + PII detection)
- 🧾 Audit logging
- 📊 Monitoring & evaluation metrics
- 🔄 Orchestrated agent workflows (LangGraph)

---

## 🎯 Problem

Enterprises need fast, reliable answers to internal policy questions (PTO, procurement, compliance).

Traditional chatbots fail in regulated environments because they:
- Do not enforce document-level access control
- Do not require citations
- Are not auditable
- Cannot expose monitoring metrics

AgentHub solves this with governance-first architecture.

---

## 🏗 Architecture Overview

User (Streamlit UI)  
→ FastAPI Backend  
→ LangGraph Orchestrator  
→ RBAC-Constrained Retriever  
→ Answer Builder (source-required)  
→ Guardrails (injection + PII)  
→ Audit Log (SQLite)  
→ Monitoring Endpoint (/metrics)

---

## 🔐 Security & Governance

### 1️⃣ Role-Based Document Access (RBAC)
Each document defines:
Classification: INTERNAL | CONFIDENTIAL
AllowedRoles: employee, manager, hr, legal


Retrieval is filtered by role before answering.

If access is not permitted → `NO_SOURCES` → safe refusal.

---

### 2️⃣ No-Hallucination Policy
- If no sources are retrieved → the system refuses.
- Every answered response includes citations.
- Post-check enforces citation presence.

---

### 3️⃣ Guardrails
- Prompt injection pattern detection
- PII detection + redaction
- Guardrail flags logged in audit trail

---

### 4️⃣ Audit Logging
Each run stores:
- run_id
- user_role
- question
- answer
- citations
- guardrail flags
- status (ANSWERED / NO_SOURCES / REFUSED)

---

### 5️⃣ Monitoring Dashboard
Exposes `/metrics` endpoint tracking:
- Total runs
- Success rate
- Refusal rate
- Guardrail trigger rate

Displayed in Streamlit under **Metrics & Monitoring**.

---

## 🧠 Tech Stack

- Python 3.12
- FastAPI
- LangGraph
- SQLite
- Streamlit
- Markdown policy ingestion
- Rule-based guardrails (MVP)

---

## 🧪 Example Scenarios

### ✅ Employee asks PTO question
- Retrieves INTERNAL policy
- Returns cited answer
- Status: ANSWERED

### 🚫 Employee asks confidential vendor question
- RBAC blocks retrieval
- Status: NO_SOURCES

### ✅ Manager asks vendor approval question
- Retrieves CONFIDENTIAL document
- Returns cited answer

---

## 🚀 How to Run

### Backend
```bash
uvicorn app.main:app --reload

Frontend 
streamlit run ui/streamlit_app.py
