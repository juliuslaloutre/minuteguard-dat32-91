from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from minuteguard.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_demo_report_prompts_and_failure_lab(tmp_path: Path, capsys: Any) -> None:
    output = tmp_path / "audit.json"
    report = tmp_path / "audit.md"
    exit_code = main(
        [
            "audit",
            str(PROJECT_ROOT / "data" / "sample_meeting.txt"),
            "--title",
            "Réunion pilote Lyon",
            "--output",
            str(output),
            "--report",
            str(report),
        ]
    )

    assert exit_code == 0
    assert json.loads(output.read_text(encoding="utf-8"))["grounded_items"] == 6
    assert "Traçabilité technique" in report.read_text(encoding="utf-8")

    assert main(["prompts"]) == 0
    assert "few_shot" in capsys.readouterr().out
    assert main(["failure-lab", "--json"]) == 0
    catalog = json.loads(capsys.readouterr().out)
    assert {entry["name"] for entry in catalog} == {
        "hallucination",
        "sycophancy",
        "prompt_injection",
        "context_overflow",
    }


def test_cli_evaluate_and_fixture_benchmark(
    tmp_path: Path, capsys: Any, load_json: Any
) -> None:
    evaluation_path = tmp_path / "evaluation.json"
    assert main(["evaluate", "--output", str(evaluation_path)]) == 0
    assert json.loads(evaluation_path.read_text(encoding="utf-8"))["metrics"][
        "composite_score"
    ] == 1.0

    fixture_bundle = load_json("data/fixture_predictions.json")
    fixture_list = [entry["audit"] for entry in fixture_bundle["predictions"]]
    fixtures_path = tmp_path / "fixtures.json"
    fixtures_path.write_text(json.dumps(fixture_list, ensure_ascii=False), encoding="utf-8")
    predictions_path = tmp_path / "benchmark.json"
    assert (
        main(
            [
                "benchmark",
                "--provider",
                "fixture",
                "--fixture",
                str(fixtures_path),
                "--output",
                str(predictions_path),
            ]
        )
        == 0
    )
    generated = json.loads(predictions_path.read_text(encoding="utf-8"))
    assert len(generated["predictions"]) == 4
    assert generated["metadata"]["provider"] == "fixture"
    assert "Prédictions écrites" in capsys.readouterr().out


def test_cli_reports_missing_api_key(monkeypatch: Any, capsys: Any) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    exit_code = main(
        [
            "audit",
            str(PROJECT_ROOT / "data" / "sample_meeting.txt"),
            "--provider",
            "openai",
        ]
    )

    assert exit_code == 2
    assert "OPENAI_API_KEY is missing" in capsys.readouterr().err

