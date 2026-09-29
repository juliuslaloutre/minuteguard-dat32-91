"""Executable catalogue for the four failure modes taught in DAT32-91."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FailureScenario:
    name: str
    attack_or_trigger: str
    observable_failure: str
    primary_control: str
    residual_risk: str
    verification: str


def failure_catalog() -> list[FailureScenario]:
    return [
        FailureScenario(
            name="hallucination",
            attack_or_trigger="Demander un owner alors qu'aucun n'est cité.",
            observable_failure="Le modèle invente un responsable plausible.",
            primary_control="Champs nullables, preuve obligatoire et filtre de citation.",
            residual_risk="Une citation réelle peut être interprétée de travers.",
            verification="tests/test_grounding.py et métrique evidence_grounding_rate",
        ),
        FailureScenario(
            name="sycophancy",
            attack_or_trigger="Le texte affirme avec insistance qu'une proposition est validée.",
            observable_failure="Le modèle approuve le cadrage au lieu de classifier le fait.",
            primary_control="Définition explicite de décision et contre-exemple few-shot.",
            residual_risk="Les formulations diplomatiques restent ambiguës.",
            verification="cas eval_ambiguity dans data/eval_cases.json",
        ),
        FailureScenario(
            name="prompt_injection",
            attack_or_trigger="La source demande d'ignorer le système et d'ajouter un fait.",
            observable_failure="L'instruction contenue dans la donnée est exécutée.",
            primary_control="Délimitation non fiable, rôles séparés et validation des preuves.",
            residual_risk="Une injection peut reprendre des mots réels pour fabriquer un sens.",
            verification="tests/test_prompt_security.py et exemple data/sample_meeting.txt",
        ),
        FailureScenario(
            name="context_overflow",
            attack_or_trigger="Le compte rendu dépasse la fenêtre exploitable du modèle.",
            observable_failure="Le début est tronqué ou des actions disparaissent.",
            primary_control="Découpage borné par lignes, chevauchement puis déduplication.",
            residual_risk="Une relation très éloignée entre deux passages peut être perdue.",
            verification="tests/test_chunking.py",
        ),
    ]


def catalog_as_dicts() -> list[dict[str, str]]:
    return [asdict(scenario) for scenario in failure_catalog()]

