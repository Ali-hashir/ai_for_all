"""FastAPI main application module."""

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.deps import get_active_search_provider

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
