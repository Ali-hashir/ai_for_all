# app/logic/selector.py
from __future__ import annotations
import asyncio
from typing import List
import numpy as np

from app.schemas import Source
from app.fetch.fetcher import get_paragraphs_with_fallback
from app.nlp.embed import embed_text, embed_texts

SIM_THRESHOLD = 0.25  # drop very weak matches

async def select_evidence(
    claim: str,
    sources: List[Source],
    per_source: int = 2,
    max_total: int = 8,
) -> List[Source]:
    claim_vec = embed_text(claim)

    # fetch paragraphs concurrently
    tasks = [get_paragraphs_with_fallback(s.url, s.snippet) for s in sources]
    all_paras = await asyncio.gather(*tasks)

    selected_sources: list[Source] = []
    for s, paras in zip(sources, all_paras):
        if not paras:
            selected_sources.append(s)
            continue

        para_vecs = embed_texts(paras)
        sims = para_vecs @ claim_vec  # cosine because normalized
        top_idx = np.argsort(-sims)[:per_source]

        evidence: list[str] = []
        for i in top_idx:
            score = float(sims[i])
            if score < SIM_THRESHOLD:
                continue
            text = paras[i].strip()
            if len(text) > 500:
                text = text[:497] + "..."
            evidence.append(text)

        selected_sources.append(
            Source(title=s.title, url=s.url, snippet=s.snippet, evidence=evidence)
        )

    # cap total evidence across all sources
    def total_evidence() -> int:
        return sum(len(s.evidence) for s in selected_sources)

    if total_evidence() > max_total:
        # trim round-robin
        while total_evidence() > max_total:
            for s in selected_sources:
                if s.evidence:
                    s.evidence.pop()
                if total_evidence() <= max_total:
                    break

    return selected_sources
