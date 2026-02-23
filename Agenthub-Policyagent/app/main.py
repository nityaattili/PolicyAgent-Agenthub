import json
import uuid
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

from app.db import init_db, get_conn
from app.agent.graph import GRAPH

app = FastAPI(title="AgentHub Policy Agent")

class RunRequest(BaseModel):
    user_role: str
    question: str

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_agent(req: RunRequest):
    run_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()

    state = {
        "user_role": req.user_role,
        "question": req.question,
        "retrieved_chunks": [],
        "answer": "",
        "citations": [],
        "guardrail_flags": [],
        "status": ""
    }

    out = GRAPH.invoke(state)

    ended_at = datetime.utcnow().isoformat()

    # Store audit log (runs table)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO runs (run_id, user_role, question, answer, citations, guardrail_flags, status)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        req.user_role,
        req.question,
        out.get("answer", ""),
        json.dumps(out.get("citations", [])),
        json.dumps(out.get("guardrail_flags", [])),
        out.get("status", "UNKNOWN")
    ))
    conn.commit()
    conn.close()

    return {
        "run_id": run_id,
        "status": out.get("status"),
        "answer": out.get("answer"),
        "citations": out.get("citations"),
        "guardrail_flags": out.get("guardrail_flags")
    }

@app.get("/audit/runs")
def list_runs(limit: int = 20):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      SELECT run_id, user_role, question, status
      FROM runs
      ORDER BY rowid DESC
      LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"runs": rows}

@app.get("/audit/runs/{run_id}")
def get_run(run_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      SELECT run_id, user_role, question, answer, citations, guardrail_flags, status
      FROM runs
      WHERE run_id=?
    """, (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"error": "not_found"}
    d = dict(row)
    d["citations"] = json.loads(d["citations"] or "[]")
    d["guardrail_flags"] = json.loads(d["guardrail_flags"] or "[]")
    return d

@app.get("/metrics")
def metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM runs")
    total_runs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM runs WHERE status='ANSWERED'")
    answered = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM runs WHERE status='NO_SOURCES'")
    refused = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM runs WHERE guardrail_flags IS NOT NULL AND guardrail_flags != '[]'")
    flagged = cur.fetchone()[0]

    conn.close()

    success_rate = (answered / total_runs * 100) if total_runs > 0 else 0
    refusal_rate = (refused / total_runs * 100) if total_runs > 0 else 0
    guardrail_rate = (flagged / total_runs * 100) if total_runs > 0 else 0

    return {
        "total_runs": total_runs,
        "answered": answered,
        "refused": refused,
        "guardrail_flagged": flagged,
        "success_rate_percent": round(success_rate, 2),
        "refusal_rate_percent": round(refusal_rate, 2),
        "guardrail_trigger_rate_percent": round(guardrail_rate, 2),
    }
