# Éthique, données et limites

## Données personnelles

Un compte rendu peut contenir des noms, opinions, données contractuelles ou
informations sensibles. Avant un appel à une API externe, l'utilisateur doit :

1. vérifier qu'il est autorisé à traiter et transférer ces données ;
2. minimiser ou pseudonymiser les informations non nécessaires ;
3. appliquer les politiques de conservation et de sécurité de son organisation ;
4. ne jamais placer de texte sensible dans les fixtures publiques.

MinuteGuard ne journalise pas la clé API et `.env` est ignoré. Le projet ne
promet cependant pas une conformité RGPD automatique : celle-ci dépend du
contexte, de la base légale, des contrats et de la configuration du service.

## Décisions humaines

La sortie ne doit pas déclencher automatiquement une sanction, une dépense ou
un engagement contractuel. Les citations rendent la revue plus rapide, mais le
responsable humain doit vérifier la source.

## Limites connues

- français prioritaire ; les dates ambiguës ne sont pas toutes normalisées ;
- égalité lexicale simple pour la déduplication et l'évaluation ;
- absence de prise en charge PDF, audio ou reconnaissance des locuteurs ;
- petit jeu d'évaluation synthétique ;
- résumé global non contrôlé citation par citation ;
- coût, latence et disponibilité du fournisseur externe non garantis.

