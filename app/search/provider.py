# app/search/provider.py
from __future__ import annotations
from app.deps import get_settings
from . import serper

def get_search():
    provider = get_settings().search_provider
    if provider == "serper":
        return serper.search
    raise NotImplementedError(f"search provider '{provider}' not implemented yet")
