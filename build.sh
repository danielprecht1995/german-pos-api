#!/usr/bin/env bash
# Build script for Render deployment

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy German model
python -m spacy download de_core_news_lg

# Download Stanza German model
python -c "import stanza; stanza.download('de')"

echo "Build completed successfully!"
