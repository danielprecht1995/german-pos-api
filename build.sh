#!/usr/bin/env bash
# Install deps only (no spacy/stanza on Python 3.13 — app uses fallback tokenizer)
set -e
pip install --upgrade pip
pip install -r requirements.txt
echo "Build completed!"
