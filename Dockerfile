# Python 3.11 has prebuilt wheels for spacy/blis — use this for the API
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# App deps (no spacy in base requirements for native Render; we add it here)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy and German model (works on 3.11)
RUN pip install --no-cache-dir spacy==3.7.2 && python -m spacy download de_core_news_sm

# App code
COPY german_pos_api.py app.py Procfile ./

# Render sets PORT at runtime
EXPOSE 8000
ENV PORT=8000
# Shell form so $PORT is expanded at runtime
CMD uvicorn german_pos_api:app --host 0.0.0.0 --port $PORT
