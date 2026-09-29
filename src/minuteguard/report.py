"""Human-readable rendering of an audit envelope."""

from __future__ import annotations

from minuteguard.models import AuditEnvelope


def _safe(text: str | None) -> str:
    if text is None:
        return "à clarifier"
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(envelope: AuditEnvelope) -> str:
    audit = envelope.audit
    git_revision = envelope.git_commit or "indisponible"
    if envelope.git_dirty is None:
        git_state = "inconnu"
    else:
        git_state = "modifié" if envelope.git_dirty else "propre"
    lines = [
        f"# Audit — {audit.title}",
        "",
        audit.summary,
        "",
        "## Décisions",
        "",
    ]
    if audit.decisions:
        for decision in audit.decisions:
            lines.extend(
                [
                    f"- **{decision.id} — {_safe(decision.statement)}** "
                    f"(owner : {_safe(decision.owner)}, confiance : {decision.confidence})",
                    f"  - Preuve L{decision.evidence.line_start}-L{decision.evidence.line_end} : "
                    f'“{_safe(decision.evidence.quote)}”',
                ]
            )
    else:
        lines.append("Aucune décision suffisamment prouvée.")

    lines.extend(
        [
            "",
            "## Actions",
            "",
            "| ID | Action | Responsable | Échéance | Statut | Preuve |",
            "|---|---|---|---|---|---|",
        ]
    )
    for action in audit.actions:
        lines.append(
            f"| {action.id} | {_safe(action.task)} | {_safe(action.owner)} | "
            f"{_safe(action.due_date)} | {action.status} | "
            f"L{action.evidence.line_start}-L{action.evidence.line_end} : "
            f'“{_safe(action.evidence.quote)}” |'
        )

    lines.extend(["", "## Risques", ""])
    if audit.risks:
        for risk in audit.risks:
            lines.append(
                f"- **{risk.id} [{risk.severity}]** {_safe(risk.description)} — "
                f'preuve L{risk.evidence.line_start}-L{risk.evidence.line_end} : '
                f'“{_safe(risk.evidence.quote)}”'
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
            f"- SHA-256 prompt effectif : `{envelope.prompt_sha256}`",
            f"- Révision Git : `{git_revision}` (dépôt {git_state})",
            "",
            "> Ce rapport assiste la revue humaine ; il ne la remplace pas.",
            "",
        ]
    )
    return "\n".join(lines)
