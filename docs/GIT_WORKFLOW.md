# Workflow Git démontré et à poursuivre

## Historique présent

Le dépôt contient des commits atomiques pour la structure, les prompts, le
pipeline et la CLI. La suite d'évaluation a été développée sur la branche
`codex/evaluation-suite`, puis fusionnée avec un commit de merge. L'auteur Git
`Codex Assistant <codex@local.invalid>` identifie honnêtement les commits créés
pendant cette assistance ; configurez votre propre identité pour vos prochains
commits.

```bash
git log --graph --oneline --decorate --all
git show --stat 25b786f
```

## Cycle recommandé pour une vraie contribution

Pour la première publication, configurer votre identité et le remote sans
réécrire les commits existants :

```bash
git config --local user.name "Votre nom"
git config --local user.email "votre-email@example.com"
git remote add origin <URL_HTTPS_DU_DEPOT>
git remote -v
git push -u origin main
```

Puis, pour chaque contribution :

```bash
git switch main
git pull --ff-only
git switch -c feature/nom-court
# modifier, tester, puis :
git add <fichiers précis>
git commit -m "feat: décrire la valeur ajoutée"
git push -u origin feature/nom-court
```

Ouvrir ensuite une pull request avec `.github/pull_request_template.md`. Un pair
doit exécuter le projet, laisser au moins un commentaire précis (problème,
impact, proposition), puis vérifier la correction avant le merge. Ne pas
présenter comme réelle une revue qui n'a pas eu lieu.

## Exercice de conflit manuel

À réaliser en binôme sur une branche dédiée, idéalement sur une phrase sans
enjeu dans un fichier de démonstration : chaque personne modifie la même ligne,
puis la seconde fusion déclenche un conflit. Ouvrir le fichier, choisir ou
recomposer la bonne version, supprimer `<<<<<<<`, `=======`, `>>>>>>>`, tester,
puis :

```bash
git add <fichier-résolu>
git commit
```

La preuve attendue est le commit de merge et l'explication orale du choix, pas
une capture artificielle. Aucun conflit n'a été fabriqué dans l'historique
actuel.

## Messages de commit

- `feat:` capacité utilisateur ;
- `fix:` correction observable ;
- `test:` cas ou métrique ;
- `docs:` explication sans changement fonctionnel ;
- `chore:` maintenance.

Chaque commit doit rester exécutable et ne contenir ni clé ni sortie locale.

Après approbation du rendu final, un tag annoté peut identifier exactement la
version présentée :

```bash
git tag -a submission-v1 -m "DAT32-91 final submission"
git push origin submission-v1
```

La CI `.github/workflows/ci.yml` exécute tests, couverture, lint et typage sur
Python 3.11 et 3.13 à chaque pull request et push sur `main`.
