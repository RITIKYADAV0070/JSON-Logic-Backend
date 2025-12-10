
import requests
import numpy as np
from typing import List
from .config import get_settings

settings = get_settings()

EMBEDDING_URL = "https://openrouter.ai/api/v1/embeddings"


def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 1), dtype="float32")

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.openrouter_embedding_model,
        "input": texts,
    }

    resp = requests.post(EMBEDDING_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    vectors = [d["embedding"] for d in data["data"]]
    return np.array(vectors, dtype="float32")


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if a.size == 0 or b.size == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype="float32")
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
    return a_norm @ b_norm.T
