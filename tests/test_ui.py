"""Tests for UI functionality."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_home_page():
    """Test that home page loads correctly."""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Automated Fact-Checker" in response.text
    assert "hx-post=\"/ui/check\"" in response.text  # HTMX form
    assert "textarea" in response.text


def test_api_info_endpoint():
    """Test that API info endpoint works."""
    client = TestClient(app)
    response = client.get("/api")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI For All - Fact Checker"
    assert "endpoints" in data
    assert data["endpoints"]["check_claim"] == "/check"


def test_result_page_404():
    """Test that non-existent result returns 404."""
    client = TestClient(app)
    response = client.get("/r/nonexistent")
    
    assert response.status_code == 404


def test_check_endpoint_validation():
    """Test POST /check endpoint validation."""
    client = TestClient(app)
    
    # Test missing claim
    response = client.post("/check", json={})
    assert response.status_code == 422  # Validation error
    
    # Test very short claim (caught by Pydantic min_length=8)
    response = client.post("/check", json={"claim": "short"})
    assert response.status_code == 422  # Pydantic validation error (5 chars < 8)
