# Traçabilité avec le syllabus DAT32-91

## Critères explicites du projet

| Critère | Preuve dans le dépôt | Démonstration |
|---|---|---|
| dépôt Git exécutable | `README.md`, `pyproject.toml`, `Makefile`, CI | `make install && make test && make demo` |
| historique Git | commits atomiques + branche fusionnée | `git log --graph --all` |
| application pilotée par prompt | `prompts/`, `pipeline.py`, `cli.py` | `minuteguard audit ...` |
| design des prompts | trois variantes + `PROMPT_DESIGN.md` | comparer fichiers et scores |
| justification technique | `ARCHITECTURE.md`, ADR implicites, limites | soutenance guidée |
| défense orale obligatoire | `ORAL_DEFENCE.md` | démo 7 minutes |
| évaluation par les pairs | template PR prêt | doit être réalisée réellement avant rendu |

## Learning outcomes

| # | Résultat attendu | Preuve |
|---:|---|---|
| 1 | expliquer le version control | `docs/GIT_WORKFLOW.md` |
| 2 | commits significatifs et push | historique local ; push à faire vers le dépôt de rendu |
| 3 | branche, merge, conflit manuel | branche/merge présents ; exercice de conflit documenté mais non fabriqué |
| 4 | PR, commentaire, correction | template présent ; vraie PR et vraie revue encore requises |
| 5 | structure standard et README reproductible | `src/`, `prompts/`, `outputs/`, `notebooks/`, README |
| 6 | next-token, température, top-p | `docs/PROMPT_DESIGN.md` et réponses de soutenance |
| 7 | LLM vs conversationnel vs agentique | README et `docs/ARCHITECTURE.md` |
| 8 | zero-shot, few-shot, délibération, grille | `prompts/`, `evaluation.py`, `docs/EVALUATION.md` |
| 9 | persona, format, contraintes, rôles | `prompts/system.md`, schéma et `PROMPT_DESIGN.md` |
| 10 | API Python, réponse, retry 429 | `providers.py`, `tests/test_provider.py` |
| 11 | quatre modes d'échec | `failure-lab`, `FAILURE_MODES.md`, tests adversariaux |

Chaque audit ajoute une preuve de provenance : hash de la source, hash du prompt
effectif, modèle, variante, commit Git et état propre/modifié du dépôt.

## Éléments qui ne doivent pas être sur-vendus

- Le score parfait de la fixture ne prouve pas la qualité d'un modèle.
- La branche locale fusionnée ne remplace pas une pull request distante.
- La revue par un pair et le conflit manuel n'ont pas été inventés.
- Le corpus synthétique de quatre cas ne suffit pas pour un usage production.

Cette transparence renforce la défense : elle distingue clairement ce qui est
implémenté, ce qui est testé et ce qui reste à produire avec l'équipe.
