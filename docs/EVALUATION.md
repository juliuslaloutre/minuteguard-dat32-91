# Protocole d'évaluation

## Question

Le few-shot améliore-t-il l'extraction des décisions et actions par rapport au
zero-shot, sans dégrader l'ancrage des preuves ?

## Jeu de données

`data/eval_cases.json` contient quatre cas écrits pour le projet : baseline,
ambiguïté/sycophancy, champs manquants/hallucination et prompt injection. Les
annotations attendues sont versionnées. Ce jeu est volontairement petit : il
sert à démontrer une méthode, pas à revendiquer une généralisation statistique.

`data/fixture_predictions.json` est une sortie de référence **rédigée à la
main**. Son score parfait vérifie le code de métrique. Il ne mesure aucun modèle.

## Grille définie avant l'expérience

| Mesure | Poids | Motivation |
|---|---:|---|
| F1 décisions | 25 % | trouver les choix actés sans sur-extraire |
| F1 actions | 35 % | valeur opérationnelle principale |
| F1 risques | 15 % | couverture du signal de vigilance |
| exactitude owner/date/statut | 15 % | utilité du suivi |
| taux de preuves ancrées | 10 % | traçabilité minimale |

La validité du schéma est aussi mesurée, sans entrer dans le score composite :
une sortie invalide ne contribue à aucun vrai positif et fait donc déjà chuter
les autres mesures.

Le matching actuel normalise casse et ponctuation puis exige une égalité
lexicale. Il est transparent et reproductible, mais pénalise une bonne
paraphrase. Une évaluation humaine aveugle peut compléter ce score, avec une
grille séparée et deux évaluateurs.

## Exécution locale de contrôle

```bash
make evaluate
cat outputs/runs/evaluation.json
```

## Benchmark réel

Pour chaque variante, exécuter :

```bash
export OPENAI_API_KEY="votre_cle"
.venv/bin/minuteguard benchmark \
  --provider openai \
  --model gpt-4o-mini \
  --variant zero_shot \
  --output outputs/runs/zero_shot_predictions.json

.venv/bin/minuteguard evaluate \
  --predictions outputs/runs/zero_shot_predictions.json \
  --output outputs/runs/zero_shot_scores.json
```

Répéter pour `few_shot` et `deliberative`, avec le même modèle. Répéter chaque
condition trois fois si le budget le permet, conserver toutes les sorties et
présenter moyenne et étendue. Ne sélectionner aucun exemple après avoir vu les
résultats sans le déclarer : cela contaminerait l'évaluation.

## Critère de décision

Préférer `few_shot` seulement si son F1 actions dépasse celui de `zero_shot`
sans diminution du taux d'ancrage et sans nouvelle vulnérabilité visible par
cas. À égalité, choisir le prompt le plus court et le moins coûteux.

