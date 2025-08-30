# app/logic/orchestrator.py
from __future__ import annotations
from typing import Dict, Any

from app.search.provider import get_search
from app.logic.selector import select_evidence
from app.nlp.verdict import make_verdict
from app.logic.communicator import build_post
from app.store.db import save_result

async def run_pipeline(claim: str) -> Dict[str, Any]:
    search = get_search()
    # 1) search
    sources = await search(claim)
    # 2) select evidence
    picked = await select_evidence(claim, sources, per_source=2, max_total=8)
    # 3) verdict
    label, confidence, rationale, cites = make_verdict(claim, picked)
    # 4) communicator
    post = build_post(claim, label, rationale, picked, cites)

    result: Dict[str, Any] = {
        "claim": claim,
        "verdict": label,
        "confidence": round(float(abs(confidence)), 3),
        "rationale": rationale,
        "post": post,
        "sources": [s.model_dump(mode='json') for s in picked],
        "id": "",
    }
    rid = save_result(result)
    result["id"] = rid
    return result
