import json
import math
from typing import List, Dict, Any

from app.db import get_conn


def _tokenize(text: str) -> List[str]:
    # simple tokenizer for MVP
    return [t.lower() for t in text.replace("\n", " ").split() if t.strip()]


def _tf(tokens: List[str]) -> Dict[str, float]:
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0.0) + 1.0
    # normalize
    n = max(1.0, float(len(tokens)))
    for k in tf:
        tf[k] /= n
    return tf


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    # sparse cosine
    dot = 0.0
    na = 0.0
    nb = 0.0
    for k, v in a.items():
        na += v * v
        if k in b:
            dot += v * b[k]
    for v in b.values():
        nb += v * v
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def search(question: str, user_role: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Returns top-k chunks the user is allowed to see.
    Each item includes doc_id, chunk_index, chunk_text, score
    """
    q_vec = _tf(_tokenize(question))

    conn = get_conn()
    cur = conn.cursor()

    # Get allowed docs for this role
    cur.execute("SELECT doc_id, allowed_roles FROM documents")
    allowed_doc_ids = []
    for doc_id, allowed_roles_json in cur.fetchall():
        roles = json.loads(allowed_roles_json)
        if user_role in roles:
            allowed_doc_ids.append(doc_id)

    if not allowed_doc_ids:
        conn.close()
        return []

    # Pull chunks for allowed docs
    placeholders = ",".join(["?"] * len(allowed_doc_ids))
    cur.execute(f"""
        SELECT doc_id, chunk_index, chunk_text
        FROM chunks
        WHERE doc_id IN ({placeholders})
    """, allowed_doc_ids)

    scored = []
    for doc_id, chunk_index, chunk_text in cur.fetchall():
        c_vec = _tf(_tokenize(chunk_text))
        score = _cosine(q_vec, c_vec)
        scored.append({
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "score": score
        })

    conn.close()

    scored.sort(key=lambda x: x["score"], reverse=True)
    # filter out super low scores (optional)
    top = [s for s in scored[:k] if s["score"] > 0.0]
    return top
