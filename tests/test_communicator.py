"""Tests for communicator functionality."""
import pytest
from app.schemas import Source
from app.logic.communicator import build_post, _domain, _pick_url, _short_reason


def test_domain_extraction():
    """Test domain extraction from URLs."""
    assert _domain("https://www.example.com/path") == "example.com"
    assert _domain("https://news.bbc.co.uk/article") == "news.bbc.co.uk"
    assert _domain("invalid-url") == "source"
    assert _domain(None) == "source"


def test_pick_url_priority():
    """Test URL selection priority logic."""
    sources = [
        Source(title="A", url="https://example1.com", evidence=["evidence1"]),
        Source(title="B", url="https://example2.com", evidence=["evidence2"]),
        Source(title="C", url="https://example3.com", evidence=["evidence3"]),
    ]
    
    # Should prefer support citations
    cites = {"support": [1], "contra": [2]}
    url = _pick_url(sources, cites)
    assert "example2.com" in url
    
    # Should prefer contra citations if no support
    cites = {"contra": [2]}
    url = _pick_url(sources, cites)
    assert "example3.com" in url
    
    # Should pick first with evidence if no citations
    url = _pick_url(sources, {})
    assert "example1.com" in url


def test_short_reason():
    """Test reason shortening and bracket removal."""
    rationale = "Evidence aligns with the claim based on [1]. The detailed explanation continues."
    
    # Should remove brackets
    result = _short_reason(rationale, 100)
    assert "[1]" not in result
    assert "Evidence aligns with the claim based on" in result
    
    # Should truncate if too long
    result = _short_reason(rationale, 30)
    assert len(result) <= 30
    assert result.endswith("…")


def test_build_post_basic():
    """Test basic post building functionality."""
    claim = "Test claim"
    label = "True"
    rationale = "Evidence supports this claim based on [1]. The source provides clear confirmation."
    sources = [
        Source(title="Test", url="https://example.com/article", evidence=["Supporting evidence"])
    ]
    cites = {"support": [0]}
    
    post = build_post(claim, label, rationale, sources, cites)
    
    # Check basic structure
    assert "Verdict: True" in post
    assert "example.com" in post
    assert "https://example.com/article" in post
    assert len(post) <= 600
    
    # Should not contain bracket references
    assert "[1]" not in post


def test_build_post_length_limit():
    """Test that posts are properly truncated to 600 characters."""
    claim = "Test claim"
    label = "Misleading"
    # Very long rationale
    rationale = "This is a very long rationale that goes on and on with lots of details " * 20
    sources = [
        Source(title="Test", url="https://very-long-domain-name-here.com/very/long/path/to/article", evidence=["evidence"])
    ]
    cites = {"support": [0]}
    
    post = build_post(claim, label, rationale, sources, cites)
    
    assert len(post) <= 600
    assert "Verdict: Misleading" in post
    assert "very-long-domain-name-here.com" in post


def test_build_post_no_sources():
    """Test post building with empty sources list."""
    claim = "Test claim"
    label = "Unverified"
    rationale = "No evidence available."
    sources = []
    cites = {}
    
    post = build_post(claim, label, rationale, sources, cites)
    
    assert "Verdict: Unverified" in post
    assert "No evidence available" in post
    assert len(post) <= 600
