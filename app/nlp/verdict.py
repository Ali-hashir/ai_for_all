# app/nlp/verdict.py
from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np

from app.schemas import Source, VerdictLabel
from app.nlp.nli import score_many

TH_TRUE = 0.60
TH_FALSE = 0.60
DELTA = 0.20

def _flatten_evidence(sources: List[Source]) -> Tuple[List[str], List[int]]:
    premises: list[str] = []
    owner_idx: list[int] = []
    for idx, s in enumerate(sources):
        for ev in s.evidence or []:
            if not ev:
                continue
            txt = ev.strip()
            if len(txt) < 40:
                continue
            premises.append(txt)
            owner_idx.append(idx)
    return premises, owner_idx

def _verdict_from(E: float, C: float) -> VerdictLabel:
    if E >= TH_TRUE and (E - C) >= DELTA:
        return "True"
    if C >= TH_FALSE and (C - E) >= DELTA:
        return "False"
    if max(E, C) >= 0.50 and abs(E - C) < DELTA:
        return "Misleading"
    return "Unverified"

def _short(txt: str, n: int = 240) -> str:
    return txt if len(txt) <= n else txt[: n - 3] + "..."

def make_verdict(
    claim: str,
    sources: List[Source],
) -> Tuple[VerdictLabel, float, str, Dict[str, List[int]]]:
    """
    Returns: (label, confidence, rationale, cites)
    - confidence = |E - C|
    - cites has indices of sources used, e.g. {"support":[0], "contra":[2]}
    """
    premises, owners = _flatten_evidence(sources)
    if not premises:
        return "Unverified", 0.0, "No strong evidence available from retrieved sources.", {}

    scores = score_many(premises, claim)
    E = float(np.mean([s["entail"] for s in scores]))
    C = float(np.mean([s["contradict"] for s in scores]))
    label = _verdict_from(E, C)
    confidence = float(abs(E - C))

    # pick top items for rationale
    ent_vals = np.array([s["entail"] for s in scores])
    con_vals = np.array([s["contradict"] for s in scores])
    top_ent_i = int(ent_vals.argmax())
    top_con_i = int(con_vals.argmax())
    ent_src = owners[top_ent_i]
    con_src = owners[top_con_i]

    if label == "True":
        rationale = f"Evidence aligns with the claim based on [{ent_src + 1}]. " + _short(premises[top_ent_i])
        cites = {"support": [ent_src]}
    elif label == "False":
        rationale = f"Evidence contradicts the claim based on [{con_src + 1}]. " + _short(premises[top_con_i])
        cites = {"contra": [con_src]}
    elif label == "Misleading":
        rationale = f"Sources both support [{ent_src + 1}] and contradict [{con_src + 1}] the claim."
        cites = {"support": [ent_src], "contra": [con_src]}
    else:
        rationale = "Insufficient or conflicting evidence across retrieved sources."
        cites = {}

    return label, confidence, rationale, cites
