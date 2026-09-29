# Checklist pratique Git et GitHub

Cette checklist adapte les exercices fournis au vrai dépôt MinuteGuard. Elle
doit être réalisée par l'étudiant ou l'équipe : une trace inventée ne remplace
pas une manipulation comprise et expliquée.

## 1. Vérifier l'état actuel

```bash
git status
git log --graph --oneline --decorate --all
git diff HEAD~1 HEAD --stat
make git-check
```

À expliquer : working directory, staging area et repository sont trois états
différents. Un commit est local ; il n'est partagé qu'après un push.

## 2. Configurer l'identité et le remote

Les commits produits pendant l'assistance sont volontairement attribués à
`Codex Assistant`. Configurer désormais votre identité réelle :

```bash
git config user.name "Votre nom"
git config user.email "votre-email@example.com"
git remote add origin <URL_HTTPS_DE_VOTRE_DEPOT>
git push -u origin main
```

Vérifier ensuite sur GitHub que les fichiers et l'historique sont visibles.

## 3. Réaliser une vraie feature branch

Choisir une petite amélioration réelle, par exemple ajouter un cinquième cas
d'évaluation annoté :

```bash
git switch -c feature/add-evaluation-case
# modifier data/eval_cases.json et data/fixture_predictions.json
make test
git status
git add data/eval_cases.json data/fixture_predictions.json
git diff --staged
git commit -m "test: add contradictory deadline evaluation case"
git push -u origin feature/add-evaluation-case
```

Ne pas utiliser `git add .` mécaniquement : vérifier et ajouter les fichiers
précis, ou employer `git add -p` pour sélectionner les blocs.

## 4. Ouvrir et faire relire la pull request

Utiliser le template du dépôt. Le reviewer doit lire le diff, exécuter les tests
et écrire un commentaire structuré, par exemple :

> **Observation :** le cas contient une instruction non fiable, mais aucun tag
> `prompt_injection`. **Concern :** le reporting par catégorie sera faux.
> **Blocking :** oui. **Proposition :** ajouter le tag puis relancer l'évaluation.

Corriger sur la même branche, pousser le nouveau commit, obtenir l'approbation,
puis merger. Cette séquence fournit la preuve authentique branch - PR - review -
fix - merge attendue par le cours.

## 5. Résoudre un conflit sur une branche d'exercice

Le faire avec un pair sur un fichier de brouillon sans secret ni donnée utile.
Créer d'abord la branche concurrente depuis une base commune, puis effectuer
les deux commits divergents :

```bash
git switch main
git switch -c practice/conflict-other
git switch main
# modifier une ligne du brouillon, git add, git commit
git switch practice/conflict-other
# modifier différemment la même ligne, git add, git commit
git switch main
git merge practice/conflict-other
```

La fusion produit alors :

```text
<<<<<<< HEAD
votre version
=======
version de l'autre branche
>>>>>>> feature/conflict-practice
```

Lire les deux intentions, écrire la version finale, supprimer les trois
marqueurs, puis :

```bash
git add <fichier-resolu>
git commit
make test
```

Ne jamais committer les marqueurs. Être capable d'expliquer pourquoi la version
finale est correcte.

## 6. Savoir corriger l'historique sans perdre le travail

- dernier commit local incomplet : `git commit --amend` ;
- commit déjà partagé à annuler : `git revert <commit>` crée une trace sûre ;
- fichier modifié à comparer : `git diff` ;
- staging à comparer : `git diff --staged` ;
- travail temporaire à mettre de côté : `git stash` ;
- synchroniser prudemment : `git fetch`, puis inspecter avant merge/rebase.

Éviter `git reset --hard` et `git push --force`. Si une réécriture d'une branche
personnelle non fusionnée est réellement nécessaire, préférer
`git push --force-with-lease` et expliquer le risque.

## 7. Protéger les secrets et les résultats générés

`.env` et tout le contenu généré sous `outputs/` sont ignorés. Vérifier :

```bash
git check-ignore .env
git check-ignore outputs/runs/demo.json
git ls-files
```

Si un faux fichier sensible de laboratoire a été ajouté sans être committé,
utiliser `git rm --cached <fichier>` puis compléter `.gitignore`. Si un vrai
secret a déjà été committé, le retirer ne suffit pas : le révoquer immédiatement
et demander de l'aide pour nettoyer l'historique.

## Critère de réussite

La preuve finale est visible sur GitHub : branche poussée, PR compréhensible,
commentaire de revue actionnable, correction, approbation et merge. Garder le
dépôt exécutable à chaque étape avec `make test`.

Après validation par l'équipe, identifier exactement la version remise :

```bash
git tag -a submission-v1 -m "DAT32-91 final submission"
git push origin submission-v1
```
