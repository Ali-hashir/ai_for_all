FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps: keep minimal (wheels cover lxml/torch on linux x86_64)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# Set cache paths for faster cold starts on Spaces
ENV HF_HOME=/tmp/.huggingface \
    TRANSFORMERS_CACHE=/tmp/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers

# Spaces expect port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
