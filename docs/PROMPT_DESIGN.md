# Conception des prompts

## Trois variantes testables

| Variante | Technique | Intérêt | Coût / risque |
|---|---|---|---|
| `zero_shot` | consigne seule | baseline courte | frontières de catégories moins illustrées |
| `few_shot` | deux exemples contrastés | clarifie décision vs proposition et champs absents | plus de tokens ; risque de sur-ajustement aux exemples |
| `deliberative` | checklist interne avant réponse | favorise l'auto-vérification | latence supérieure ; aucun raisonnement interne n'est exposé |

Les trois variantes partagent `prompts/system.md`. Ainsi, une comparaison ne
change qu'une variable : la stratégie utilisateur.

## Techniques exigées par le cours

### Persona

« Auditeur de comptes rendus rigoureux » oriente le modèle vers la fidélité et
la prudence. Une persona ne constitue toutefois pas un mécanisme de sécurité ;
les contrôles déterministes restent nécessaires.

### Format de sortie

Le JSON Schema impose les collections, types, valeurs autorisées et
`additionalProperties: false`. La structure facilite le traitement logiciel et
réduit les erreurs de parsing. Elle ne garantit pas la justesse sémantique.

### Contraintes

Les règles rendent `owner` et `due_date` nullables, interdisent l'inférence et
exigent une citation courte par élément. Une contrainte trop longue peut
diluer les priorités ; elles sont donc numérotées et testées.

### Séparation des rôles

Les invariants et la frontière de confiance sont dans les instructions système.
Le compte rendu se trouve dans l'entrée utilisateur entre deux délimiteurs
explicites. Une instruction trouvée dans cette zone reste une donnée.

### Few-shot

Un exemple positif contient une décision et une action complètes. Un
contre-exemple montre qu'une proposition n'est pas une décision et que les
champs inconnus restent `null`. Les faits des exemples sont explicitement
interdits dans la réponse à produire.

### Délibération

La variante `deliberative` demande une checklist silencieuse, puis seulement le
JSON final. Elle teste l'intérêt d'une analyse intermédiaire sans exiger ni
stocker une chaîne de pensée privée.

## Paramètres d'échantillonnage

Un LLM prédit successivement le token suivant à partir d'une distribution de
probabilités. La **température** aplatit ou concentre cette distribution ; le
**top-p** limite les candidats au plus petit ensemble dont la masse cumulée
atteint `p`. Modifier les deux en même temps rend l'effet difficile à attribuer.

MinuteGuard fixe `temperature=0` et ne règle pas `top_p`, car l'extraction
privilégie la stabilité à la créativité. Cela ne rend pas le système parfaitement
déterministe : infrastructure, alias de modèle ou mises à jour peuvent encore
modifier une réponse. C'est pourquoi le modèle et la variante sont enregistrés.

## Cycle d'amélioration

1. Formuler une hypothèse avant de modifier le prompt.
2. Créer ou compléter un cas d'évaluation représentatif.
3. Exécuter les trois variantes dans les mêmes conditions.
4. Comparer métriques et erreurs par cas.
5. Conserver le changement seulement si le gain ne dégrade pas un garde-fou.
6. Committer ensemble prompt, test et justification.

