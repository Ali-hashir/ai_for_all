# app/nlp/nli.py
from __future__ import annotations
from functools import lru_cache
from typing import List, Dict, Tuple

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "MoritzLaurer/DeBERTa-v3-base-mnli"

@lru_cache(maxsize=1)
def _load() -> Tuple[AutoTokenizer, AutoModelForSequenceClassification, torch.device, Dict[str, int]]:
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    mdl.eval()
    device = torch.device("cpu")
    mdl.to(device)

    # Map label names to ids case-insensitively
    name_to_id = {v.lower(): int(k) for k, v in mdl.config.id2label.items()}
    # Ensure keys exist for mnli
    # Common names: "entailment", "neutral", "contradiction"
    for needed in ("entailment", "neutral", "contradiction"):
        assert any(needed in k for k in name_to_id.keys()), f"Label {needed} missing"
    return tok, mdl, device, name_to_id

def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)

def score_pairs(pairs: List[Tuple[str, str]], batch_size: int = 8) -> List[Dict[str, float]]:
    """
    pairs: list of (premise, hypothesis)
    returns: list of dicts with probs for 'entail', 'contradict', 'neutral'
    """
    tok, mdl, device, name_to_id = _load()
    out: list[Dict[str, float]] = []
    for i in range(0, len(pairs), batch_size):
        chunk = pairs[i:i + batch_size]
        premises = [p for p, _ in chunk]
        hyps = [h for _, h in chunk]
        with torch.no_grad():
            enc = tok(
                premises,
                hyps,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(device)
            logits = mdl(**enc).logits.detach().cpu().numpy()
        probs = _softmax(logits)
        ent_id = next(v for k, v in name_to_id.items() if "entail" in k)
        con_id = next(v for k, v in name_to_id.items() if "contradict" in k)
        neu_id = next(v for k, v in name_to_id.items() if "neutral" in k)
        for row in probs:
            out.append({
                "entail": float(row[ent_id]),
                "contradict": float(row[con_id]),
                "neutral": float(row[neu_id]),
            })
    return out

def score_many(premises: List[str], hypothesis: str, batch_size: int = 8) -> List[Dict[str, float]]:
    return score_pairs([(p, hypothesis) for p in premises], batch_size=batch_size)

def score_one(premise: str, hypothesis: str) -> Dict[str, float]:
    return score_pairs([(premise, hypothesis)])[0]
