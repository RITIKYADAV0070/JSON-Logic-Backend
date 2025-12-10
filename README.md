#🧠 JSON Logic Rule Generator — Backend (FastAPI + OpenRouter + Embeddings + RAG)#

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

#🔗 Live API

👉 https://json-logic-backend.onrender.com

Root endpoint:

.GET /


Response:

{ "status": "ok", "message": "JSON Logic Rule Generator API" }


Generate rule:

POST /generate-rule

🛠 Tech Stack

Python 3.10+

FastAPI

Uvicorn

Requests

OpenRouter API

Embeddings (text-embedding-3-small)

Vercel + Render compatible

📦 Setup Instructions
1️⃣ Clone repository
git clone https://github.com/RITIKYADAV0070/JSON-Logic-Backend
cd JSON-Logic-Backend

2️⃣ Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create .env file
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small
CORS_ORIGINS=["*"]

5️⃣ Start server
uvicorn app.main:app --reload --port 8001

📚 API Example Request
{
  "prompt": "Approve if bureau score > 700 and customer age > 25",
  "context_docs": [
    "Credit policy v1.0 — minimum bureau score 600...",
    "Income rules — high risk if FOIR > 0.6..."
  ]
}


Response includes:

JSON Logic

Explanation

Used keys

Embedding mappings + similarity

Policy snippets (RAG)

Raw JSON output

🚀 Deployment

This backend runs on:

Render (live deployment)

Supports Vercel / Railway / Docker deployments

Automatically loads .env for OpenRouter API keys

📄 License

MIT

✅ README for Frontend (JSON-Logic-Frontend)

Copy–paste this into JSON-Logic-Frontend/README.md

🎨 JSON Logic Rule Generator — Frontend (React + Vite + Tailwind + Vercel)

This is the UI for the JSON Logic Rule Generator, where users can:

✔ Enter a natural-language policy
✔ Add optional context documents
✔ Generate JSON Logic using backend API
✔ View explanation, key mappings, RAG snippets
✔ Switch between Summary + Raw JSON
✔ Toggle Dark Mode

🔗 Live Frontend

👉 https://json-logic-frontend.vercel.app

Backend used:
👉 https://json-logic-backend.onrender.com

🛠 Tech Stack

React (Vite)

TailwindCSS

Lucide Icons

Axios

Framer Motion

Dark Mode with localStorage

Deployed on Vercel

📁 Project Structure
src/
 ├── components/
 ├── App.jsx
 ├── main.jsx
 ├── index.css
public/
vite.config.js
postcss.config.js

⚙️ Environment Variables

Create .env in the root:

VITE_API_URL=https://json-logic-backend.onrender.com


(The deployed version on Vercel already uses this.)

🚀 Running the Frontend
1️⃣ Clone repository
git clone https://github.com/RITIKYADAV0070/JSON-Logic-Frontend
cd JSON-Logic-Frontend

2️⃣ Install packages
npm install

3️⃣ Start dev server
npm run dev


Frontend runs on:

http://localhost:5173

📡 API Call Example
const API_BASE_URL = import.meta.env.VITE_API_URL;

const res = await axios.post(`${API_BASE_URL}/generate-rule`, {
    prompt,
    context_docs,
});

🖼 Screenshots

(Add screenshots of:
✔ Rule builder
✔ Summary
✔ Raw JSON
✔ Dark mode view)

🚀 Deployment (Vercel)

1️⃣ Connect GitHub repo
2️⃣ Add Environment Variable

VITE_API_URL=https://json-logic-backend.onrender.com


3️⃣ Deploy

🧑‍💻 Built By

Ritik Yadav
AI Developer Assignment — Crego
