import json
import logging
import re
from typing import Type, TypeVar, Optional, Dict, Any
import httpx
from pydantic import BaseModel, ValidationError

from ai.config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TIMEOUT, LLM_MAX_RETRIES

logger = logging.getLogger("kai.llm_client")
T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _clean_json_response(self, text: str) -> str:
        """Extract valid JSON from raw text output (handling markdown code fences, leading text, etc.)."""
        text = text.strip()
        # Remove markdown ```json ... ``` blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if json_match:
            return json_match.group(1).strip()
        
        # Search for first { or [ to last } or ]
        first_obj = text.find("{")
        first_arr = text.find("[")
        
        if first_obj != -1 and (first_arr == -1 or first_obj < first_arr):
            last_obj = text.rfind("}")
            if last_obj != -1:
                return text[first_obj:last_obj+1]
        elif first_arr != -1:
            last_arr = text.rfind("]")
            if last_arr != -1:
                return text[first_arr:last_arr+1]
                
        return text

    def generate_raw(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Call Ollama generate endpoint raw."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        
        try:
            with httpx.Client(timeout=LLM_TIMEOUT) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "")
                else:
                    logger.warning(f"Ollama returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Ollama connection error: {e}")
        return None

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        fallback_factory: Optional[Any] = None
    ) -> T:
        """
        Generate structured output matching a Pydantic schema.
        Handles extraction, repair, retries, and schema validation.
        Falls back gracefully if LLM is offline or returns invalid format.
        """
        prompt_with_schema = (
            f"{system_prompt}\n\n"
            f"You MUST output valid JSON matching this structure: {json.dumps(schema.model_json_schema())}\n"
            "Do NOT include conversational commentary, explanations, or intro text. Output JSON only."
        )

        for attempt in range(LLM_MAX_RETRIES + 1):
            current_user_prompt = user_prompt
            if attempt > 0:
                current_user_prompt += "\n\nCRITICAL: Previous response was not valid JSON matching the schema. Please return ONLY raw JSON."
            
            raw_output = self.generate_raw(prompt_with_schema, current_user_prompt)
            if raw_output:
                cleaned = self._clean_json_response(raw_output)
                try:
                    parsed_json = json.loads(cleaned)
                    validated_obj = schema.model_validate(parsed_json)
                    return validated_obj
                except (json.JSONDecodeError, ValidationError) as err:
                    logger.warning(f"Attempt {attempt + 1} validation failed: {err}")

        logger.warning("LLM generation failed or unavailable. Engaging fallback system.")
        if fallback_factory:
            if callable(fallback_factory):
                return fallback_factory()
            return fallback_factory
        
        raise RuntimeError(f"Could not generate structured response for schema {schema.__name__} and no fallback provided.")

# Singleton instance
default_llm_client = LLMClient()
