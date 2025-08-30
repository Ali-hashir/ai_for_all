"""Tests for storage functionality."""
import pytest
import tempfile
import os
from app.store.db import init_db, save_result, load_result, _gen_id


def test_gen_id():
    """Test ID generation."""
    rid1 = _gen_id()
    rid2 = _gen_id()
    
    # Should generate different IDs
    assert rid1 != rid2
    
    # Should be reasonable length
    assert 6 <= len(rid1) <= 10
    assert 6 <= len(rid2) <= 10
    
    # Should only contain URL-safe characters
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    assert all(c in allowed for c in rid1)


def test_save_and_load_result():
    """Test saving and loading results."""
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Override DB_PATH for this test
        original_path = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = tmp_path
        
        # Reload the module to pick up new path
        import importlib
        from app.store import db
        importlib.reload(db)
        
        # Initialize database
        db.init_db()
        
        # Test data
        test_result = {
            "claim": "Test claim for storage",
            "verdict": "True",
            "confidence": 0.85,
            "rationale": "Test rationale",
            "post": "Test post content",
            "sources": [
                {
                    "title": "Test Source",
                    "url": "https://example.com",
                    "snippet": "Test snippet",
                    "evidence": ["Test evidence"]
                }
            ]
        }
        
        # Save result
        rid = db.save_result(test_result)
        assert rid
        assert len(rid) >= 6
        
        # Load result
        loaded = db.load_result(rid)
        assert loaded is not None
        assert loaded["claim"] == test_result["claim"]
        assert loaded["verdict"] == test_result["verdict"]
        assert loaded["confidence"] == test_result["confidence"]
        assert loaded["id"] == rid  # Should have added ID
        
        # Test non-existent ID
        missing = db.load_result("nonexistent")
        assert missing is None
        
    finally:
        # Cleanup
        if original_path:
            os.environ["DB_PATH"] = original_path
        else:
            os.environ.pop("DB_PATH", None)
        
        # Remove temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_save_result_with_existing_id():
    """Test saving result with existing ID."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        original_path = os.environ.get("DB_PATH")
        os.environ["DB_PATH"] = tmp_path
        
        import importlib
        from app.store import db
        importlib.reload(db)
        
        db.init_db()
        
        # Test with predefined ID
        test_result = {
            "id": "custom123",
            "claim": "Test with custom ID",
            "verdict": "False"
        }
        
        rid = db.save_result(test_result)
        assert rid == "custom123"
        
        loaded = db.load_result("custom123")
        assert loaded["claim"] == "Test with custom ID"
        
    finally:
        if original_path:
            os.environ["DB_PATH"] = original_path
        else:
            os.environ.pop("DB_PATH", None)
        
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
