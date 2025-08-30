# app/search/serper.py
from __future__ import annotations
import httpx
from typing import List
from app.deps import get_settings
from app.schemas import Source
from .base import dedupe_by_domain

ENDPOINT = "https://google.serper.dev/search"

async def search(query: str) -> List[Source]:
    s = get_settings()
    if not s.serper_api_key:
        raise RuntimeError("SERPER_API_KEY is not set")
    headers = {"X-API-KEY": s.serper_api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": 10}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(ENDPOINT, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    items: list[Source] = []
    for it in data.get("organic", [])[:10]:
        title = it.get("title") or ""
        link = it.get("link") or ""
        snippet = it.get("snippet")
        if title and link:
            try:
                items.append(Source(title=title, url=link, snippet=snippet))
            except Exception:
                continue
    return dedupe_by_domain(items, k=5)
