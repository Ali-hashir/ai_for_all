# app/logic/communicator.py
from __future__ import annotations
from typing import List, Dict, Optional
from urllib.parse import urlparse
import re

from app.schemas import Source, VerdictLabel

MAX_LEN = 600

def _domain(url: str | None) -> str:
    if not url:
        return "source"
    try:
        host = urlparse(url).netloc or "source"
        return host.replace("www.", "")
    except Exception:
        return "source"

def _pick_url(sources: List[Source], cites: Dict[str, List[int]]) -> Optional[str]:
    # Prefer cited support, then cited contra, then any with evidence, else first source
    for key in ("support", "contra"):
        for i in (cites.get(key) or []):
            if 0 <= i < len(sources):
                return str(sources[i].url)
    for s in sources:
        if s.evidence:
            return str(s.url)
    return str(sources[0].url) if sources else None

def _short_reason(rationale: str, limit: int) -> str:
    # Strip bracket refs like [1], collapse spaces
    r = re.sub(r"\[\d+\]", "", rationale).strip()
    r = re.sub(r"\s+", " ", r)
    return r if len(r) <= limit else (r[: max(0, limit - 1)].rstrip() + "…")

def build_post(
    claim: str,
    label: VerdictLabel,
    rationale: str,
    sources: List[Source],
    cites: Dict[str, List[int]],
) -> str:
    url = _pick_url(sources, cites)
    dom = _domain(url)

    # Base template
    # One link only. Plain English. No hashtags.
    # We reserve space for fixed parts and URL.
    fixed = f"Verdict: {label} — "
    tail = f" Source: {dom} {url or ''}".strip()
    # Compute max space for reason
    room_for_reason = MAX_LEN - len(fixed) - len(tail) - 1  # 1 for space/newline safety
    room_for_reason = max(40, room_for_reason)  # keep reason informative

    reason = _short_reason(rationale, room_for_reason)

    post = f"{fixed}{reason}{tail}"
    if len(post) > MAX_LEN:
        # Final guard: trim reason harder
        overflow = len(post) - MAX_LEN
        reason2 = _short_reason(reason, max(0, len(reason) - overflow - 1))
        post = f"{fixed}{reason2}{tail}"
    return post
