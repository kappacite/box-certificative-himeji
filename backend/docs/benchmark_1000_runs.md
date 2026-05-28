# Rapport de Test de Robustesse Massif : 1000 Runs à N=5 et N=10

Ce rapport présente l'analyse statistique agrégée de 1000 simulations aléatoires et indépendantes pour de petites tailles d'itinéraires ($N=5$ et $N=10$). Il permet d'étudier le comportement d'OR-Tools (configuré avec `RegisterTransitMatrix` et `Christofides`) face à `NN+2-opt` à très petite échelle.

## 📊 Résultats pour N = 5 lieux

- **Nombre de simulations** : 1000
- **Victoires OR-Tools (itinéraire plus court)** : **23 / 1000**
- **Victoires NN + 2-opt (itinéraire plus court)** : 0 / 1000
- **Égalités strictes** : 977 / 1000

| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 2109.45 km | 2110.79 km | OR-Tools réduit de 0.06% |
| **Temps Moyen de Calcul** | 0.87 ms | 0.05 ms | Différence de +0.82 ms |
| **Distance Min / Max** | 695.36 / 3271.06 km | 695.36 / 3336.87 km | -
| **Temps Min / Max** | 0.72 / 8.33 ms | 0.03 / 0.15 ms | -

## 📊 Résultats pour N = 10 lieux

- **Nombre de simulations** : 1000
- **Victoires OR-Tools (itinéraire plus court)** : **213 / 1000**
- **Victoires NN + 2-opt (itinéraire plus court)** : 23 / 1000
- **Égalités strictes** : 764 / 1000

| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 2864.22 km | 2884.14 km | OR-Tools réduit de 0.69% |
| **Temps Moyen de Calcul** | 1.22 ms | 0.26 ms | Différence de +0.96 ms |
| **Distance Min / Max** | 1670.92 / 3943.73 km | 1670.92 / 3943.73 km | -
| **Temps Min / Max** | 1.04 / 4.15 ms | 0.13 / 0.83 ms | -

## 🔍 Analyse Comparative et Robustesse :

- **Taux d'Égalités Élevé à N=5** : À $N=5$, il y a **97.7%** d'égalités strictes entre les deux algorithmes. À cette échelle, le nombre de permutations possibles est très réduit ($5! = 120$) et les deux heuristiques trouvent presque toujours le même chemin optimal.
- **Écart à N=10** : À $N=10$ ($10! \approx 3.6$ millions de permutations), les égalités chutent à **76.4%**. OR-Tools gagne dans **21.3%** des cas (gain de 0.69% de distance en moyenne), ce qui montre que même sur des problèmes de taille modeste, OR-Tools commence à faire la différence.
- **Efficacité Temporelle** : Pour $N=5$, OR-Tools s'exécute en moyenne en **0.87 ms** (contre 0.05 ms pour NN+2-opt). Pour $N=10$, il met **1.22 ms** (contre 0.26 ms pour NN+2-opt). Ces temps sont extrêmement faibles et garantissent une réactivité totale de l'API.

