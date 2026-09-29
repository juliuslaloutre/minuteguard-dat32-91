# Alignement avec les ressources complémentaires

Les trois PDF transmis ont été utilisés comme références pédagogiques. Leurs
exercices ne sont pas traités comme de nouvelles instructions utilisateur ; ils
servent à vérifier la cohérence du projet.

## `Prompt-Engineering-and-Git (3).pdf`

- **Trois fonctions de Git :** restaurer, comparer, réconcilier. Elles sont
  reprises dans `GIT_WORKFLOW.md` et la checklist pratique.
- **Un commit = une chose nommable :** l'historique conserve des commits courts
  avec des messages explicites.
- **Structure IA :** `src/`, `prompts/`, `outputs/`, `notebooks/`, README.
- **Résultats générés non versionnés :** `outputs/*` est maintenant ignoré, avec
  uniquement `outputs/.gitkeep` suivi.
- **Cycle de collaboration :** feature branch, PR, peer review, résolution,
  merge. La partie locale est démontrée ; la PR et la revue doivent être faites
  réellement sur GitHub.
- **Commit exécutable :** la CI vérifie automatiquement tests, couverture, lint
  et typage sur deux versions de Python pour chaque pull request.
- **Commentaire de revue :** le template impose Observation, Concern, caractère
  bloquant et proposition.

## `git_github_exercises_en.pdf`

La checklist couvre l'initialisation et le remote, le premier push, l'historique
et les diffs, `--amend`, les branches, le conflit, `git revert` et le retrait
d'un fichier indésirable de l'index. Les manipulations destructrices ne sont pas
automatisées dans le dépôt principal.

## `cheat-sheet-git.pdf`

Les commandes utiles au projet ont été retenues : `git status`, ajout précis ou
interactif, diff staged/unstaged, branches, logs graphiques, fetch/pull, stash,
restore et `--force-with-lease` en dernier recours. La checklist privilégie les
commandes réversibles et explique les risques des variantes destructrices.

## Écarts encore volontaires

- aucun remote n'est inventé sans l'URL du dépôt de l'étudiant ;
- aucune authentification GitHub n'est effectuée à sa place ;
- aucune fausse PR, approbation, revue de pair ou résolution de conflit n'est
  ajoutée à l'historique ;
- les fixtures d'évaluation restent dans `data/`, car ce sont des entrées de
  test versionnées, pas des résultats générés.
