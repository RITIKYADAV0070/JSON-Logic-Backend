
# JSON Logic Rule Generator — Backend (FastAPI + OpenRouter)

This service exposes a single endpoint `/generate-rule` that:

- Takes a natural-language prompt describing a credit rule
- Uses embeddings (OpenRouter) to map phrases to allowed SAMPLE_STORE_KEYS
- Optionally uses simple RAG over a few hard-coded policy snippets
- Calls an LLM via OpenRouter to synthesise:
  - `json_logic` (machine-readable rule)
  - `explanation` (plain English)
  - `used_keys` (which SAMPLE_STORE_KEYS were used)
  - `key_mappings` (phrase → key similarity)
  - `confidence_score`
  - `retrieved_policy_snippets`

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env
# edit .env and put your OPENROUTER_API_KEY

uvicorn app.main:app --reload --port 8001
```

Then open: http://127.0.0.1:8001/docs
