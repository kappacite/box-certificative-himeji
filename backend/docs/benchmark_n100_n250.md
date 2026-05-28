# Rapport de Benchmark Comparatif : N=100 et N=250 (10 Iterations)

Ce rapport presente l'analyse comparative et de performance detaillee pour deux tailles d'itineraires significatives ($N=100$ et $N=250$), realisee sur 10 simulations aleatoires. Il met en evidence les gains de performance et de precision de l'algorithme Google OR-Tools (optimise avec `RegisterTransitMatrix` et la strategie `Christofides`) face à notre heuristique custom `NN + 2-opt`.

## 📊 Résultats détaillés pour N = 100 lieux

- **Nombre d'itérations** : 10
- **Victoires OR-Tools (itinéraire plus court)** : **8 / 10**
- **Victoires NN + 2-opt (itinéraire plus court)** : 2 / 10
- **Égalités** : 0 / 10

| Run | Dist OR-Tools (km) | Temps OR-Tools (ms) | Dist NN+2-Opt (km) | Temps NN+2-Opt (ms) | Gain (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | 8168.80 | 69.40 | 8105.41 | 228.65 | -0.78% |
| 2 | 7861.42 | 65.31 | 8122.65 | 165.86 | 3.22% |
| 3 | 7784.64 | 65.75 | 7855.74 | 131.74 | 0.90% |
| 4 | 7846.76 | 79.30 | 8150.67 | 152.52 | 3.73% |
| 5 | 8696.04 | 62.43 | 8999.51 | 142.91 | 3.37% |
| 6 | 8016.45 | 55.67 | 8793.82 | 280.90 | 8.84% |
| 7 | 8035.73 | 112.03 | 8569.41 | 158.30 | 6.23% |
| 8 | 8041.11 | 54.52 | 8349.22 | 272.21 | 3.69% |
| 9 | 8319.17 | 67.71 | 8688.51 | 182.17 | 4.25% |
| 10 | 8474.49 | 67.81 | 8451.92 | 62.23 | -0.27% |

### Synthèse des Métriques :

| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 8124.46 km | 8408.69 km | OR-Tools réduit de 3.38% |
| **Temps Moyen de Calcul** | 69.99 ms | 177.75 ms | Différence de -107.76 ms |
| **Distance Min / Max** | 7784.64 / 8696.04 km | 7855.74 / 8999.51 km | -
| **Temps Min / Max** | 54.52 / 112.03 ms | 62.23 / 280.90 ms | -

## 📊 Résultats détaillés pour N = 250 lieux

- **Nombre d'itérations** : 10
- **Victoires OR-Tools (itinéraire plus court)** : **10 / 10**
- **Victoires NN + 2-opt (itinéraire plus court)** : 0 / 10
- **Égalités** : 0 / 10

| Run | Dist OR-Tools (km) | Temps OR-Tools (ms) | Dist NN+2-Opt (km) | Temps NN+2-Opt (ms) | Gain (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | 12045.66 | 640.72 | 12737.44 | 2452.93 | 5.43% |
| 2 | 12258.64 | 567.63 | 12654.42 | 3822.00 | 3.13% |
| 3 | 12414.77 | 704.17 | 13144.87 | 2814.05 | 5.55% |
| 4 | 12281.15 | 458.10 | 12592.34 | 3178.23 | 2.47% |
| 5 | 12438.91 | 576.99 | 12886.46 | 3692.93 | 3.47% |
| 6 | 12057.00 | 641.71 | 12695.05 | 3643.31 | 5.03% |
| 7 | 12201.09 | 572.00 | 13044.14 | 3030.16 | 6.46% |
| 8 | 11957.10 | 791.90 | 12723.12 | 3056.90 | 6.02% |
| 9 | 12237.55 | 892.71 | 12884.70 | 3188.34 | 5.02% |
| 10 | 12126.13 | 823.59 | 12783.68 | 4649.37 | 5.14% |

### Synthèse des Métriques :

| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 12201.80 km | 12814.62 km | OR-Tools réduit de 4.78% |
| **Temps Moyen de Calcul** | 666.95 ms | 3352.82 ms | Différence de -2685.87 ms |
| **Distance Min / Max** | 11957.10 / 12438.91 km | 12592.34 / 13144.87 km | -
| **Temps Min / Max** | 458.10 / 892.71 ms | 2452.93 / 4649.37 ms | -

## 🔍 Analyse & Conclusion :

- **Efficacité de la recherche** : À $N=100$, OR-Tools obtient un itinéraire plus court dans **80%** des cas avec un gain moyen de 3.38%. À $N=250$, l'hégémonie d'OR-Tools est totale (**100%** de victoires) avec un gain moyen de 4.78% de distance économisée.
- **Vitesse d'exécution** : Grâce au passage de la matrice directe (`RegisterTransitMatrix`), OR-Tools est non seulement plus précis, mais il surpasse également `NN + 2-opt` en vitesse :
  - À $N=100$, OR-Tools s'exécute en **69.99 ms** en moyenne (contre 177.75 ms pour NN+2-opt).
  - À $N=250$, OR-Tools résout le problème en **666.95 ms** (contre 3352.82 ms pour NN+2-opt, soit un gain de temps très important).
- **Conclusion** : L'optimisation consistant à éliminer les callbacks Python a transformé la performance d'OR-Tools. Celui-ci est désormais la solution optimale à tous les niveaux, alliant la rapidité fulgurante du C++ à la précision des heuristiques avancées (Christofides).

