
import json
import re
from typing import List, Tuple, Dict, Any

import numpy as np
import requests

from .config import get_settings
from .embeddings import embed_texts, cosine_sim_matrix
from .sample_keys import SAMPLE_STORE_KEYS

settings = get_settings()

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


class JSONLogicGenerator:
    def __init__(self) -> None:
        # Pre-compute embeddings for store keys
        self.keys = SAMPLE_STORE_KEYS
        key_texts = [
            f"{k['label']} ({k['value']}) in group {k['group']}"
            for k in self.keys
        ]
        self.key_embeddings = embed_texts(key_texts)

        # Simple built-in policy docs for RAG flavour
        self.policy_docs = [
            """Credit Policy v1.0
- Minimum bureau score for approval should normally be 600 or above.
- Applicants with bureau score below 550 should usually be rejected.
- Overdue amount greater than 50,000 should be treated as high risk.
""",
            """Income Policy v1.0
- FOIR should ideally be below 0.6 (60%).
- Debt to income ratio above 0.8 is considered high risk.
- Monthly income above 100,000 may qualify for premium offers.
""",
        ]
        self.policy_embeddings = embed_texts(self.policy_docs)

    # ---------- PHRASE + KEY MAPPING ----------

    def _extract_phrases(self, prompt: str) -> List[str]:
        # Split on and/or/comma/period
        chunks = re.split(r"\band\b|\bor\b|,|\.", prompt, flags=re.IGNORECASE)
        phrases = []
        for ch in chunks:
            phrase = ch.strip()
            if len(phrase) >= 4:
                phrases.append(phrase)
        # If nothing, fall back to whole prompt
        return phrases or [prompt.strip()]

    def map_phrases_to_keys(
        self, prompt: str
    ) -> Tuple[List[Dict[str, Any]], float, List[str]]:
        phrases = self._extract_phrases(prompt)
        phrase_embs = embed_texts(phrases)

        sim = cosine_sim_matrix(phrase_embs, self.key_embeddings)  # [P, K]
        key_mappings: List[Dict[str, Any]] = []
        candidate_keys: List[str] = []
        max_sim = 0.0

        for i, phrase in enumerate(phrases):
            # top-3 keys for transparency
            sims = sim[i]
            top_idx = np.argsort(-sims)[:3]
            for idx in top_idx:
                key = self.keys[idx]["value"]
                s = float(sims[idx])
                key_mappings.append(
                    {
                        "user_phrase": phrase,
                        "mapped_to": key,
                        "similarity": s,
                    }
                )
                max_sim = max(max_sim, s)

        # dedupe candidate keys above relaxed threshold
        RELAXED_THRESHOLD = 0.30
        for km in key_mappings:
            if km["similarity"] >= RELAXED_THRESHOLD and km["mapped_to"] not in candidate_keys:
                candidate_keys.append(km["mapped_to"])

        # sort mappings by similarity desc
        key_mappings.sort(key=lambda x: x["similarity"], reverse=True)
        return key_mappings, max_sim, candidate_keys

    # ---------- POLICY RAG ----------

    def retrieve_policy_snippets(self, prompt: str, extra_docs: List[str]) -> List[str]:
        all_docs = list(self.policy_docs)
        if extra_docs:
            all_docs.extend(extra_docs)

        base_embs = self.policy_embeddings
        extra_embs = embed_texts(extra_docs) if extra_docs else np.zeros((0, 1))
        if extra_docs:
            policy_embs = np.vstack([base_embs, extra_embs])
        else:
            policy_embs = base_embs

        prompt_emb = embed_texts([prompt])
        sim = cosine_sim_matrix(prompt_emb, policy_embs)[0]  # [N]
        top_idx = np.argsort(-sim)[: min(3, len(all_docs))]
        return [all_docs[i] for i in top_idx]

    # ---------- LLM CALL ----------

    def _call_llm(
        self,
        prompt: str,
        candidate_keys: List[str],
        policy_snippets: List[str],
    ) -> Dict[str, Any]:
        allowed_keys_block = "\n".join(
            [f"- {k['label']} → {k['value']}" for k in self.keys]
        )

        system_msg = (
            "You are a credit risk rules engineer. "
            "You take natural language policy descriptions and convert them into JSON Logic. "
            "You MUST only use the allowed keys under the 'var' operator."
        )

        user_content = f"""You are given:

1) A user prompt describing a credit policy.
2) A list of allowed JSON fields (SAMPLE_STORE_KEYS).
3) A small set of policy snippets (RAG context).
4) A small set of candidate keys that embeddings think are most relevant.

TASK:

- Produce a JSON object with EXACTLY these top-level keys:
  - "json_logic": a valid JSON Logic rule object
  - "explanation": 1–3 sentences explaining the rule in plain English
  - "used_keys": array of strings of the fields actually used in json_logic

RULES:

- "json_logic" must be valid JSON Logic.
- Use operators like "and", "or", ">", ">=", "<", "<=", "==", "in".
- Under each "var" use ONLY field names from SAMPLE_STORE_KEYS.
- Prefer to use the candidate keys when relevant, but do not force them if they don't make sense.
- Be deterministic and conservative: do not invent extra conditions.

SAMPLE_STORE_KEYS:
{allowed_keys_block}

Candidate keys suggested by embeddings:
{json.dumps(candidate_keys, indent=2)}

Policy snippets (may influence thresholds and decisions):
{json.dumps(policy_snippets, indent=2)}

User prompt:
{prompt}

Now respond ONLY with a JSON object having keys: "json_logic", "explanation", "used_keys".
"""  # noqa: E501

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
        }

        resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        # content should be JSON; attempt to parse
        # sometimes models wrap in ```json ... ```
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```[a-zA-Z]*", "", content)
            content = content.strip("`\n ")

        parsed = json.loads(content)
        return parsed

    # ---------- PUBLIC API ----------

    def generate(self, prompt: str, context_docs: List[str]) -> Dict[str, Any]:
        key_mappings, max_sim, candidate_keys = self.map_phrases_to_keys(prompt)

        STRICT_THRESHOLD = 0.15  # keep it low so examples always work
        if max_sim < STRICT_THRESHOLD or not candidate_keys:
            # no reasonable mapping
            raise ValueError(
                json.dumps(
                    {
                        "error": "Prompt concepts do not map cleanly to available fields.",
                        "detail": "None of the allowed keys matched the prompt with sufficient similarity.",
                        "top_suggestions": key_mappings[:3],
                    }
                )
            )

        policy_snippets = self.retrieve_policy_snippets(prompt, context_docs)

        llm_obj = self._call_llm(prompt, candidate_keys, policy_snippets)

        json_logic = llm_obj.get("json_logic")
        explanation = llm_obj.get("explanation", "")
        used_keys = llm_obj.get("used_keys", [])

        # simple confidence heuristic: average of top-3 sims
        top_sims = [km["similarity"] for km in key_mappings[:3]]
        confidence = float(sum(top_sims) / len(top_sims)) if top_sims else 0.0

        return {
            "json_logic": json_logic,
            "explanation": explanation,
            "used_keys": used_keys,
            "key_mappings": key_mappings,
            "confidence_score": confidence,
            "retrieved_policy_snippets": policy_snippets,
        }
