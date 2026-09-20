"""MEMORA LLM client — NVIDIA NIM API (OpenAI-compatible)

Supports both standard and reasoning models via NVIDIA's API.
"""
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
    model: str = "nvidia/nemotron-3.5-lightning-30b-a3b",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    tools: Optional[list[dict]] = None,
    timeout_s: Optional[float] = None,
    thinking: bool = False,
) -> dict:
    """Call the NVIDIA NIM API. Returns the full response dict."""
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

    for attempt in range(3):
        try:
            resp = requests.post(
                url, headers=_headers(), json=body, timeout=timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                # Clean up reasoning_content if present
                if "choices" in data and data["choices"]:
                    msg = data["choices"][0].get("message", {})
                    if "reasoning_content" in msg:
                        msg.pop("reasoning_content", None)
                return data
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            raise LLMError(f"LLM returned {resp.status_code}: {resp.text[:500]}")
        except requests.RequestException as e:
            if attempt < 2:
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


def list_models() -> list[dict]:
    """List available models from NVIDIA NIM API."""
    url = f"{LLM_BASE_URL}/models"
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except:
        pass
    return []


def get_model_info() -> dict:
    """Get information about the configured model."""
    models = list_models()
    current = next((m for m in models if m.get("id") == LLM_MODEL_FAST), None)
    return {
        "base_url": LLM_BASE_URL,
        "current_model": LLM_MODEL_FAST,
        "available_models": [m.get("id") for m in models[:10]],
        "model_info": current,
    }


import re  # noqa: E402