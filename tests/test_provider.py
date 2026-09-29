from types import SimpleNamespace
from typing import Any

from minuteguard.providers import OpenAIProvider


class FakeTransientError(Exception):
    pass


class FakeResponses:
    def __init__(self) -> None:
        self.calls = 0
        self.kwargs: dict[str, Any] = {}

    def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls += 1
        self.kwargs = kwargs
        if self.calls == 1:
            raise FakeTransientError("temporary")
        return SimpleNamespace(output_text='{"ok": true}')


def test_provider_retries_once_and_uses_strict_json_schema() -> None:
    responses = FakeResponses()
    sleeps: list[float] = []
    client = SimpleNamespace(responses=responses)
    provider = OpenAIProvider(
        model="test-model",
        client=client,
        max_attempts=2,
        sleeper=sleeps.append,
        jitter=lambda _start, _end: 0.0,
    )
    provider._retryable_errors = (FakeTransientError,)  # type: ignore[assignment]

    output = provider.complete(
        system_prompt="system",
        user_prompt="user",
        json_schema={"type": "object", "properties": {}, "additionalProperties": False},
    )

    assert output == '{"ok": true}'
    assert responses.calls == 2
    assert sleeps == [1.0]
    assert responses.kwargs["instructions"] == "system"
    assert responses.kwargs["temperature"] == 0
    assert responses.kwargs["text"]["format"]["strict"] is True

