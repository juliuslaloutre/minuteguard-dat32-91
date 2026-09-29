from pathlib import Path
from typing import Any

import pytest

from minuteguard.chunking import split_text
from minuteguard.pipeline import MeetingAuditor, _git_metadata, _prompt_sha256
from minuteguard.prompts import PromptRepository, number_lines
from minuteguard.providers import FixtureProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_offline_pipeline_is_reproducible(
    load_json: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = (PROJECT_ROOT / "data" / "sample_meeting.txt").read_text(encoding="utf-8")
    provider = FixtureProvider([load_json("data/fixture_response.json")])
    monkeypatch.setattr(
        "minuteguard.pipeline._git_metadata", lambda: ("a" * 40, True)
    )

    result = MeetingAuditor(provider).audit(source, title="Réunion pilote Lyon")
    chunk = split_text(source)[0]
    bundle = PromptRepository(PROJECT_ROOT / "prompts").load(
        "few_shot",
        title="Réunion pilote Lyon",
        numbered_source=number_lines(chunk.text, first_line=chunk.first_line),
    )

    assert len(result.audit.decisions) == 2
    assert len(result.audit.actions) == 3
    assert result.grounded_items == 6
    assert result.rejected_items == 0
    assert len(result.source_sha256) == 64
    assert result.prompt_sha256 == _prompt_sha256([(bundle.system, bundle.user)])
    assert result.git_commit == "a" * 40
    assert result.git_dirty is True
    assert result.provider == "fixture"


def test_prompt_sha256_is_stable_and_role_sensitive() -> None:
    assert _prompt_sha256([("system", "user")]) == (
        "5cc6b05780cc75028e0cb34ea607093b9d13af9a2d147f7ec927a5bdb3303858"
    )
    assert _prompt_sha256([("system", "user")]) != _prompt_sha256([("user", "system")])


def test_git_metadata_is_null_outside_repository(tmp_path: Path) -> None:
    assert _git_metadata(tmp_path) == (None, None)
