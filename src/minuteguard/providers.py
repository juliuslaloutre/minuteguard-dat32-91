"""LLM provider adapters with explicit, testable retry behavior."""

from __future__ import annotations

import json
import random
import time
from collections.abc import Callable, Sequence
from typing import Any, Protocol


class TextProvider(Protocol):
    provider_name: str
    model_name: str

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
    ) -> str: ...


class FixtureProvider:
    """Deterministic provider for demos and tests; never calls a network."""

    provider_name = "fixture"
    model_name = "recorded-fixture-v1"

    def __init__(self, responses: Sequence[dict[str, Any] | str]) -> None:
        if not responses:
            raise ValueError("FixtureProvider needs at least one response")
        self._responses = list(responses)
        self._index = 0

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
    ) -> str:
        del system_prompt, user_prompt, json_schema
        if self._index >= len(self._responses):
            raise RuntimeError("No fixture response remains for this request")
        response = self._responses[self._index]
        self._index += 1
        return response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)


class OpenAIProvider:
    """Responses API adapter with bounded exponential backoff and jitter.

    SDK retries are disabled so attempts are not multiplied by nested retry
    loops. Transient 429, 5xx, connection, and timeout errors are retried.
    Authentication, quota, billing, and validation errors fail immediately.
    """

    provider_name = "openai"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        max_attempts: int = 4,
        max_delay: float = 20.0,
        timeout: float = 60.0,
        sleeper: Callable[[float], None] = time.sleep,
        jitter: Callable[[float, float], float] = random.uniform,
        client: Any | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.model_name = model
        self.max_attempts = max_attempts
        self.max_delay = max_delay
        self._sleep = sleeper
        self._jitter = jitter

        try:
            from openai import (
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                OpenAI,
                RateLimitError,
            )
        except ImportError as exc:  # pragma: no cover - depends on optional environment
            raise RuntimeError("Install the project first with: pip install -e .") from exc

        self._retryable_errors = (
            RateLimitError,
            InternalServerError,
            APIConnectionError,
            APITimeoutError,
        )
        self._client = client or OpenAI(api_key=api_key, max_retries=0, timeout=timeout)

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
    ) -> str:
        for attempt in range(self.max_attempts):
            try:
                response = self._client.responses.create(
                    model=self.model_name,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "meeting_audit",
                            "strict": True,
                            "schema": json_schema,
                        }
                    },
                )
                return str(response.output_text)
            except self._retryable_errors as exc:
                if attempt + 1 >= self.max_attempts:
                    raise
                delay = self._retry_delay(exc, attempt)
                self._sleep(delay)
        raise AssertionError("unreachable")

    def _retry_delay(self, exc: Exception, attempt: int) -> float:
        headers = getattr(getattr(exc, "response", None), "headers", {}) or {}
        raw_retry_after = headers.get("retry-after") or headers.get("Retry-After")
        if raw_retry_after is not None:
            try:
                server_delay = float(raw_retry_after)
            except (TypeError, ValueError):
                server_delay = -1.0
            if server_delay > self.max_delay:
                raise RuntimeError(
                    f"Server requested Retry-After={server_delay}s, above configured limit"
                ) from exc
            if server_delay >= 0:
                return server_delay + self._jitter(0.0, 0.25)

        exponential = min(self.max_delay, 2.0**attempt)
        return exponential + self._jitter(0.0, 0.25)

