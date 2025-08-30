# AI For All - Fact Checker

A FastAPI application that takes claims and returns fact-checking results with sources, verdicts, and shareable posts.

## Features

- **Claim Analysis**: Submit claims for fact-checking
- **Multiple Search Providers**: Support for Google, Brave, and Serper APIs
- **AI-Powered Verification**: Uses transformer models for natural language inference
- **Source Extraction**: Automatically fetches and analyzes web content
- **Shareable Results**: Generate shareable links for fact-check results
- **REST API**: Clean JSON API for integration

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
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Test the health endpoint**:
   ```bash
   curl http://localhost:8000/healthz
   ```

## API Endpoints

- `POST /check` - Submit a claim for fact-checking
- `GET /r/{id}` - View shareable fact-check result
- `GET /healthz` - Health check endpoint

## Environment Variables

See `.env.example` for all required environment variables.

## Deployment

This application is designed to deploy on Railway. Set the required environment variables in your Railway project settings.

## Tech Stack

- FastAPI + Uvicorn
- Transformers (DeBERTa, sentence-transformers)
- SQLite for caching and result storage
- httpx, trafilatura for web scraping