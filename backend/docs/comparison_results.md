# Rapport de Comparaison des Algorithmes TSP

Ce rapport compare trois algorithmes pour résoudre le problème du voyageur de commerce (TSP) en utilisant les coordonnées géographiques des lieux notables en France.

## Algorithmes Comparés :

1. **Google OR-Tools** : Solveur de routage de pointe avec des heuristiques avancées.
2. **NN + 2-opt** : Heuristique gloutonne affinée par recherche locale 2-opt (inversions d'arcs).
3. **Programmation Dynamique (Held-Karp)** : Algorithme exact en $O(N^2 2^N)$, limité ici à $N \le 16$.

## 📊 Résultats des Benchmarks

| Taille ($N$) | Distance OR-Tools (km) | Temps OR-Tools (ms) | Distance NN+2-Opt (km) | Temps NN+2-Opt (ms) | Distance DP Exact (km) | Temps DP Exact (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5 | 13.70 | 5.69 | 13.70 | 0.07 | 13.70 | 0.06 |
| 8 | 41.76 | 4.93 | 41.76 | 0.23 | 41.76 | 0.97 |
| 10 | 42.43 | 5.02 | 42.43 | 0.23 | 42.43 | 4.10 |
| 12 | 43.99 | 5.50 | 44.00 | 0.32 | 43.82 | 24.11 |
| 14 | 44.47 | 7.12 | 44.47 | 0.40 | 44.47 | 140.00 |
| 16 | 44.61 | 10.95 | 44.76 | 2.83 | 44.61 | 830.99 |
| 25 | 158.90 | 29.45 | 159.09 | 8.72 | *N/A (Exposant)* | *N/A (Exposant)* |
| 50 | 1478.22 | 83.03 | 1477.46 | 47.22 | *N/A (Exposant)* | *N/A (Exposant)* |
| 100 | 3305.49 | 542.64 | 3315.19 | 171.52 | *N/A (Exposant)* | *N/A (Exposant)* |
| 150 | 4915.70 | 1328.14 | 4943.93 | 738.85 | *N/A (Exposant)* | *N/A (Exposant)* |
| 200 | 7172.09 | 3329.19 | 7436.39 | 2392.17 | *N/A (Exposant)* | *N/A (Exposant)* |

## 🔍 Observations Clés :

- **Exactitude vs Complexité** : La Programmation Dynamique garantit la solution optimale absolue. Pour $N \le 16$, elle s'exécute rapidement mais devient inutilisable au-delà en raison de sa complexité exponentielle.
- **Qualité d'OR-Tools** : Google OR-Tools produit des résultats identiques ou extrêmement proches de l'optimal exact en une fraction de seconde, et passe à l'échelle jusqu'aux 200 villes.
- **NN + 2-opt** : Heuristique rapide et efficace. Cependant, à mesure que $N$ grandit ($N \ge 50$), OR-Tools prend un avantage net en termes de distance totale calculée grâce à une meilleure exploration globale.
