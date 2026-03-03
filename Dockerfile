# Use Python 3.11 so spaCy installs from wheels (no build from source)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install de_core_news_sm via wheel (spacy download can 404 in Docker)
RUN pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.7.0/de_core_news_sm-3.7.0-py3-none-any.whl

COPY german_pos_api.py app.py Procfile ./

EXPOSE 8000
ENV PORT=8000
# Shell form so $PORT is expanded when the container runs (Render sets PORT)
CMD uvicorn german_pos_api:app --host 0.0.0.0 --port $PORT
