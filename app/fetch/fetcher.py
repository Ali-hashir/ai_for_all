# app/fetch/fetcher.py
from __future__ import annotations
import re
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document
import trafilatura

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en;q=0.9",
}

TIMEOUT = httpx.Timeout(10.0, connect=5.0)
BLOCKED_SCHEMES = {"javascript", "data"}
BLOCKED_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

def _looks_blocked(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme in BLOCKED_SCHEMES:
            return True
        for ext in BLOCKED_EXTS:
            if p.path.lower().endswith(ext):
                return True
    except Exception:
        return True
    return False

async def fetch_html(url: str) -> Optional[str]:
    if _looks_blocked(url):
        return None
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(url)
        ct = resp.headers.get("Content-Type", "")
        if "text/html" not in ct and "application/xhtml+xml" not in ct:
            return None
        resp.raise_for_status()
        return resp.text

def _clean_text(txt: str) -> str:
    txt = re.sub(r"\r\n|\r", "\n", txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()

def _bs4_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Drop nav, footer, script, style
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    return _clean_text(soup.get_text("\n"))

def extract_main_text(html: str, base_url: str | None = None) -> Optional[str]:
    # Try trafilatura first
    try:
        txt = trafilatura.extract(html, url=base_url, include_comments=False, include_tables=False)
        if txt and len(txt) >= 400:
            return _clean_text(txt)
    except Exception:
        pass
    # Fallback to readability-lxml
    try:
        doc = Document(html)
        summary_html = doc.summary() or ""
        txt = _bs4_text(summary_html)
        if txt and len(txt) >= 300:
            return _clean_text(txt)
    except Exception:
        pass
    # Last resort: whole page text
    try:
        txt = _bs4_text(html)
        if txt and len(txt) >= 200:
            return _clean_text(txt)
    except Exception:
        pass
    return None

def _split_paragraphs(text: str) -> List[str]:
    # Split on blank lines first
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out: list[str] = []
    for p in parts:
        # Further split very long paragraphs by sentence groups
        if len(p) > 1200:
            chunks = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", p)
            buf = []
            cur = ""
            for s in chunks:
                cur = (cur + " " + s).strip()
                if len(cur) >= 400:
                    buf.append(cur)
                    cur = ""
            if cur:
                buf.append(cur)
            out.extend(buf)
        else:
            out.append(p)
    # Filter short or junky lines
    out = [p for p in out if len(p) >= 160]
    # Deduplicate
    seen: set[str] = set()
    deduped: list[str] = []
    for p in out:
        key = re.sub(r"\W+", " ", p).strip().casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped[:12]  # cap

async def get_paragraphs_for_url(url: str) -> List[str]:
    html = await fetch_html(url)
    if not html:
        return []
    text = extract_main_text(html, base_url=url)
    if not text:
        return []
    return _split_paragraphs(text)

async def get_paragraphs_with_fallback(url: str, snippet: str | None) -> List[str]:
    paras = await get_paragraphs_for_url(url)
    if paras:
        return paras
    return [snippet] if snippet else []
