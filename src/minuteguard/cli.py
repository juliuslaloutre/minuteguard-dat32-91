"""Command-line interface for reproducible demos and evaluations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from minuteguard.evaluation import evaluate_predictions
from minuteguard.failures import failure_catalog
from minuteguard.pipeline import MeetingAuditor
from minuteguard.prompts import VALID_VARIANTS
from minuteguard.providers import FixtureProvider, OpenAIProvider, TextProvider
from minuteguard.report import render_markdown

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _provider_from_args(args: argparse.Namespace) -> TextProvider:
    if args.provider == "fixture":
        raw = _read_json(args.fixture)
        responses = raw if isinstance(raw, list) else [raw]
        return FixtureProvider(responses)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Export it or use --provider fixture for an offline demo."
        )
    return OpenAIProvider(model=args.model, api_key=api_key)


def _run_audit(args: argparse.Namespace) -> int:
    source = args.input.read_text(encoding="utf-8")
    provider = _provider_from_args(args)
    auditor = MeetingAuditor(
        provider,
        prompt_variant=args.variant,
        max_chars=args.max_chars,
        overlap_lines=args.overlap_lines,
    )
    envelope = auditor.audit(source, title=args.title or args.input.stem)
    _write_text(args.output, envelope.model_dump_json(indent=2) + "\n")
    if args.report:
        _write_text(args.report, render_markdown(envelope))
    print(f"Audit JSON écrit dans {args.output}")
    if args.report:
        print(f"Rapport Markdown écrit dans {args.report}")
    print(
        f"Contrôle des preuves : {envelope.grounded_items} ancrée(s), "
        f"{envelope.rejected_items} rejetée(s)."
    )
    return 0


def _show_prompts(args: argparse.Namespace) -> int:
    del args
    print("Variantes disponibles :")
    for variant in VALID_VARIANTS:
        print(f"- {variant}: prompts/{variant}.md")
    print("- règles partagées: prompts/system.md")
    return 0


def _show_failure_lab(args: argparse.Namespace) -> int:
    if args.json:
        from minuteguard.failures import catalog_as_dicts

        print(json.dumps(catalog_as_dicts(), ensure_ascii=False, indent=2))
        return 0

    for scenario in failure_catalog():
        print(f"\n[{scenario.name}]")
        print(f"Déclencheur : {scenario.attack_or_trigger}")
        print(f"Échec : {scenario.observable_failure}")
        print(f"Contrôle : {scenario.primary_control}")
        print(f"Risque résiduel : {scenario.residual_risk}")
        print(f"Preuve : {scenario.verification}")
    return 0


def _run_evaluation(args: argparse.Namespace) -> int:
    cases = _read_json(args.cases)
    predictions = _read_json(args.predictions)
    if not isinstance(cases, list) or not isinstance(predictions, dict):
        raise ValueError("Invalid evaluation file shape")
    report = evaluate_predictions(cases, predictions)
    _write_text(args.output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    metrics = report["metrics"]
    print(f"Rapport d'évaluation écrit dans {args.output}")
    print(
        f"Score composite={metrics['composite_score']:.4f} | "
        f"actions F1={metrics['actions']['f1']:.4f} | "
        f"ancrage={metrics['evidence_grounding_rate']:.4f}"
    )
    return 0


def _run_benchmark(args: argparse.Namespace) -> int:
    cases = _read_json(args.cases)
    if not isinstance(cases, list):
        raise ValueError("The cases file must contain a JSON list")
    provider = _provider_from_args(args)
    auditor = MeetingAuditor(provider, prompt_variant=args.variant)
    predictions: list[dict[str, Any]] = []
    for case in cases:
        envelope = auditor.audit(str(case["text"]), title=str(case["title"]))
        predictions.append(
            {
                "case_id": str(case["id"]),
                "audit": envelope.audit.model_dump(mode="json"),
                "rejected_items": envelope.rejected_items,
            }
        )
    bundle = {
        "metadata": {
            "provider": provider.provider_name,
            "model": provider.model_name,
            "prompt_variant": args.variant,
            "generated_at": datetime.now(UTC).isoformat(),
        },
        "predictions": predictions,
    }
    _write_text(args.output, json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")
    print(f"Prédictions écrites dans {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minuteguard",
        description="Auditer un compte rendu avec des sorties structurées et vérifiables.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Auditer un fichier texte")
    audit.add_argument("input", type=Path)
    audit.add_argument("--title")
    audit.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    audit.add_argument(
        "--fixture",
        type=Path,
        default=PROJECT_ROOT / "data" / "fixture_response.json",
    )
    audit.add_argument(
        "--model",
        default=os.environ.get("MINUTEGUARD_MODEL", "gpt-4o-mini"),
    )
    audit.add_argument("--variant", choices=VALID_VARIANTS, default="few_shot")
    audit.add_argument("--max-chars", type=int, default=12_000)
    audit.add_argument("--overlap-lines", type=int, default=2)
    audit.add_argument("--output", type=Path, default=Path("outputs/runs/audit.json"))
    audit.add_argument("--report", type=Path)
    audit.set_defaults(handler=_run_audit)

    prompts = subparsers.add_parser("prompts", help="Lister les stratégies de prompt")
    prompts.set_defaults(handler=_show_prompts)

    failures = subparsers.add_parser(
        "failure-lab", help="Afficher les quatre modes d'échec et leurs contrôles"
    )
    failures.add_argument("--json", action="store_true")
    failures.set_defaults(handler=_show_failure_lab)

    evaluate = subparsers.add_parser("evaluate", help="Évaluer un fichier de prédictions")
    evaluate.add_argument(
        "--cases", type=Path, default=PROJECT_ROOT / "data" / "eval_cases.json"
    )
    evaluate.add_argument(
        "--predictions",
        type=Path,
        default=PROJECT_ROOT / "data" / "fixture_predictions.json",
    )
    evaluate.add_argument("--output", type=Path, default=Path("outputs/runs/evaluation.json"))
    evaluate.set_defaults(handler=_run_evaluation)

    benchmark = subparsers.add_parser(
        "benchmark", help="Générer des prédictions sur le jeu d'évaluation"
    )
    benchmark.add_argument(
        "--cases", type=Path, default=PROJECT_ROOT / "data" / "eval_cases.json"
    )
    benchmark.add_argument("--provider", choices=("fixture", "openai"), default="openai")
    benchmark.add_argument(
        "--fixture",
        type=Path,
        default=PROJECT_ROOT / "data" / "fixture_response.json",
    )
    benchmark.add_argument(
        "--model", default=os.environ.get("MINUTEGUARD_MODEL", "gpt-4o-mini")
    )
    benchmark.add_argument("--variant", choices=VALID_VARIANTS, default="few_shot")
    benchmark.add_argument(
        "--output", type=Path, default=Path("outputs/runs/predictions.json")
    )
    benchmark.set_defaults(handler=_run_benchmark)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, RuntimeError, ValueError, ValidationError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
