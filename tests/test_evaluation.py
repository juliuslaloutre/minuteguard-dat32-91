from typing import Any

from minuteguard.evaluation import evaluate_predictions


def test_curated_fixture_reaches_perfect_reference_score(load_json: Any) -> None:
    cases = load_json("data/eval_cases.json")
    predictions = load_json("data/fixture_predictions.json")

    report = evaluate_predictions(cases, predictions)

    assert report["metrics"]["composite_score"] == 1.0
    assert report["metrics"]["schema_validity_rate"] == 1.0
    assert report["metrics"]["evidence_grounding_rate"] == 1.0
    assert report["prediction_metadata"]["model"] == "none"


def test_missing_prediction_is_counted_as_false_negatives(load_json: Any) -> None:
    cases = load_json("data/eval_cases.json")[:1]
    report = evaluate_predictions(cases, {"predictions": []})

    assert report["metrics"]["decisions"]["false_negative"] == 1
    assert report["metrics"]["actions"]["false_negative"] == 1
    assert report["metrics"]["schema_validity_rate"] == 0.0

