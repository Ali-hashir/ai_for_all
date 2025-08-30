# app/nlp/embed.py
from __future__ import annotations
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    # CPU is fine for this model
    return SentenceTransformer(MODEL_NAME)

def embed_texts(texts: list[str]) -> np.ndarray:
    model = _load_model()
    vecs = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vecs.astype("float32")

def embed_text(text: str) -> np.ndarray:
    return embed_texts([text])[0]
