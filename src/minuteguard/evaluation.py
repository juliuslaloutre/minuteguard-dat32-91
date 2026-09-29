"""Transparent, deterministic scoring against a versioned gold dataset."""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from minuteguard.grounding import evidence_is_grounded
from minuteguard.models import Action, Decision, MeetingAudit, Risk


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _prf(tp: int, fp: int, fn: int) -> dict[str, float | int]:
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _set_counts(expected: list[str], predicted: list[str]) -> tuple[int, int, int]:
    expected_set = {_normalise(item) for item in expected}
    predicted_set = {_normalise(item) for item in predicted}
    return (
        len(expected_set & predicted_set),
        len(predicted_set - expected_set),
        len(expected_set - predicted_set),
    )


def evaluate_predictions(
    cases: list[dict[str, Any]], prediction_bundle: dict[str, Any]
) -> dict[str, Any]:
    """Score decisions, actions, fields, risks, schema, and evidence grounding.

    Semantic labels are matched after case-folding and punctuation removal. This
    deliberately simple rule is reproducible but penalises valid paraphrases;
    the limitation is reported in the returned object.
    """

    predictions = {
        str(item["case_id"]): item["audit"]
        for item in prediction_bundle.get("predictions", [])
    }
    decision_counts = [0, 0, 0]
    action_counts = [0, 0, 0]
    risk_counts = [0, 0, 0]
    field_correct = 0
    field_total = 0
    grounded = 0
    evidence_total = 0
    valid_schemas = 0
    case_details: list[dict[str, Any]] = []

    for case in cases:
        case_id = str(case["id"])
        expected = case["expected"]
        raw_prediction = predictions.get(case_id)
        if raw_prediction is None:
            decision_counts[2] += len(expected["decisions"])
            action_counts[2] += len(expected["actions"])
            risk_counts[2] += len(expected["risks"])
            case_details.append({"case_id": case_id, "schema_valid": False, "missing": True})
            continue

        try:
            audit = MeetingAudit.model_validate(raw_prediction)
        except ValidationError as exc:
            decision_counts[2] += len(expected["decisions"])
            action_counts[2] += len(expected["actions"])
            risk_counts[2] += len(expected["risks"])
            case_details.append(
                {
                    "case_id": case_id,
                    "schema_valid": False,
                    "validation_errors": len(exc.errors()),
                }
            )
            continue

        valid_schemas += 1
        dc = _set_counts(expected["decisions"], [item.statement for item in audit.decisions])
        ac = _set_counts(
            [item["task"] for item in expected["actions"]],
            [item.task for item in audit.actions],
        )
        rc = _set_counts(expected["risks"], [item.description for item in audit.risks])
        for totals, counts in (
            (decision_counts, dc),
            (action_counts, ac),
            (risk_counts, rc),
        ):
            for index, value in enumerate(counts):
                totals[index] += value

        expected_actions = {_normalise(item["task"]): item for item in expected["actions"]}
        predicted_actions = {_normalise(item.task): item for item in audit.actions}
        for key in expected_actions.keys() & predicted_actions.keys():
            gold = expected_actions[key]
            actual = predicted_actions[key]
            for field in ("owner", "due_date", "status"):
                field_total += 1
                if getattr(actual, field) == gold[field]:
                    field_correct += 1

        source_lines = str(case["text"]).splitlines()
        items: list[Decision | Action | Risk] = [
            *audit.decisions,
            *audit.actions,
            *audit.risks,
        ]
        for item in items:
            evidence_total += 1
            if evidence_is_grounded(item.evidence, source_lines):
                grounded += 1

        case_details.append(
            {
                "case_id": case_id,
                "schema_valid": True,
                "decision_counts": dc,
                "action_counts": ac,
                "risk_counts": rc,
            }
        )

    decision_metrics = _prf(*decision_counts)
    action_metrics = _prf(*action_counts)
    risk_metrics = _prf(*risk_counts)
    field_accuracy = field_correct / field_total if field_total else 1.0
    grounding_rate = grounded / evidence_total if evidence_total else 1.0
    schema_rate = valid_schemas / len(cases) if cases else 1.0
    composite = (
        0.25 * float(decision_metrics["f1"])
        + 0.35 * float(action_metrics["f1"])
        + 0.15 * float(risk_metrics["f1"])
        + 0.15 * field_accuracy
        + 0.10 * grounding_rate
    )

    return {
        "dataset_cases": len(cases),
        "prediction_metadata": prediction_bundle.get("metadata", {}),
        "metrics": {
            "decisions": decision_metrics,
            "actions": action_metrics,
            "risks": risk_metrics,
            "action_field_accuracy": round(field_accuracy, 4),
            "evidence_grounding_rate": round(grounding_rate, 4),
            "schema_validity_rate": round(schema_rate, 4),
            "composite_score": round(composite, 4),
        },
        "weights": {
            "decision_f1": 0.25,
            "action_f1": 0.35,
            "risk_f1": 0.15,
            "action_field_accuracy": 0.15,
            "evidence_grounding_rate": 0.10,
        },
        "case_details": case_details,
        "limitations": [
            "Le matching lexical exact pénalise les paraphrases pourtant correctes.",
            "Le jeu est petit et pédagogique ; ce n'est pas une validation de production.",
            "Le score composite reflète des poids décidés avant l'expérience.",
        ],
    }
