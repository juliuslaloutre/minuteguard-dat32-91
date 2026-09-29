#!/usr/bin/env bash

# Read-only readiness check: it never edits Git history, remotes, or files.
set -u

pass_count=0
action_count=0

pass() {
  printf 'PASS   %s\n' "$1"
  pass_count=$((pass_count + 1))
}

action() {
  printf 'ACTION %s\n' "$1"
  action_count=$((action_count + 1))
}

branch="$(git branch --show-current 2>/dev/null || true)"
if [ "$branch" = "main" ]; then
  pass "branche courante = main"
else
  action "revenir sur main avant le rendu (branche actuelle: ${branch:-aucune})"
fi

author_name="$(git config user.name 2>/dev/null || true)"
author_email="$(git config user.email 2>/dev/null || true)"
if [ -n "$author_name" ] && [ "$author_name" != "Codex Assistant" ]; then
  pass "identité Git personnelle configurée: $author_name"
else
  action "configurer votre nom Git personnel; la valeur actuelle est ${author_name:-absente}"
fi
if [ -n "$author_email" ] && [ "$author_email" != "codex@local.invalid" ]; then
  pass "email Git personnel configuré"
else
  action "configurer votre email Git personnel"
fi

remote_url="$(git remote get-url origin 2>/dev/null || true)"
if [ -n "$remote_url" ]; then
  pass "remote origin configuré: $remote_url"
else
  action "créer le dépôt GitHub puis ajouter le remote origin"
fi

if git log --merges -1 --format=%H >/dev/null 2>&1 && [ -n "$(git log --merges -1 --format=%H)" ]; then
  pass "au moins un commit de merge présent"
else
  action "aucun commit de merge détecté"
fi

branch_count="$(git branch --format='%(refname:short)' | wc -l | tr -d ' ')"
if [ "$branch_count" -ge 2 ]; then
  pass "historique de branche présent ($branch_count branches locales)"
else
  action "aucune branche de fonctionnalité conservée"
fi

if [ -z "$(git status --porcelain)" ]; then
  pass "working tree propre"
else
  action "des changements ne sont pas encore commités"
fi

if git check-ignore -q outputs/runs/probe.json; then
  pass "les résultats générés sous outputs/ sont ignorés"
else
  action "outputs/ n'est pas correctement ignoré"
fi

if git grep -nE '^(<<<<<<<|=======|>>>>>>>)' -- 'src/**' 'tests/**' 'prompts/**' 'data/**' >/dev/null 2>&1; then
  action "marqueurs de conflit détectés dans les fichiers exécutables"
else
  pass "aucun marqueur de conflit dans le code, les tests, prompts ou données"
fi

printf '\nRésultat: %s PASS, %s ACTION(S).\n' "$pass_count" "$action_count"
printf 'Les ACTIONS nécessitent une décision ou une action humaine; ce script ne les automatise pas.\n'

