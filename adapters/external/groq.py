"""
External API Adapter - OpenAI-compatible LLM client (Groq / Omniroute / etc.)

Uses httpx directly so it works with any OpenAI-compatible /v1/chat/completions
endpoint (Groq, Omniroute, Ollama, etc.) without SDK path quirks.
"""
import json
import os
from types import SimpleNamespace
from typing import Optional

import httpx


def _obj(data):
    """Recursively convert dicts to attribute-access objects."""
    if isinstance(data, dict):
        return SimpleNamespace(**{k: _obj(v) for k, v in data.items()})
    if isinstance(data, list):
        return [_obj(v) for v in data]
    return data


def _stream_chunks(response):
    """Yield SSE chunks as objects compatible with Groq/OpenAI streaming."""
    for line in response.iter_lines():
        if not line:
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
        if not line or line == "[DONE]":
            continue
        try:
            yield _obj(json.loads(line))
        except Exception:
            continue


class GroqAdapter:
    """Adapter para comunicación con APIs OpenAI-compatible (Groq, Omniroute, etc.)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
        raw_base = base_url or os.getenv("LLM_BASE_URL") or "https://api.groq.com/openai/v1"
        self.base_url = raw_base.rstrip("/")
        self.default_model = (
            default_model
            or os.getenv("LLM_MODEL")
            or os.getenv("MODEL_NAME")
            or "llama-3.3-70b-versatile"
        )

        if not self.api_key:
            raise ValueError("Missing API key! Set LLM_API_KEY (or GROQ_API_KEY) in .env.")

        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat_complete(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.9,
        max_tokens: int = 512,
        stream: bool = False,
    ):
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        reasoning_effort = os.getenv("LLM_REASONING_EFFORT")
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort
        url = f"{self.base_url}/chat/completions"
        if stream:
            client = httpx.Client(timeout=90.0)
            req = client.build_request("POST", url, headers=self._headers, json=payload)
            resp = client.send(req, stream=True)
            resp.raise_for_status()

            def gen():
                try:
                    yield from _stream_chunks(resp)
                finally:
                    resp.close()
                    client.close()

            return gen()
        else:
            resp = httpx.post(url, headers=self._headers, json=payload, timeout=90.0)
            resp.raise_for_status()
            return _obj(resp.json())

    def extract_memories(self, prompt: str) -> list:
        resp = self.chat_complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.default_model,
            temperature=0.3,
            max_tokens=150,
            stream=False,
        )
        content = (getattr(resp.choices[0].message, "content", None) or "").strip()
        if content.lower() == "nada":
            return []
        return [h.strip() for h in content.split("|||") if h.strip()]
