"""
German POS Tagger API — Commercial-Safe
----------------------------------------
Primary: spaCy (MIT license)
Backup:  Stanza (Apache 2.0 license)
Both are free for commercial use.

How to run:
1. Install dependencies:
   pip install fastapi uvicorn spacy stanza

2. Download models (one-time):
   python -m spacy download de_core_news_lg
   python -c "import stanza; stanza.download('de')"

3. Run the server:
   uvicorn german_pos_api:app --host 0.0.0.0 --port 8080

API endpoints:
- GET  /health
- POST /tag  { "text": "...", "splitSentences": true, "includeLemma": true, "includeMorph": true }
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os

# ---------- Load Primary: spaCy (optional, no wheel on Python 3.13) ----------
nlp_spacy = None
SPACY_MODEL = os.getenv("SPACY_MODEL", "de_core_news_sm")
try:
    import spacy
    nlp_spacy = spacy.load(SPACY_MODEL)
    print(f"[OK] spaCy model '{SPACY_MODEL}' loaded")
except Exception as e:
    print(f"[WARN] spaCy not available: {e}")

# ---------- Load Backup: Stanza (optional) ----------
STANZA_LANG = "de"
nlp_stanza = None
try:
    import stanza
    stanza.download(STANZA_LANG, processors="tokenize,pos,lemma,mwt", verbose=False)
    nlp_stanza = stanza.Pipeline(
        lang=STANZA_LANG,
        processors="tokenize,pos,lemma,mwt",
        tokenize_pretokenized=False
    )
    print("[OK] Stanza loaded")
except Exception as e:
    print(f"[WARN] Stanza not available: {e}")

# ---------- FastAPI App ----------
app = FastAPI(title="German POS API", version="1.0.0")

class TagRequest(BaseModel):
    text: str
    splitSentences: bool = True
    includeLemma: bool = True
    includeMorph: bool = True

# ---------- Utility functions ----------
def spacy_to_tokens(doc, include_lemma: bool, include_morph: bool):
    sentences = []
    for sent in doc.sents:
        toks = []
        for t in sent:
            if t.is_space:
                continue
            morph: Dict[str, Any] = {}
            if include_morph:
                try:
                    morph = {k: v for k, v in t.morph.to_dict().items()}
                except Exception:
                    morph = {}
            toks.append({
                "text": t.text,
                "pos": t.pos_,
                "lemma": t.lemma_ if include_lemma else None,
                "morph": morph
            })
        sentences.append({"tokens": toks})
    return sentences

def stanza_to_tokens(doc, include_lemma: bool, include_morph: bool):
    sentences = []
    for s in doc.sentences:
        toks = []
        for w in s.words:
            if not w.text.strip():
                continue
            feats = {}
            if include_morph and w.feats:
                feats = {kv.split("=")[0]: kv.split("=")[1] for kv in w.feats.split("|") if "=" in kv}
            toks.append({
                "text": w.text,
                "pos": w.upos,
                "lemma": w.lemma if include_lemma else None,
                "morph": feats
            })
        sentences.append({"tokens": toks})
    return sentences

# ---------- Routes ----------
@app.get("/health")
def health():
    return {
        "ok": bool(nlp_spacy or nlp_stanza),
        "providers": {
            "spacy": bool(nlp_spacy),
            "stanza": bool(nlp_stanza)
        }
    }

@app.post("/tag")
def tag(req: TagRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    # Try spaCy first
    if nlp_spacy:
        try:
            doc = nlp_spacy(text)
            sents = spacy_to_tokens(doc, req.includeLemma, req.includeMorph)
            return {"model": SPACY_MODEL, "transformer": False, "sentences": sents}
        except Exception as e:
            print(f"[ERR] spaCy failed: {e}")

    # Fallback to Stanza
    if nlp_stanza:
        try:
            doc = nlp_stanza(text)
            sents = stanza_to_tokens(doc, req.includeLemma, req.includeMorph)
            return {"model": f"stanza-{STANZA_LANG}", "transformer": True, "sentences": sents}
        except Exception as e:
            print(f"[ERR] Stanza failed: {e}")

    # No NLP libs: return basic tokenization so the app still works
    tokens = [{"text": w, "pos": "X", "lemma": w.lower() if req.includeLemma else None, "morph": {}}
              for w in text.split() if w.strip()]
    return {"model": "fallback", "transformer": False, "sentences": [{"tokens": tokens}]}
