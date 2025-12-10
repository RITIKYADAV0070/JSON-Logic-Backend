
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class GenerateRuleRequest(BaseModel):
    prompt: str
    context_docs: Optional[List[str]] = None


class KeyMapping(BaseModel):
    user_phrase: str
    mapped_to: str
    similarity: float


class GenerateRuleResponse(BaseModel):
    json_logic: Dict[str, Any]
    explanation: str
    used_keys: List[str]
    key_mappings: List[KeyMapping]
    confidence_score: float
    retrieved_policy_snippets: List[str]
