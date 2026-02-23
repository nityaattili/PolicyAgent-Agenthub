# PRD — AgentHub Policy Agent (Mini Enterprise Agent Platform Demo)

## 1. Summary
AgentHub Policy Agent is an internal Policy Q&A assistant designed for regulated enterprise environments. It answers employee questions using an approved policy knowledge base with role-based access control (RBAC), mandatory citations, guardrails, and audit logging.

## 2. Problem Statement
Employees and managers frequently need fast, reliable answers to internal policy questions (PTO, procurement, compliance). Traditional search is slow, policies are scattered, and incorrect answers create compliance risk.

## 3. Goals
- Provide fast policy answers grounded in approved sources (RAG).
- Enforce RBAC: users only retrieve policy content they are authorized to access.
- Require citations for every answer (no hallucination mode).
- Provide auditability: log each run, citations, and guardrail flags.
- Provide monitoring: success/refusal/guardrail rates.

## 4. Non-Goals (MVP)
- Not a general chatbot.
- No external web browsing.
- No automated policy updates from enterprise systems (e.g., SharePoint) yet.
- No fine-grained identity integration (SSO/Okta) in MVP (role is selected in UI).

## 5. Users & Personas
- Employee: asks PTO/benefits/how-to questions.
- Manager: asks approval/procurement questions; higher access tier.
- HR/Legal: maintains policy docs; needs audit visibility.

## 6. User Stories
- As an employee, I can ask about PTO carryover and receive a cited answer.
- As an employee, if I ask a restricted question, the agent refuses safely without leaking content.
- As a manager, I can access confidential procurement policy and receive a cited answer.
- As HR/Legal, I can review audit logs for runs and guardrail triggers.

## 7. Key Requirements
### Functional
- Document ingestion from markdown policy files.
- Chunking + retrieval constrained by AllowedRoles.
- Orchestrated workflow (validate → retrieve → answer → post-check).
- Source-required behavior: no sources → refuse.
- Guardrails: prompt injection heuristics, PII detection/redaction.
- Audit logging: runs captured with status, citations, flags.
- Monitoring endpoint + dashboard.

### Non-Functional
- Reliability: deterministic behavior (no hallucinated policy).
- Security: doc-level access control enforced at retrieval time.
- Auditability: every run is traceable via run_id.

## 8. Success Metrics (MVP)
- Success rate (% ANSWERED)
- Refusal rate (% NO_SOURCES)
- Guardrail trigger rate (% with flags)
- Citation coverage (% ANSWERED with citations = 100% target)

## 9. Risks & Mitigations
- Prompt injection attempts → detect patterns + do not treat retrieved text as instructions.
- Unauthorized data exposure → RBAC filtering before retrieval.
- Hallucinations → “sources required” policy; refuse without sources.
- PII leakage → redaction + flagging.

## 10. MVP Scope
- 2–10 policy docs
- 4 roles (employee/manager/hr/legal)
- Streamlit UI (ask + audit + monitoring)
- FastAPI backend + SQLite logs
- LangGraph orchestration

## 11. Roadmap (Next Iterations)
- Add agent registry/versioning (multiple agents, publish/discover).
- Replace simple retrieval with embeddings + vector DB.
- Add SSO + real identity (Okta/Azure AD).
- Add evaluation suite (golden Q&A set + automated regression).
- Add latency metrics + tool-call tracing.
- Add connectors (SharePoint/Confluence/Jira) with permission mapping.
