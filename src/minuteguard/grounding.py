"""Deterministic evidence checks applied after model generation."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from typing import TypeVar

from minuteguard.models import Action, Decision, Evidence, MeetingAudit, Risk

GroundedItem = TypeVar("GroundedItem", Action, Decision, Risk)


def _canonical(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", normalized).strip()


def evidence_is_grounded(evidence: Evidence, source_lines: Sequence[str]) -> bool:
    if evidence.line_end > len(source_lines):
        return False
    passage = "\n".join(source_lines[evidence.line_start - 1 : evidence.line_end])
    return _canonical(evidence.quote) in _canonical(passage)


def _partition_grounded(
    items: Sequence[GroundedItem], source_lines: Sequence[str]
) -> tuple[list[GroundedItem], int]:
    kept: list[GroundedItem] = []
    rejected = 0
    for item in items:
        if evidence_is_grounded(item.evidence, source_lines):
            kept.append(item)
        else:
            rejected += 1
    return kept, rejected


def enforce_grounding(audit: MeetingAudit, source: str) -> tuple[MeetingAudit, int, int]:
    """Drop ungrounded extracted items and return kept/rejected counts."""

    checked = audit.model_copy(deep=True)
    source_lines = source.splitlines()
    decisions, rejected_decisions = _partition_grounded(checked.decisions, source_lines)
    actions, rejected_actions = _partition_grounded(checked.actions, source_lines)
    risks, rejected_risks = _partition_grounded(checked.risks, source_lines)
    checked.decisions = decisions
    checked.actions = actions
    checked.risks = risks

    rejected = rejected_decisions + rejected_actions + rejected_risks
    grounded = len(decisions) + len(actions) + len(risks)
    if rejected:
        checked.warnings.append(
            f"Garde-fou : {rejected} élément(s) rejeté(s), car leur citation "
            "ne correspondait pas aux lignes sources."
        )
    return checked, grounded, rejected

