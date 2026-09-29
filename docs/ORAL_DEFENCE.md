# Guide de soutenance

## Démonstration proposée — 7 minutes

### 0:00–0:45 — Problème

« Un compte rendu contient des décisions et actions, mais les transformer en
suivi structuré à la main est lent. Le risque principal n'est pas seulement de
manquer une action : c'est d'en inventer une ou de lui attribuer le mauvais
responsable. MinuteGuard privilégie donc la traçabilité. »

### 0:45–1:30 — Architecture

Montrer le schéma dans `docs/ARCHITECTURE.md`. Expliquer : application pilotée
par prompt, pas agent autonome ; JSON strict ; validation locale ; revue humaine.

### 1:30–2:30 — Git et reproductibilité

```bash
git log --graph --oneline --decorate --all
make test
```

Montrer les commits atomiques, la branche fusionnée, la couverture minimale de
90 % et l'absence de secret.

### 2:30–4:00 — Démo

```bash
make demo
```

Ouvrir `outputs/runs/demo.md`. Relier une action à sa ligne source. Montrer que
la proposition Paris n'est pas une décision et que l'injection concernant Marc
n'est pas suivie.

### 4:00–5:15 — Prompt engineering

Comparer `zero_shot.md`, `few_shot.md` et `deliberative.md`. Justifier la
persona, la séparation des rôles, le schéma, les champs nullables et le choix de
température. Mentionner le coût en tokens du few-shot.

### 5:15–6:15 — Évaluation

```bash
make evaluate
```

Expliquer F1, exactitude des champs, ancrage et poids définis avant le test.
Dire explicitement que le score de fixture vérifie le calcul, pas le modèle.

### 6:15–7:00 — Limites

Présenter un risque résiduel : une vraie citation peut être mal interprétée.
Conclure par l'amélioration prioritaire : exécuter le benchmark réel sur davantage
de comptes rendus annotés par deux personnes.

## Questions probables

**Pourquoi pas un agent ?**  
La tâche est bornée et n'exige aucun choix d'outil. Un agent ajouterait autonomie,
coût et surface d'attaque sans bénéfice démontré.

**Pourquoi le même texte peut-il produire deux réponses ?**  
Le modèle échantillonne des tokens successifs. Température, top-p, état du
service et version du modèle influencent la trajectoire. Température 0 réduit la
variabilité sans la supprimer absolument.

**Pourquoi Structured Outputs ?**  
Le schéma garantit la forme attendue et simplifie le parsing. Une seconde
validation Pydantic protège aussi le reste de l'application.

**Que se passe-t-il lors d'un 429 ?**  
Les retries automatiques du SDK sont désactivés. L'application respecte
`Retry-After` lorsqu'il est raisonnable, sinon utilise un backoff exponentiel
avec jitter, au maximum quatre tentatives. Les erreurs de quota ou
d'authentification ne sont pas réessayées.

**La citation élimine-t-elle les hallucinations ?**  
Non. Elle empêche une preuve entièrement fabriquée de passer le filtre, mais une
citation réelle peut soutenir une mauvaise interprétation.

**Comment choisir le meilleur prompt ?**  
Même jeu, même modèle, conditions identiques, métriques définies à l'avance et
analyse des erreurs. À performance égale, choisir le prompt le plus court.

**Quel est le résultat le plus honnête aujourd'hui ?**  
Le logiciel et la métrique sont vérifiés hors ligne. La performance réelle d'un
modèle doit encore être mesurée avec une clé API et un corpus plus large.

