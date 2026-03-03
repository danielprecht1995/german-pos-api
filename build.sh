#!/usr/bin/env bash
set -e
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download de_core_news_sm
echo "Build completed!"
