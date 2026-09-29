# MinuteGuard

MinuteGuard transforme un compte rendu de réunion non structuré en un audit
JSON vérifiable : décisions, actions, responsables, échéances, questions
ouvertes et risques. Chaque élément extrait doit citer un passage réellement
présent dans la source. Le texte d'entrée est toujours traité comme une donnée
non fiable, jamais comme une instruction.

> Projet final DAT32-91 — version de travail. Les résultats d'un LLM doivent
> être relus par une personne avant toute décision opérationnelle.

## Démarrage rapide

Prérequis : Python 3.11+ et Git.

```bash
make install
make test
make demo
```

Le dernier appel fonctionne sans clé API et crée :

- `outputs/runs/demo.json` — résultat structuré ;
- `outputs/runs/demo.md` — rapport lisible.

Pour une exécution réelle :

```bash
export OPENAI_API_KEY="votre_cle"
.venv/bin/minuteguard audit data/sample_meeting.txt \
  --provider openai \
  --model gpt-4o-mini \
  --variant few_shot \
  --output outputs/runs/live.json \
  --report outputs/runs/live.md
```

Ne placez jamais une clé dans le dépôt. Le modèle par défaut est volontairement
configurable afin d'éviter de figer le projet sur un alias qui pourrait évoluer.

## Question et hypothèse de projet

**Question :** un prompt structuré, enrichi d'exemples et d'un contrôle de
preuves, extrait-il des engagements de réunion plus fidèlement qu'un prompt
minimal ?

**Hypothèse :** le few-shot améliore la complétude des champs, tandis que le
schéma strict et la vérification déterministe des citations réduisent les
hallucinations. Cette hypothèse est testée avec un jeu d'évaluation versionné et
une grille explicite, pas avec une impression subjective.

## Commandes utiles

```bash
make test       # tests unitaires et couverture
make lint       # Ruff + mypy strict
make demo       # démonstration locale reproductible
make evaluate   # score les prédictions d'exemple

.venv/bin/minuteguard prompts
.venv/bin/minuteguard failure-lab
.venv/bin/minuteguard evaluate --help
```

## Structure

```text
.
├── data/                 exemples, jeu d'évaluation et fixtures
├── docs/                 architecture, prompts, évaluation, soutenance
├── notebooks/            protocole expérimental reproductible
├── outputs/              résultats de référence et exécutions ignorées
├── prompts/              versions zero-shot, few-shot et délibérative
├── src/minuteguard/      application Python
└── tests/                tests unitaires et adversariaux
```

## Parcours de démonstration (3 minutes)

1. `make test` : prouver que les garde-fous sont exécutables.
2. `make demo` : auditer le compte rendu sans réseau.
3. Ouvrir `outputs/runs/demo.md` et relier une action à sa citation.
4. `make evaluate` : expliquer précision, rappel et ancrage des preuves.
5. `minuteguard failure-lab` : montrer les quatre modes d'échec du cours.

## Ce que MinuteGuard est — et n'est pas

MinuteGuard est une **application pilotée par prompt** : un pipeline Python
orchestre un LLM, valide sa sortie et produit un rapport. Ce n'est pas un LLM
(le modèle génératif lui-même), ni un système agentique autonome : aucune
boucle ne choisit librement des outils ou des objectifs. Cette architecture
plus simple est adaptée à une extraction bornée, auditable et à faible risque.

## Reproductibilité et limites

- Le fournisseur `fixture` garantit une démo locale déterministe.
- Le fournisseur `openai` nécessite une clé, un accès réseau et peut avoir un coût.
- Une sortie valide au niveau du schéma peut rester fausse au niveau sémantique.
- Les citations sont contrôlées, mais les synonymes employés dans les champs
  résumés rendent encore nécessaire une revue humaine.
- Aucun score de fixture n'est présenté comme une performance réelle de modèle.

La matrice complète entre le syllabus et les preuves du dépôt se trouve dans
[`docs/RUBRIC_TRACEABILITY.md`](docs/RUBRIC_TRACEABILITY.md).

