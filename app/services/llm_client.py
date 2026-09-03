import json
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings


class LLMGenerationError(RuntimeError):
    pass


class BaseLLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def _raw_generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def generate_json(self, system_prompt: str, user_prompt: str, response_model: type[BaseModel]) -> BaseModel:
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                raw = self._raw_generate(system_prompt, user_prompt)
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.S)
                payload = json.loads(cleaned)
                return response_model.model_validate(payload)
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                last_error = exc
                user_prompt = (
                    f"{user_prompt}\n\nPrevious response failed validation. "
                    f"Please return valid JSON matching the schema exactly. "
                    f"Error: {exc}"
                )

        if last_error is not None:
            raise LLMGenerationError(f"LLM generation failed after retries: {last_error}")
        raise LLMGenerationError("LLM generation failed without a detailed error.")


class GroqProvider(BaseLLMProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str):
        from groq import Groq

        self.client = Groq(api_key=api_key)
        self.model = model

    def _raw_generate(self, system_prompt: str, user_prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content or "{}"


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _raw_generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )
        return getattr(response, "text", "{}")


class OllamaProvider(BaseLLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _raw_generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }
        response = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "{}")


def get_llm_provider() -> BaseLLMProvider:
    provider_name = settings.llm_provider.lower()

    if provider_name == "groq":
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is missing or empty.")
        return GroqProvider(settings.groq_api_key, settings.groq_model)

    if provider_name == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is missing or empty.")
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)

    if provider_name == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model)

    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")
