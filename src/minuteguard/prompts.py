"""Prompt loading and safe source delimiting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

VALID_VARIANTS = ("zero_shot", "few_shot", "deliberative")


@dataclass(frozen=True)
class PromptBundle:
    system: str
    user: str
    variant: str


class PromptRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2] / "prompts"

    def load(self, variant: str, *, title: str, numbered_source: str) -> PromptBundle:
        if variant not in VALID_VARIANTS:
            allowed = ", ".join(VALID_VARIANTS)
            raise ValueError(f"Unknown prompt variant {variant!r}; expected one of: {allowed}")

        system = (self.root / "system.md").read_text(encoding="utf-8").strip()
        template = (self.root / f"{variant}.md").read_text(encoding="utf-8").strip()
        user = template.replace("{{TITLE}}", title).replace("{{SOURCE}}", numbered_source)
        return PromptBundle(system=system, user=user, variant=variant)


def number_lines(text: str, *, first_line: int = 1) -> str:
    """Make evidence locations explicit without changing source content."""

    return "\n".join(
        f"L{number:04d}: {line}"
        for number, line in enumerate(text.splitlines(), start=first_line)
    )

