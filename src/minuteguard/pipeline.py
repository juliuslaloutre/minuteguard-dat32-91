"""Orchestration pipeline: chunk, prompt, parse, ground, and merge."""

from __future__ import annotations

import hashlib
import re
from typing import TypeVar

from minuteguard.chunking import split_text
from minuteguard.grounding import enforce_grounding
from minuteguard.models import Action, AuditEnvelope, Decision, MeetingAudit, Risk
from minuteguard.prompts import PromptRepository, number_lines
from minuteguard.providers import TextProvider

ItemT = TypeVar("ItemT")


def _dedupe_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _dedupe(items: list[ItemT], *, attribute: str) -> list[ItemT]:
    seen: set[str] = set()
    result: list[ItemT] = []
    for item in items:
        key = _dedupe_key(str(getattr(item, attribute)))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _renumber(
    decisions: list[Decision], actions: list[Action], risks: list[Risk]
) -> tuple[list[Decision], list[Action], list[Risk]]:
    for index, item in enumerate(decisions, start=1):
        item.id = f"D{index}"
    for index, item in enumerate(actions, start=1):
        item.id = f"A{index}"
    for index, item in enumerate(risks, start=1):
        item.id = f"R{index}"
    return decisions, actions, risks


class MeetingAuditor:
    def __init__(
        self,
        provider: TextProvider,
        *,
        prompt_variant: str = "few_shot",
        max_chars: int = 12_000,
        overlap_lines: int = 2,
        prompts: PromptRepository | None = None,
    ) -> None:
        self.provider = provider
        self.prompt_variant = prompt_variant
        self.max_chars = max_chars
        self.overlap_lines = overlap_lines
        self.prompts = prompts or PromptRepository()

    def audit(self, text: str, *, title: str) -> AuditEnvelope:
        if not text.strip():
            raise ValueError("The meeting text cannot be empty")

        chunks = split_text(text, max_chars=self.max_chars, overlap_lines=self.overlap_lines)
        audits: list[MeetingAudit] = []
        grounded_total = 0
        rejected_total = 0
        schema = MeetingAudit.model_json_schema()

        for chunk in chunks:
            bundle = self.prompts.load(
                self.prompt_variant,
                title=title,
                numbered_source=number_lines(chunk.text, first_line=chunk.first_line),
            )
            raw = self.provider.complete(
                system_prompt=bundle.system,
                user_prompt=bundle.user,
                json_schema=schema,
            )
            parsed = MeetingAudit.model_validate_json(raw)
            parsed.title = title
            checked, grounded, rejected = enforce_grounding(parsed, text)
            audits.append(checked)
            grounded_total += grounded
            rejected_total += rejected

        merged = self._merge(audits, title=title)
        return AuditEnvelope(
            audit=merged,
            prompt_variant=self.prompt_variant,
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            source_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            chunks_processed=len(chunks),
            grounded_items=grounded_total,
            rejected_items=rejected_total,
        )

    @staticmethod
    def _merge(audits: list[MeetingAudit], *, title: str) -> MeetingAudit:
        decisions = _dedupe(
            [item for audit in audits for item in audit.decisions], attribute="statement"
        )
        actions = _dedupe([item for audit in audits for item in audit.actions], attribute="task")
        risks = _dedupe(
            [item for audit in audits for item in audit.risks], attribute="description"
        )
        decisions, actions, risks = _renumber(decisions, actions, risks)
        questions = list(
            dict.fromkeys(question for audit in audits for question in audit.open_questions)
        )
        warnings = list(dict.fromkeys(warning for audit in audits for warning in audit.warnings))
        summaries = list(dict.fromkeys(audit.summary for audit in audits))
        summary = summaries[0] if len(summaries) == 1 else " ".join(summaries)
        return MeetingAudit(
            title=title,
            summary=summary,
            decisions=decisions,
            actions=actions,
            risks=risks,
            open_questions=questions,
            warnings=warnings,
        )
