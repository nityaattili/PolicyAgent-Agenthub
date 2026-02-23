import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "agenthub.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
      doc_id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      classification TEXT NOT NULL,
      allowed_roles TEXT NOT NULL,
      content TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
      chunk_id TEXT PRIMARY KEY,
      doc_id TEXT NOT NULL,
      chunk_text TEXT NOT NULL,
      chunk_index INTEGER NOT NULL,
      FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
      run_id TEXT PRIMARY KEY,
      user_role TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT,
      citations TEXT,
      guardrail_flags TEXT,
      status TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
