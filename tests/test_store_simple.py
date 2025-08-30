"""Simple tests for storage functionality."""
import pytest
from app.store.db import _gen_id


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


def test_save_and_load_basic():
    """Basic test that storage functions can be imported and run."""
    from app.store.db import init_db, save_result, load_result
    
    # Should not crash on import
    assert callable(init_db)
    assert callable(save_result)
    assert callable(load_result)
    
    # Test missing result
    missing = load_result("definitely-not-exists")
    assert missing is None
