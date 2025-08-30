# app/schemas.py
from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl

VerdictLabel = Literal["True", "False", "Misleading", "Unverified"]

class CheckRequest(BaseModel):
    claim: str = Field(..., min_length=8, max_length=1000)

class Source(BaseModel):
    title: str
    url: HttpUrl
    snippet: str | None = None
    evidence: List[str] = Field(default_factory=list)

class CheckResult(BaseModel):
    claim: str
    verdict: VerdictLabel
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    post: str
    sources: List[Source]
    id: str
