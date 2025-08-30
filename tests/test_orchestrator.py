"""Tests for orchestrator functionality."""
import pytest
from unittest.mock import patch, AsyncMock
from app.logic.orchestrator import run_pipeline


@pytest.mark.asyncio
async def test_orchestrator_imports():
    """Test that orchestrator can import all required modules."""
    # Should not crash on import
    assert callable(run_pipeline)


@pytest.mark.asyncio
async def test_run_pipeline_structure():
    """Test that run_pipeline returns correct structure."""
    # Mock all the dependencies to avoid actual API calls
    mock_sources = []
    mock_picked = []
    mock_verdict = ("True", 0.8, "Test rationale", {"support": []})
    mock_post = "Test post"
    mock_rid = "test123"
    
    with patch('app.logic.orchestrator.get_search') as mock_get_search, \
         patch('app.logic.orchestrator.select_evidence', new_callable=AsyncMock) as mock_select, \
         patch('app.logic.orchestrator.make_verdict') as mock_make_verdict, \
         patch('app.logic.orchestrator.build_post') as mock_build_post, \
         patch('app.logic.orchestrator.save_result') as mock_save:
        
        # Setup mocks
        mock_search = AsyncMock()
        mock_search.return_value = mock_sources
        mock_get_search.return_value = mock_search
        
        mock_select.return_value = mock_picked
        mock_make_verdict.return_value = mock_verdict
        mock_build_post.return_value = mock_post
        mock_save.return_value = mock_rid
        
        # Run pipeline
        result = await run_pipeline("Test claim")
        
        # Verify structure
        assert isinstance(result, dict)
        assert "claim" in result
        assert "verdict" in result
        assert "confidence" in result
        assert "rationale" in result
        assert "post" in result
        assert "sources" in result
        assert "id" in result
        
        # Verify values
        assert result["claim"] == "Test claim"
        assert result["verdict"] == "True"
        assert result["confidence"] == 0.8
        assert result["rationale"] == "Test rationale"
        assert result["post"] == "Test post"
        assert result["id"] == "test123"
        
        # Verify all components were called
        mock_search.assert_called_once_with("Test claim")
        mock_select.assert_called_once()
        mock_make_verdict.assert_called_once()
        mock_build_post.assert_called_once()
        mock_save.assert_called_once()


def test_check_request_schema():
    """Test that CheckRequest schema works."""
    from app.schemas import CheckRequest
    
    # Valid request
    req = CheckRequest(claim="This is a test claim for validation")
    assert req.claim == "This is a test claim for validation"
    
    # Test validation (too short)
    with pytest.raises(Exception):  # Pydantic validation error
        CheckRequest(claim="short")
