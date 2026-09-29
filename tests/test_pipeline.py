from pathlib import Path
from typing import Any

from minuteguard.pipeline import MeetingAuditor
from minuteguard.providers import FixtureProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_offline_pipeline_is_reproducible(load_json: Any) -> None:
    source = (PROJECT_ROOT / "data" / "sample_meeting.txt").read_text(encoding="utf-8")
    provider = FixtureProvider([load_json("data/fixture_response.json")])

    result = MeetingAuditor(provider).audit(source, title="Réunion pilote Lyon")

    assert len(result.audit.decisions) == 2
    assert len(result.audit.actions) == 3
    assert result.grounded_items == 6
    assert result.rejected_items == 0
    assert len(result.source_sha256) == 64
    assert result.provider == "fixture"

