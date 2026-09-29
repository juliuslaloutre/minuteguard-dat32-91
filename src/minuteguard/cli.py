"""Command-line interface for reproducible demos and evaluations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

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

