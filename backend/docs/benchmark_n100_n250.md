# Rapport de Benchmark Comparatif : N=100 et N=250 (10 Iterations)

Ce rapport presente l'analyse comparative et de performance detaillee pour deux tailles d'itineraires significatives ($N=100$ et $N=250$), realisee sur 10 simulations aleatoires. Il met en evidence les gains de performance et de precision de l'algorithme Google OR-Tools (optimise avec `RegisterTransitMatrix` et la strategie `Christofides`) face à notre heuristique custom `NN + 2-opt`.

## 📊 Résultats détaillés pour N = 100 lieux

- **Nombre d'itérations** : 10
- **Victoires OR-Tools (itinéraire plus court)** : **8 / 10**
- **Victoires NN + 2-opt (itinéraire plus court)** : 2 / 10
- **Égalités** : 0 / 10


| Run | Dist OR-Tools (km) | Temps OR-Tools (ms) | Dist NN+2-Opt (km) | Temps NN+2-Opt (ms) | Gain (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |

| 1 | 8168.80 | 66.74 | 8105.41 | 228.97 | -0.78% |

| 2 | 7861.42 | 65.46 | 8122.65 | 166.38 | 3.22% |

| 3 | 7784.64 | 65.78 | 7855.74 | 131.56 | 0.90% |

| 4 | 7846.76 | 67.96 | 8150.67 | 156.04 | 3.73% |

| 5 | 8696.04 | 61.15 | 8999.51 | 142.13 | 3.37% |

| 6 | 8016.45 | 59.87 | 8793.82 | 282.29 | 8.84% |

| 7 | 8035.73 | 96.24 | 8569.41 | 162.19 | 6.23% |

| 8 | 8041.11 | 62.30 | 8349.22 | 276.43 | 3.69% |

| 9 | 8319.17 | 68.49 | 8688.51 | 183.48 | 4.25% |

| 10 | 8474.49 | 57.27 | 8451.92 | 62.03 | -0.27% |



### Synthèse des Métriques :


| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 8124.46 km | 8408.69 km | OR-Tools réduit de 3.38% |
| **Temps Moyen de Calcul** | 67.13 ms | 179.15 ms | Différence de -112.02 ms |
| **Distance Min / Max** | 7784.64 / 8696.04 km | 7855.74 / 8999.51 km | -
| **Temps Min / Max** | 57.27 / 96.24 ms | 62.03 / 282.29 ms | -




## 📊 Résultats détaillés pour N = 250 lieux

- **Nombre d'itérations** : 10
- **Victoires OR-Tools (itinéraire plus court)** : **10 / 10**
- **Victoires NN + 2-opt (itinéraire plus court)** : 0 / 10
- **Égalités** : 0 / 10


| Run | Dist OR-Tools (km) | Temps OR-Tools (ms) | Dist NN+2-Opt (km) | Temps NN+2-Opt (ms) | Gain (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |

| 1 | 12045.66 | 642.11 | 12737.44 | 2482.94 | 5.43% |

| 2 | 12258.64 | 587.98 | 12654.42 | 3830.41 | 3.13% |

| 3 | 12414.77 | 717.99 | 13144.87 | 2820.53 | 5.55% |

| 4 | 12281.15 | 461.32 | 12592.34 | 3165.68 | 2.47% |

| 5 | 12438.91 | 571.21 | 12886.46 | 3683.08 | 3.47% |

| 6 | 12057.00 | 634.83 | 12695.05 | 3660.47 | 5.03% |

| 7 | 12201.09 | 574.37 | 13044.14 | 3025.57 | 6.46% |

| 8 | 11957.10 | 783.21 | 12723.12 | 3071.17 | 6.02% |

| 9 | 12237.55 | 859.10 | 12884.70 | 3171.63 | 5.02% |

| 10 | 12126.13 | 763.09 | 12783.68 | 4705.15 | 5.14% |



### Synthèse des Métriques :


| Métrique | Google OR-Tools | NN + 2-opt | Différence / Amélioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 12201.80 km | 12814.62 km | OR-Tools réduit de 4.78% |
| **Temps Moyen de Calcul** | 659.52 ms | 3361.66 ms | Différence de -2702.14 ms |
| **Distance Min / Max** | 11957.10 / 12438.91 km | 12592.34 / 13144.87 km | -
| **Temps Min / Max** | 461.32 / 859.10 ms | 2482.94 / 4705.15 ms | -




## 🔍 Analyse & Conclusion :

- **Efficacité de la recherche** : À $N=100$, OR-Tools obtient un itinéraire plus court dans **80%** des cas avec un gain moyen de 3.38%. À $N=250$, l'hégémonie d'OR-Tools est totale (**100%** de victoires) avec un gain moyen de 4.78% de distance économisée.
- **Vitesse d'exécution** : Grâce au passage de la matrice directe (`RegisterTransitMatrix`), OR-Tools est non seulement plus précis, mais il surpasse également `NN + 2-opt` en vitesse :
  - À $N=100$, OR-Tools s'exécute en **67.13 ms** en moyenne (contre 179.15 ms pour NN+2-opt).
  - À $N=250$, OR-Tools résout le problème en **659.52 ms** (contre 3361.66 ms pour NN+2-opt, soit un gain de temps très important).
- **Conclusion** : L'optimisation consistant à éliminer les callbacks Python a transformé la performance d'OR-Tools. Celui-ci est désormais la solution optimale à tous les niveaux, alliant la rapidité fulgurante du C++ à la précision des heuristiques avancées (Christofides).
