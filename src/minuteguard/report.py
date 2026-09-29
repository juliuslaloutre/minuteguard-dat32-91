"""Human-readable rendering of an audit envelope."""

from __future__ import annotations

from minuteguard.models import AuditEnvelope


def _safe(text: str | None) -> str:
    if text is None:
        return "à clarifier"
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(envelope: AuditEnvelope) -> str:
    audit = envelope.audit
    lines = [
        f"# Audit — {audit.title}",
        "",
        audit.summary,
        "",
        "## Décisions",
        "",
    ]
    if audit.decisions:
        for item in audit.decisions:
            lines.extend(
                [
                    f"- **{item.id} — {_safe(item.statement)}** "
                    f"(owner : {_safe(item.owner)}, confiance : {item.confidence})",
                    f"  - Preuve L{item.evidence.line_start}-L{item.evidence.line_end} : "
                    f'“{_safe(item.evidence.quote)}”',
                ]
            )
    else:
        lines.append("Aucune décision suffisamment prouvée.")

    lines.extend(
        [
            "",
            "## Actions",
            "",
            "| ID | Action | Responsable | Échéance | Statut |",
            "|---|---|---|---|---|",
        ]
    )
    for item in audit.actions:
        lines.append(
            f"| {item.id} | {_safe(item.task)} | {_safe(item.owner)} | "
            f"{_safe(item.due_date)} | {item.status} |"
        )
        lines.append(
            f"\nPreuve {item.id}, L{item.evidence.line_start}-L{item.evidence.line_end} : "
            f'“{_safe(item.evidence.quote)}”'
        )

    lines.extend(["", "## Risques", ""])
    if audit.risks:
        for item in audit.risks:
            lines.append(
                f"- **{item.id} [{item.severity}]** {_safe(item.description)} — "
                f'preuve L{item.evidence.line_start}-L{item.evidence.line_end} : '
                f'“{_safe(item.evidence.quote)}”'
            )
    else:
        lines.append("Aucun risque explicite suffisamment prouvé.")

    lines.extend(["", "## Questions ouvertes", ""])
    lines.extend(f"- {_safe(question)}" for question in audit.open_questions)
    if not audit.open_questions:
        lines.append("- Aucune.")

    lines.extend(["", "## Avertissements", ""])
    lines.extend(f"- {_safe(warning)}" for warning in audit.warnings)
    if not audit.warnings:
        lines.append("- Aucun avertissement automatique.")

    lines.extend(
        [
            "",
            "## Traçabilité technique",
            "",
            f"- Provider : `{envelope.provider}` / modèle : `{envelope.model}`",
            f"- Variante de prompt : `{envelope.prompt_variant}`",
            f"- Segments traités : {envelope.chunks_processed}",
            f"- Éléments ancrés : {envelope.grounded_items}",
            f"- Éléments rejetés : {envelope.rejected_items}",
            f"- SHA-256 source : `{envelope.source_sha256}`",
            "",
            "> Ce rapport assiste la revue humaine ; il ne la remplace pas.",
            "",
        ]
    )
    return "\n".join(lines)
