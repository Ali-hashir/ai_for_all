"""Tests for search functionality."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


def test_simple():
    """Simple test to verify pytest discovers this file."""
    assert True


@pytest.mark.asyncio
async def test_serper_search_success():
    """Test successful Serper search."""
    from app.search.serper import search as serper_search
    
    # Mock response from Serper API
    mock_response = {
        "organic": [
            {
                "title": "Test Title 1",
                "link": "https://example.com/1",
                "snippet": "Test snippet 1"
            },
            {
                "title": "Test Title 2", 
                "link": "https://example.com/2",
                "snippet": "Test snippet 2"
            }
        ]
    }
    
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('app.search.serper.get_settings') as mock_settings:
        
        # Mock settings
        mock_settings.return_value.serper_api_key = "test-key"
        
        # Mock HTTP response
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = MagicMock()
        mock_post.return_value = mock_response_obj
        
        results = await serper_search("test query")
        
        assert len(results) == 2
        assert results[0].title == "Test Title 1"
        assert results[0].url == "https://example.com/1"
        assert results[0].snippet == "Test snippet 1"


@pytest.mark.asyncio
async def test_serper_search_deduplication():
    """Test that duplicate domains are filtered out."""
    from app.search.serper import search as serper_search
    
    mock_response = {
        "organic": [
            {
                "title": "Test Title 1",
                "link": "https://example.com/page1",
                "snippet": "Test snippet 1"
            },
            {
                "title": "Test Title 2",
                "link": "https://example.com/page2", 
                "snippet": "Test snippet 2"
            },
            {
                "title": "Test Title 3",
                "link": "https://different.com/page1",
                "snippet": "Test snippet 3"
            }
        ]
    }
    
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('app.search.serper.get_settings') as mock_settings:
        
        mock_settings.return_value.serper_api_key = "test-key"
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = MagicMock()
        mock_post.return_value = mock_response_obj
        
        results = await serper_search("test query")
        
        # Should only get 2 results due to deduplication
        assert len(results) == 2
        domains = {result.url for result in results}
        assert "https://example.com/page1" in domains
        assert "https://different.com/page1" in domains


@pytest.mark.asyncio
async def test_serper_search_no_results():
    """Test handling of empty search results."""
    from app.search.serper import search as serper_search
    
    mock_response = {"organic": []}
    
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('app.search.serper.get_settings') as mock_settings:
        
        mock_settings.return_value.serper_api_key = "test-key"
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status = MagicMock()
        mock_post.return_value = mock_response_obj
        
        results = await serper_search("test query")
        
        assert len(results) == 0


@pytest.mark.asyncio
async def test_serper_search_missing_api_key():
    """Test error handling for missing API key."""
    from app.search.serper import search as serper_search
    
    with patch('app.search.serper.get_settings') as mock_settings:
        mock_settings.return_value.serper_api_key = ""
        
        with pytest.raises(RuntimeError, match="SERPER_API_KEY is not set"):
            await serper_search("test query")
