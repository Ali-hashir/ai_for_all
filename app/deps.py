# app/deps.py
from __future__ import annotations
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, Dict
from dotenv import load_dotenv

load_dotenv()  # reads .env if present

SearchProvider = Literal["google", "brave", "serper"]

@dataclass(frozen=True)
class Settings:
    search_provider: SearchProvider = "serper"
    google_cse_id: str | None = None
    google_api_key: str | None = None
    brave_api_key: str | None = None
    serper_api_key: str | None = None

def _read_env() -> Settings:
    provider = (os.getenv("SEARCH_PROVIDER") or "serper").lower()
    if provider not in ("google", "brave", "serper"):
        provider = "serper"
    return Settings(
        search_provider=provider,  # type: ignore[assignment]
        google_cse_id=os.getenv("GOOGLE_CSE_ID"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        brave_api_key=os.getenv("BRAVE_API_KEY"),
        serper_api_key=os.getenv("SERPER_API_KEY"),
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return _read_env()

def get_active_search_provider() -> SearchProvider:
    return get_settings().search_provider

def get_active_search_headers() -> Dict[str, str]:
    s = get_settings()
    if s.search_provider == "brave" and s.brave_api_key:
        return {"X-Subscription-Token": s.brave_api_key}
    if s.search_provider == "serper" and s.serper_api_key:
        return {"X-API-KEY": s.serper_api_key}
    # google uses key params, not headers
    return {}
