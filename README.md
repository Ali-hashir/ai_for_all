---
title: AI For All - Fact Checker
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# AI For All - Fact Checker

A sophisticated fact-checking API built with FastAPI that verifies claims using web search, content analysis, and natural language inference.

## Features

- **Multi-Source Verification**: Search and analyze claims across multiple web sources
- **ML-Powered Analysis**: Uses advanced NLP models for semantic understanding and inference
- **Smart Content Extraction**: Intelligent web scraping with multiple fallback strategies
- **Verdict Aggregation**: Combines evidence from multiple sources for accurate assessment
- **Post Generation**: Creates shareable social media content based on findings
- **Persistent Storage**: Save and share results with unique URLs
- **Web Interface**: User-friendly HTML interface with real-time updates

## Demo

🚀 **Live Demo**: [Deploy your own on Railway](https://railway.app)

### Try These Example Claims:
- "The Earth is flat"
- "Vaccines cause autism"
- "Climate change is a hoax"
- "The Great Wall of China is visible from space"

### How It Works:
1. **Enter a claim** in the web interface at `/`
2. **AI searches** multiple sources across the web using Serper API
3. **ML models analyze** content for relevance and accuracy using DeBERTa and sentence-transformers
4. **Get instant verdict** with supporting evidence and confidence scores
5. **Share results** with unique URLs at `/r/{share_id}`

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd ai_for_all
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   # Create .env file with your Serper API key
   echo "SERPER_API_KEY=your_serper_api_key_here" > .env
   ```

4. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Test the application**:
   - Visit `http://localhost:8000` for the web interface
   - Or test the API: `curl -X POST http://localhost:8000/check -H "Content-Type: application/json" -d '{"claim": "The Earth is round"}'`

## API Endpoints

### Core Endpoints
- `GET /` - Web interface homepage
- `POST /check` - Fact-check a claim (JSON API)
- `POST /ui/check` - Fact-check via web form (HTMX)
- `GET /r/{share_id}` - View shareable fact-check result

### Example API Usage

**Request:**
```bash
curl -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth is flat"}'
```

**Response:**
```json
{
  "claim": "The Earth is flat",
  "verdict": "False",
  "confidence": 0.95,
  "sources": [
    {
      "url": "https://example.com/earth-round",
      "title": "Scientific Evidence for Earth's Spherical Shape",
      "snippet": "Multiple lines of evidence confirm...",
      "relevance": 0.92
    }
  ],
  "reasoning": "Based on overwhelming scientific evidence...",
  "post": "🔍 Fact Check: The claim 'The Earth is flat' is FALSE...",
  "share_id": "abc123def456"
}
```

## Architecture

### Core Components

1. **Search Module** (`app/search/`): Serper API integration with deduplication
2. **Fetch Module** (`app/fetch/`): Multi-strategy content extraction (trafilatura, readability, BeautifulSoup)
3. **NLP Module** (`app/nlp/`): Embeddings (sentence-transformers) and NLI (DeBERTa)
4. **Logic Module** (`app/logic/`): Pipeline orchestration and post generation
5. **Storage Module** (`app/store/`): SQLite database with JSON blob storage
6. **Web Module** (`app/web/`): Jinja2 templates with HTMX integration

### Technology Stack

- **Backend**: FastAPI with async/await support
- **ML/NLP**: sentence-transformers (all-MiniLM-L6-v2), transformers (DeBERTa-v3-base-mnli)
- **Search**: Serper API for web search
- **Storage**: SQLite with JSON serialization
- **Frontend**: HTMX + Jinja2 templates (no build step required)
- **Web Scraping**: trafilatura, readability-lxml, BeautifulSoup

## Deployment

### Railway Deployment (Recommended)

This project is configured for one-click deployment on Railway:

1. **Fork this repository** on GitHub
2. **Connect to Railway**:
   - Go to [Railway](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your fork
3. **Set environment variables** in Railway dashboard:
   - `SERPER_API_KEY`: Your Serper API key (get from [serper.dev](https://serper.dev))
4. **Deploy automatically** - Railway uses `Procfile` and `runtime.txt`

The app will be live at your Railway-provided URL (e.g., `https://your-app.up.railway.app`)

### Hugging Face Spaces Deployment

Deploy on Hugging Face Spaces for free ML model hosting:

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Select Docker** as the Space SDK
3. **Upload your repository** files including the `Dockerfile`
4. **Set environment variables** in Space settings:
   - `SERPER_API_KEY`: Your Serper API key
5. **Deploy automatically** - Spaces will build using the Dockerfile

The app will be live at your Space URL: `https://<your-space>.<your-username>.hf.space/`

**API Example for Spaces:**
```bash
curl -X POST "https://<your-space>.<your-username>.hf.space/check" \
  -H "Content-Type: application/json" \
  -d '{"claim": "The Earth orbits the Sun."}'
```

### Manual Deployment

For other platforms, the project includes:
- `Procfile`: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `runtime.txt`: `python-3.11.9`
- `Dockerfile`: Docker container configuration for Spaces
- `requirements.txt`: All dependencies with versions

### Environment Variables

- `SERPER_API_KEY`: **Required** - Get from [serper.dev](https://serper.dev)
- `DATABASE_URL`: Optional - SQLite database path (default: `./factcheck.db`)

## Testing

Run the comprehensive test suite (18 tests covering all components):

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Expected output: 18 tests passed
```

Tests cover:
- API endpoints and response formats
- ML pipeline components (search, NLP, logic)
- Database operations and JSON serialization
- Error handling and edge cases

## Technical Implementation

### Pipeline Flow
1. **Claim Input**: User submits claim via web UI or API
2. **Web Search**: Serper API searches for relevant sources
3. **Content Extraction**: Multi-strategy scraping of source content
4. **Relevance Filtering**: Sentence embeddings rank source relevance
5. **Fact Verification**: DeBERTa model performs natural language inference
6. **Verdict Aggregation**: Confidence-weighted averaging of individual verdicts
7. **Post Generation**: AI creates shareable social media content
8. **Result Storage**: SQLite database saves results with unique share IDs

### Key Features
- **Domain Deduplication**: Prevents bias from multiple sources from same domain
- **Confidence Scoring**: ML-based confidence estimation for verdicts
- **Robust Error Handling**: Graceful degradation when sources fail to load
- **JSON Serialization**: Proper handling of Pydantic models for database storage
- **HTMX Integration**: Dynamic UI updates without JavaScript build complexity

## Troubleshooting

### Common Issues

**"No search results found"**
- Check your `SERPER_API_KEY` is set correctly
- Verify the claim is in English and well-formed

**"Model loading errors"**
- Ensure you have sufficient disk space (~2GB for models)
- Models download automatically on first run

**"Database errors"**
- Check write permissions in the app directory
- SQLite database is created automatically

### Development Notes

**Pydantic v2 Compatibility**: The project uses `model_dump(mode='json')` for proper URL serialization when saving to database.

**Model Caching**: Transformer models are cached locally after first download. Subsequent runs are much faster.

**Rate Limiting**: Serper API has rate limits. Consider implementing caching for production use.

## Environment Variables

- `SERPER_API_KEY`: **Required** - Get from [serper.dev](https://serper.dev)
- `DATABASE_URL`: Optional - SQLite database path (default: `./factcheck.db`)

## Tech Stack

- FastAPI + Uvicorn
- Transformers (DeBERTa, sentence-transformers)
- SQLite for caching and result storage
- httpx, trafilatura for web scraping
