import hashlib
import json
import uuid
from pathlib import Path
from datetime import datetime

from app.db import get_conn

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "kb_docs"

def _parse_metadata_and_body(text: str):
    """
    Expected format in the top lines:
    # Title
    Classification: INTERNAL
    AllowedRoles: employee, manager, hr
    <blank line>
    Body...
    """
    lines = [l.rstrip() for l in text.splitlines()]
    title = lines[0].lstrip("#").strip() if lines else "Untitled"
    classification = "INTERNAL"
    allowed_roles = ["employee"]

    for l in lines[:10]:
        if l.lower().startswith("classification:"):
            classification = l.split(":", 1)[1].strip().upper()
        if l.lower().startswith("allowedroles:"):
            roles_str = l.split(":", 1)[1].strip()
            allowed_roles = [r.strip() for r in roles_str.split(",") if r.strip()]

    body = "\n".join(lines)
    return title, classification, allowed_roles, body

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 80):
    """
    Simple character-based chunking for MVP.
    """
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        i += max(1, chunk_size - overlap)
    return chunks

def ingest_all():
    conn = get_conn()
    cur = conn.cursor()

    md_files = sorted(KB_DIR.glob("*.md"))
    if not md_files:
        raise RuntimeError(f"No .md files found in {KB_DIR}")

    for fp in md_files:
        text = fp.read_text(encoding="utf-8")
        title, classification, allowed_roles, body = _parse_metadata_and_body(text)

        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        doc_id = fp.stem  # stable id from filename
        updated_at = datetime.utcnow().isoformat()

        # Upsert document
        cur.execute("""
        INSERT INTO documents (doc_id, title, classification, allowed_roles, content)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
          title=excluded.title,
          classification=excluded.classification,
          allowed_roles=excluded.allowed_roles,
          content=excluded.content
        """, (doc_id, title, classification, json.dumps(allowed_roles), body))

        # Remove old chunks and re-chunk
        cur.execute("DELETE FROM chunks WHERE doc_id=?", (doc_id,))
        chunks = _chunk_text(body)

        for idx, chunk_text in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            cur.execute("""
            INSERT INTO chunks (chunk_id, doc_id, chunk_text, chunk_index)
            VALUES (?, ?, ?, ?)
            """, (chunk_id, doc_id, chunk_text, idx))

    conn.commit()
    conn.close()
    return {"docs_ingested": len(md_files)}
