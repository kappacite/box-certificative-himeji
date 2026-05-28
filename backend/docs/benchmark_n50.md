# Rapport de Test de Robustesse : 10 Simulations a N = 50

Ce rapport compile 10 tirages independants et aleatoires de 50 lieux parmi notre pool de 1000 destinations, comparant Google OR-Tools et Nearest Neighbour + 2-opt.

## 📊 Tableau des Resultats

| Run # | Dist OR-Tools (km) | Temps OR-Tools (ms) | Dist NN+2-Opt (km) | Temps NN+2-Opt (ms) | Gain Dist (km) | Gain (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 6513.81 | 62.57 | 6480.72 | 35.12 | -33.09 | -0.51% |
| 2 | 5775.30 | 64.39 | 5729.43 | 20.59 | -45.87 | -0.80% |
| 3 | 5790.66 | 82.40 | 6021.08 | 42.93 | 230.42 | 3.83% |
| 4 | 6115.71 | 60.13 | 6719.19 | 25.98 | 603.48 | 8.98% |
| 5 | 6388.46 | 69.30 | 6690.94 | 21.79 | 302.47 | 4.52% |
| 6 | 5944.64 | 63.89 | 6150.55 | 25.92 | 205.92 | 3.35% |
| 7 | 6561.51 | 62.42 | 6647.82 | 17.16 | 86.30 | 1.30% |
| 8 | 5971.28 | 70.11 | 6365.27 | 28.54 | 393.99 | 6.19% |
| 9 | 6402.93 | 47.98 | 6108.38 | 28.03 | -294.55 | -4.82% |
| 10 | 5751.37 | 54.51 | 5803.66 | 43.71 | 52.29 | 0.90% |

## 📈 Statistiques Globales (Synthese)

| Metrique | OR-Tools | NN + 2-opt | Difference / Amelioration |
| :--- | :---: | :---: | :---: |
| **Distance Moyenne** | 6121.57 km | 6271.70 km | OR-Tools reduit de 2.29% |
| **Temps Moyen** | 63.77 ms | 28.98 ms | OR-Tools prend +34.79 ms |
| **Distance Min / Max** | 5751.37 / 6561.51 km | 5729.43 / 6719.19 km | - |
| **Temps Min / Max** | 47.98 / 82.40 ms | 17.16 / 43.71 ms | - |

## 🔍 Observations & Analyse de robustesse :

- **Qualité des itinéraires** : Sur les 10 simulations, Google OR-Tools offre un gain moyen de **2.29%** sur la distance totale. Il obtient le meilleur itinéraire dans 70% des cas. Dans 30% des cas (Runs 1, 2, 9), NN + 2-opt trouve une distance légèrement plus courte, ce qui s'explique par le fait qu'OR-Tools utilise des distances entières à l'échelle (en mètres) et s'appuie sur une heuristique de premier choix (PATH_CHEAPEST_ARC), tandis que le 2-opt local explore en virgule flottante continue sur cette taille modérée.
- **Vitesse** : L'heuristique NN + 2-opt s'exécute en moyenne en 29.0 ms contre 63.8 ms pour OR-Tools, mais cette différence reste totalement invisible pour l'utilisateur final.
