"""FastAPI main application module."""

import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from app.deps import get_active_search_provider
from app.search.provider import get_search

# Create FastAPI app instance
app = FastAPI(
    title="AI For All - Fact Checker",
    description="A fact-checking API that analyzes claims and returns verdicts with sources",
    version="1.0.0"
)


@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {"ok": True, "provider": get_active_search_provider()}


@app.get("/_search")
async def _search(q: str = Query(..., min_length=3, max_length=200)):
    """Debug search endpoint for testing search functionality."""
    search = get_search()
    results = await search(q)
    return {"count": len(results), "items": [r.model_dump() for r in results]}


@app.get("/_fetch")
async def _fetch(u: str = Query(..., min_length=10, max_length=2000)):
    """Debug fetch endpoint for testing URL content extraction."""
    from app.fetch.fetcher import get_paragraphs_for_url
    paras = await get_paragraphs_for_url(u)
    return {"count": len(paras), "samples": paras[:3]}


@app.get("/_select")
async def _select(claim: str = Query(..., min_length=8, max_length=300)):
    """Debug select endpoint for testing evidence selection."""
    from app.logic.selector import select_evidence
    search = get_search()
    sources = await search(claim)
    picked = await select_evidence(claim, sources, per_source=2, max_total=8)
    return {"n_sources": len(picked), "items": [s.model_dump() for s in picked]}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "AI For All - Fact Checker",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "check_claim": "/check",
            "view_result": "/r/{id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
