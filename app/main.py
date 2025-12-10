from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .config import get_settings
from .json_logic_generator import JSONLogicGenerator
from .schemas import GenerateRuleRequest, GenerateRuleResponse

settings = get_settings()
generator = JSONLogicGenerator()

app = FastAPI(
    title="JSON Logic Rule Generator",
    description="Natural language → JSON Logic using embeddings + OpenRouter",
    version="1.0.0",
)

# FIXED CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://json-logic-frontend-git-main-ritik-yadavs-projects-ddbd3c9f.vercel.app",
        "https://json-logic-frontend.vercel.app",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "JSON Logic Rule Generator API"}


@app.post("/generate-rule", response_model=GenerateRuleResponse)
def generate_rule(payload: GenerateRuleRequest):
    try:
        ctx_docs: List[str] = payload.context_docs or []
        result = generator.generate(payload.prompt, ctx_docs)
        return result

    except ValueError as ve:
        try:
            detail = ve.args[0]
        except IndexError:
            detail = str(ve)
        raise HTTPException(status_code=422, detail=detail)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
