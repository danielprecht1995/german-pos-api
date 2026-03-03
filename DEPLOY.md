# Deploy so the API returns real POS tags (spaCy)

Render must use **Docker** for this app (Python 3.11 + spaCy). The default Python runtime uses 3.13 where spaCy does not install.

## Steps

1. Open [dashboard.render.com](https://dashboard.render.com) → your **german-pos-api** service.
2. Go to **Settings**.
3. Set **Environment** to **Docker** (not Python).
4. Set **Dockerfile Path** to `./Dockerfile`.
5. Save.
6. **Manual Deploy** → **Clear build cache & deploy**.

Wait for the build to finish (~3–5 min). Then `/health` should show `"spacy": true` and `/tag` will return real POS tags.
