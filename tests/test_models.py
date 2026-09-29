import pytest
from pydantic import ValidationError

from minuteguard.models import Action, Evidence


def test_due_date_must_be_a_real_iso_date() -> None:
    with pytest.raises(ValidationError):
        Action(
            id="A1",
            task="Tester",
            owner=None,
            due_date="2026-02-31",
            status="confirmed",
            evidence=Evidence(quote="Tester", line_start=1, line_end=1),
        )


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Evidence(quote="Texte", line_start=1, line_end=1, invented=True)  # type: ignore[call-arg]

