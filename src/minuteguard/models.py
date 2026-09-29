"""Strict domain models shared by the prompt, pipeline, and evaluator."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Reject fields that the application did not explicitly request."""

    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    quote: str = Field(min_length=1, description="Verbatim quote from the source")
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)

    @model_validator(mode="after")
    def ordered_lines(self) -> Evidence:
        if self.line_end < self.line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class Decision(StrictModel):
    id: str = Field(pattern=r"^D[0-9]+$")
    statement: str = Field(min_length=1)
    owner: str | None
    confidence: Literal["low", "medium", "high"]
    evidence: Evidence


class Action(StrictModel):
    id: str = Field(pattern=r"^A[0-9]+$")
    task: str = Field(min_length=1)
    owner: str | None
    due_date: str | None = Field(description="ISO date YYYY-MM-DD, or null")
    status: Literal["confirmed", "needs_clarification"]
    evidence: Evidence

    @model_validator(mode="after")
    def valid_due_date(self) -> Action:
        if self.due_date is not None:
            try:
                date.fromisoformat(self.due_date)
            except ValueError as exc:
                raise ValueError("due_date must be a valid ISO date (YYYY-MM-DD)") from exc
        return self


class Risk(StrictModel):
    id: str = Field(pattern=r"^R[0-9]+$")
    description: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    evidence: Evidence


class MeetingAudit(StrictModel):
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    decisions: list[Decision]
    actions: list[Action]
    risks: list[Risk]
    open_questions: list[str]
    warnings: list[str]


class AuditEnvelope(StrictModel):
    """Application metadata kept outside model-generated content."""

    audit: MeetingAudit
    prompt_variant: str
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider: str
    model: str
    source_sha256: str
    git_commit: str | None = Field(
        default=None, pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$"
    )
    git_dirty: bool | None = None
    chunks_processed: int = Field(ge=1)
    grounded_items: int = Field(ge=0)
    rejected_items: int = Field(ge=0)
