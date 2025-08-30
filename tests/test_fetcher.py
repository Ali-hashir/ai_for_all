"""Tests for fetch functionality."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.fetch.fetcher import get_paragraphs_for_url


@pytest.mark.asyncio
async def test_get_paragraphs_success():
    """Test successful content fetching and extraction."""
    # Mock HTML content
    mock_html = """
    <html>
        <body>
            <article>
                <p>This is the first paragraph of the main content.</p>
                <p>This is the second paragraph with important information.</p>
                <p>This is the third paragraph continuing the story.</p>
            </article>
        </body>
    </html>
    """
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        paragraphs = await get_paragraphs_for_url("https://example.com/article")
        
        assert len(paragraphs) >= 1
        # Should contain meaningful content
        assert any("paragraph" in p.lower() for p in paragraphs)


@pytest.mark.asyncio
async def test_get_paragraphs_trafilatura_fallback():
    """Test that trafilatura extraction works."""
    # Test with a simple HTML structure that trafilatura can handle
    mock_html = """
    <!DOCTYPE html>
    <html>
        <head><title>Test Article</title></head>
        <body>
            <main>
                <h1>Test Article Title</h1>
                <p>This is a test paragraph that should be extracted by trafilatura.</p>
                <p>This is another paragraph with substantive content for testing.</p>
            </main>
        </body>
    </html>
    """
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        paragraphs = await get_paragraphs_for_url("https://example.com/test")
        
        # Should extract at least some content
        assert len(paragraphs) >= 1
        # Content should be meaningful (not just whitespace)
        assert any(len(p.strip()) > 10 for p in paragraphs)


@pytest.mark.asyncio 
async def test_get_paragraphs_min_length_filter():
    """Test that short paragraphs are filtered out."""
    mock_html = """
    <html>
        <body>
            <div>
                <p>Short.</p>
                <p>This is a longer paragraph that should be included in the results.</p>
                <p>OK</p>
                <p>Another substantial paragraph with enough content to be useful for analysis.</p>
            </div>
        </body>
    </html>
    """
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        paragraphs = await get_paragraphs_for_url("https://example.com/test")
        
        # Should filter out very short paragraphs
        for p in paragraphs:
            assert len(p.strip()) >= 10


@pytest.mark.asyncio
async def test_get_paragraphs_http_error():
    """Test handling of HTTP errors."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = Exception("HTTP 404")
        
        paragraphs = await get_paragraphs_for_url("https://example.com/notfound")
        
        # Should return empty list on error
        assert paragraphs == []


@pytest.mark.asyncio
async def test_get_paragraphs_empty_content():
    """Test handling of empty or minimal content."""
    mock_html = "<html><body></body></html>"
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        paragraphs = await get_paragraphs_for_url("https://example.com/empty")
        
        # Should handle empty content gracefully
        assert isinstance(paragraphs, list)
