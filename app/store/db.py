# app/store/db.py
from __future__ import annotations
import os, json, sqlite3, secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional

DB_PATH = os.getenv("DB_PATH", "data.db")

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db() -> None:
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id TEXT PRIMARY KEY,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

def _gen_id(n_bytes: int = 6) -> str:
    # URL-safe short id ~8–10 chars
    s = secrets.token_urlsafe(n_bytes)
    return s.replace("-", "").replace("_", "")[:10]

def save_result(result: Dict[str, Any]) -> str:
    rid = str(result.get("id") or _gen_id())
    result["id"] = rid
    payload = json.dumps(result, ensure_ascii=False)
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO results (id, result_json, created_at) VALUES (?, ?, ?)",
            (rid, payload, datetime.now(timezone.utc).isoformat()),
        )
    return rid

def load_result(rid: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute("SELECT result_json FROM results WHERE id = ?", (rid,)).fetchone()
    if not row:
        return None
    return json.loads(row["result_json"])
