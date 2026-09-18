"""MEMORA LLM client — OpenAI-compatible calls through the Hermes router at :31416."""
import json
import time
from typing import Any, Optional

import requests

from backend.config import (
    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL_FAST, LLM_MODEL_STRONG,
    LLM_MODEL_VISION, LLM_TIMEOUT_S,
)


class LLMError(Exception):
    pass


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }


def chat(
    messages: list[dict],
    model: str = "auto",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    tools: Optional[list[dict]] = None,
    timeout_s: Optional[float] = None,
) -> dict:
    """Call the LLM router. Returns the full response dict."""
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools

    url = f"{LLM_BASE_URL}/chat/completions"
    timeout = timeout_s or LLM_TIMEOUT_S

    for attempt in range(2):
        try:
            resp = requests.post(
                url, headers=_headers(), json=body, timeout=timeout
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                time.sleep(2)
                continue
            raise LLMError(f"LLM returned {resp.status_code}: {resp.text[:500]}")
        except requests.RequestException as e:
            if attempt == 0:
                time.sleep(2)
                continue
            raise LLMError(f"LLM request failed: {e}") from e

    raise LLMError("LLM exhausted retries")


def chat_json(
    messages: list[dict],
    model: str = "auto",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    timeout_s: Optional[float] = None,
) -> dict:
    """Call LLM and parse the response as JSON. Retries once with a fix-up prompt."""
    raw = chat(messages, model=model, temperature=temperature, max_tokens=max_tokens, timeout_s=timeout_s)
    content = _extract_content(raw)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise


def _extract_content(response: dict) -> str:
    try:
        return response["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError):
        return ""


def get_usage(response: dict) -> dict:
    return response.get("usage", {})


import re  # noqa: E402