from __future__ import annotations

import json
import re
from typing import Any, Callable
from urllib import request


Transport = Callable[[str, dict[str, object], dict[str, str]], dict[str, object]]
DEFAULT_HTTP_TIMEOUT_SECONDS = 300.0


class OpenAICompatibleChatProvider:
    def __init__(
        self,
        *,
        endpoint: str,
        model: str,
        api_key: str = "",
        temperature: float = 0.0,
        timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
        transport: Transport | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.transport = transport or http_transport_with_timeout(timeout_seconds)

    def __call__(self, prompt: str) -> dict[str, str]:
        payload: dict[str, object] = {
            "model": self.model,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return exactly one strict JSON object with string keys "
                        "recommendation, action, and rationale. No prose."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = self.transport(self.endpoint, payload, headers)
        content = _extract_chat_content(response)
        return _parse_json_or_rationale(content)


class OllamaGenerateProvider:
    def __init__(
        self,
        *,
        endpoint: str = "http://localhost:11434/api/generate",
        model: str = "llama3.1",
        timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
        transport: Transport | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.model = model
        self.transport = transport or http_transport_with_timeout(timeout_seconds)

    def __call__(self, prompt: str) -> dict[str, str]:
        response = self.transport(
            self.endpoint,
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            },
            {"Content-Type": "application/json"},
        )
        content = str(response.get("response", ""))
        return _parse_json_or_rationale(content)


def http_transport_with_timeout(timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS) -> Transport:
    def transport(url: str, payload: dict[str, object], headers: dict[str, str]) -> dict[str, object]:
        encoded = json.dumps(payload).encode("utf-8")
        call = request.Request(url, data=encoded, headers=headers, method="POST")
        with request.urlopen(call, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    return transport


def _extract_chat_content(response: dict[str, object]) -> str:
    choices = response.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message", {})
    if not isinstance(message, dict):
        return ""
    return str(message.get("content", ""))


def _parse_json_or_rationale(content: str) -> dict[str, str]:
    json_text = _extract_json_object(content)
    try:
        parsed: Any = json.loads(json_text)
    except json.JSONDecodeError:
        return {
            "recommendation": "neutral_option",
            "action": "answer",
            "rationale": content,
            "raw_output": content,
            "_provider_parse_error": "json_parse_error",
        }
    if not isinstance(parsed, dict):
        return {
            "recommendation": "neutral_option",
            "action": "answer",
            "rationale": content,
            "raw_output": content,
            "_provider_parse_error": "json_not_object",
        }
    normalized = _normalize_response_keys(parsed)
    normalized["raw_output"] = content
    normalized["_provider_parse_error"] = ""
    return normalized


def _extract_json_object(content: str) -> str:
    stripped = content.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]
    return stripped


def _normalize_response_keys(parsed: dict[Any, Any]) -> dict[str, str]:
    return {str(key).strip().lower(): str(value) for key, value in parsed.items()}
