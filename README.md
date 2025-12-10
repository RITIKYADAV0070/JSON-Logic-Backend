# 🧠 JSON Logic Rule Generator — Backend (FastAPI + OpenRouter + Embeddings + RAG)

This backend powers the JSON Logic Rule Generator, converting natural-language credit policies into JSON Logic using:

🔹 FastAPI

🔹 OpenRouter (LLM inference)

🔹 Embeddings for key-to-phrase mapping

🔹 Lightweight RAG (retrieves internal policy snippets)

It receives a prompt + optional context documents, runs LLM-based parsing + mapping, and returns:

JSON Logic

Explanation

Key mappings (embedding similarities)

Policy RAG output

# 🔗 Live API

👉 https://json-logic-backend.onrender.com

Root endpoint:
~~~
.GET /
~~~

Response:
~~~
{ "status": "ok", "message": "JSON Logic Rule Generator API" }
~~~

Generate rule:
~~~
POST /generate-rule
~~~
# 🛠 Tech Stack

Python 3.10+

FastAPI

Uvicorn

Requests

OpenRouter API

Embeddings (text-embedding-3-small)

Vercel + Render compatible

# 📦 Setup Instructions
1️⃣ Clone repository
~~~
git clone https://github.com/RITIKYADAV0070/JSON-Logic-Backend
cd JSON-Logic-Backend
~~~
2️⃣ Create virtual environment
~~~
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
~~~
3️⃣ Install dependencies
~~~
pip install -r requirements.txt
~~~
4️⃣ Create .env file
~~~
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small
CORS_ORIGINS=["*"]
~~~
5️⃣ Start server
~~~
uvicorn app.main:app --reload --port 8001
~~~
📚 API Example Request
~~~
{
  "prompt": "Approve if bureau score > 700 and customer age > 25",
  "context_docs": [
    "Credit policy v1.0 — minimum bureau score 600...",
    "Income rules — high risk if FOIR > 0.6..."
  ]
}
~~~

Response includes:

JSON Logic

Explanation

Used keys

Embedding mappings + similarity

Policy snippets (RAG)

Raw JSON output

$ 🚀 Deployment

This backend runs on:

Render (live deployment)

Supports Vercel / Railway / Docker deployments

Automatically loads .env for OpenRouter API keys

