"""FastAPI main application module."""

import os
from fastapi import FastAPI, Query, HTTPException, Request, Body, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.deps import get_active_search_provider
from app.search.provider import get_search
from app.store.db import init_db, load_result
from app.schemas import CheckRequest

# Create FastAPI app instance
app = FastAPI(
    title="AI For All - Fact Checker",
    description="A fact-checking API that analyzes claims and returns verdicts with sources",
    version="1.0.0"
)

# Templates setup
templates = Jinja2Templates(directory="app/web/templates")

@app.on_event("startup")
def _startup():
    init_db()


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


@app.get("/_nli")
def _nli(text: str = Query(..., min_length=5, max_length=800),
         claim: str = Query(..., min_length=5, max_length=800)):
    """Debug NLI endpoint for testing natural language inference."""
    from app.nlp.nli import score_one
    probs = score_one(text, claim)
    verdict = max(probs, key=probs.get)
    return {"probs": probs, "top": verdict}


@app.get("/_verdict")
async def _verdict(claim: str = Query(..., min_length=8, max_length=300)):
    """Debug verdict endpoint for testing full search → selector → verdict pipeline."""
    from app.logic.selector import select_evidence
    from app.nlp.verdict import make_verdict
    
    search = get_search()
    sources = await search(claim)
    picked = await select_evidence(claim, sources, per_source=2, max_total=8)
    label, confidence, rationale, cites = make_verdict(claim, picked)
    return {
        "label": label,
        "confidence": round(confidence, 3),
        "rationale": rationale,
        "cites": cites,
        "sources": [s.model_dump() for s in picked],
    }


@app.get("/_post")
async def _post(claim: str = Query(..., min_length=8, max_length=300)):
    """Debug post endpoint for testing full search → select → verdict → communicator pipeline."""
    from app.logic.selector import select_evidence
    from app.nlp.verdict import make_verdict
    from app.logic.communicator import build_post
    
    search = get_search()
    sources = await search(claim)
    picked = await select_evidence(claim, sources, per_source=2, max_total=8)
    label, confidence, rationale, cites = make_verdict(claim, picked)
    post = build_post(claim, label, rationale, picked, cites)
    return {
        "label": label,
        "confidence": round(confidence, 3),
        "post_len": len(post),
        "post": post,
    }


@app.get("/r/{rid}", response_class=HTMLResponse)
def read_result(rid: str, request: Request):
    """View a shared fact-check result."""
    data = load_result(rid)
    if not data:
        raise HTTPException(status_code=404, detail="Result not found")
    return templates.TemplateResponse("result.html", {"request": request, "r": data})


@app.post("/check")
async def check(payload: CheckRequest = Body(...)):
    """Main fact-checking endpoint - processes claims and returns verdicts."""
    from app.logic.orchestrator import run_pipeline
    
    claim = payload.claim.strip()
    if len(claim) < 8:
        raise HTTPException(status_code=400, detail="claim too short")
    try:
        result = await run_pipeline(claim)
        return result
    except Exception as e:
        # Return structured fallback rather than 500
        fallback = {
            "claim": claim,
            "verdict": "Unverified",
            "confidence": 0.0,
            "rationale": f"Pipeline error: {type(e).__name__}. Try again later or rephrase.",
            "post": "Verdict: Unverified — Unable to verify due to a temporary error.",
            "sources": [],
            "id": "",
        }
        # do not save failing runs
        return fallback


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Home page with fact-checking form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ui/check", response_class=HTMLResponse)
async def ui_check(request: Request, claim: str = Form(...)):
    """UI endpoint for HTMX form submission."""
    from app.logic.orchestrator import run_pipeline
    
    result = await run_pipeline(claim.strip())
    return templates.TemplateResponse("_result_block.html", {"request": request, "r": result})


# Root API info endpoint  
@app.get("/api")
async def api_info():
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


@app.get("/_save_dummy")
def _save_dummy():
    """Debug endpoint to test saving and sharing functionality."""
    from app.store.db import save_result
    
    dummy = {
      "claim": "The Earth orbits the Sun.",
      "verdict": "True",
      "confidence": 0.8,
      "rationale": "Textbook science and multiple sources support it. [1]",
      "post": "Verdict: True — Basic astronomy supports the claim. Source: nasa.gov https://www.nasa.gov/",
      "sources": [
        {"title":"NASA", "url":"https://www.nasa.gov/", "snippet":"", "evidence":["Earth orbits the Sun."]}
      ],
      "id": ""
    }
    rid = save_result(dummy)
    return {"id": rid, "url": f"/r/{rid}"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
