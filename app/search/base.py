# app/search/base.py
from __future__ import annotations
from urllib.parse import urlparse
from app.schemas import Source

def dedupe_by_domain(items: list[Source], k: int = 5) -> list[Source]:
    seen: set[str] = set()
    out: list[Source] = []
    for s in items:
        domain = urlparse(str(s.url)).netloc.lower()
        if domain and domain not in seen:
            seen.add(domain)
            out.append(s)
        if len(out) >= k:
            break
    return out
