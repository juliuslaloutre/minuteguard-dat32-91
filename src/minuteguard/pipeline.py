"""Orchestration pipeline: chunk, prompt, parse, ground, and merge."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import TypeVar

from minuteguard.chunking import split_text
from minuteguard.grounding import enforce_grounding
from minuteguard.models import Action, AuditEnvelope, Decision, MeetingAudit, Risk
from minuteguard.prompts import PromptRepository, number_lines
from minuteguard.providers import TextProvider

ItemT = TypeVar("ItemT")
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _prompt_sha256(prompt_messages: list[tuple[str, str]]) -> str:
    """Hash the exact ordered system/user messages sent for every chunk."""

    digest = hashlib.sha256()
    digest.update(b"minuteguard-prompt-transcript-v1\0")
    for system_prompt, user_prompt in prompt_messages:
        digest.update(b"bundle\0")
        for role, content in ((b"system", system_prompt), (b"user", user_prompt)):
            encoded = content.encode("utf-8")
            digest.update(role)
            digest.update(b"\0")
            digest.update(len(encoded).to_bytes(8, byteorder="big"))
            digest.update(encoded)
    return digest.hexdigest()


def _git_metadata(repo_root: Path | None = None) -> tuple[str | None, bool | None]:
    """Return the current revision and dirty state, or null metadata without Git."""

    root = repo_root or PROJECT_ROOT
    try:
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, None

    commit = revision.stdout.strip().lower()
    if revision.returncode != 0 or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        return None, None

    try:
        status = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=normal",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return commit, None

    if status.returncode != 0:
        return commit, None
    return commit, bool(status.stdout.strip())


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
    for index, decision in enumerate(decisions, start=1):
        decision.id = f"D{index}"
    for index, action in enumerate(actions, start=1):
        action.id = f"A{index}"
    for index, risk in enumerate(risks, start=1):
        risk.id = f"R{index}"
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

        git_commit, git_dirty = _git_metadata()
        chunks = split_text(text, max_chars=self.max_chars, overlap_lines=self.overlap_lines)
        audits: list[MeetingAudit] = []
        prompt_messages: list[tuple[str, str]] = []
        rejected_total = 0
        schema = MeetingAudit.model_json_schema()

        for chunk in chunks:
            bundle = self.prompts.load(
                self.prompt_variant,
                title=title,
                numbered_source=number_lines(chunk.text, first_line=chunk.first_line),
            )
            prompt_messages.append((bundle.system, bundle.user))
            raw = self.provider.complete(
                system_prompt=bundle.system,
                user_prompt=bundle.user,
                json_schema=schema,
            )
            parsed = MeetingAudit.model_validate_json(raw)
            parsed.title = title
            checked, _, rejected = enforce_grounding(parsed, text)
            audits.append(checked)
            rejected_total += rejected

        merged = self._merge(audits, title=title)
        final_item_count = len(merged.decisions) + len(merged.actions) + len(merged.risks)
        return AuditEnvelope(
            audit=merged,
            prompt_variant=self.prompt_variant,
            prompt_sha256=_prompt_sha256(prompt_messages),
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            source_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            git_commit=git_commit,
            git_dirty=git_dirty,
            chunks_processed=len(chunks),
            grounded_items=final_item_count,
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
