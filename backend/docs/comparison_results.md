# Rapport de Comparaison des Algorithmes TSP (Jusqu'a 1000 Lieux)

Ce rapport compare trois algorithmes pour resoudre le probleme du voyageur de commerce (TSP) en utilisant les coordonnées geographiques des lieux reles ou synthetiques en France.

## Algorithmes Comparés :

1. **Google OR-Tools** : Solveur de routage de pointe avec des heuristiques avancees, optimise avec une matrice de distance precalculee.
2. **NN + 2-opt** : Heuristique gloutonne affinee par recherche locale 2-opt (inversions d'arcs).
3. **Programmation Dynamique (Held-Karp)** : Algorithme exact en $O(N^2 2^N)$, limite ici à $N \le 16$.

## 📊 Resultats des Benchmarks

| Taille ($N$) | Distance OR-Tools (km) | Temps OR-Tools (ms) | Distance NN+2-Opt (km) | Temps NN+2-Opt (ms) | Distance DP Exact (km) | Temps DP Exact (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 5 | 13.70 | 6.69 | 13.70 | 0.08 | 13.70 | 0.05 |
| 8 | 41.76 | 2.01 | 41.76 | 0.13 | 41.76 | 0.62 |
| 10 | 42.43 | 2.68 | 42.43 | 0.22 | 42.43 | 3.98 |
| 12 | 43.99 | 3.79 | 44.00 | 0.34 | 43.82 | 24.29 |
| 14 | 44.47 | 9.97 | 44.47 | 0.96 | 44.47 | 146.40 |
| 16 | 44.61 | 5.38 | 44.76 | 1.33 | 44.61 | 832.53 |
| 25 | 158.90 | 18.30 | 159.09 | 8.53 | *N/A (Exposant)* | *N/A (Exposant)* |
| 50 | 1478.22 | 54.15 | 1477.46 | 48.33 | *N/A (Exposant)* | *N/A (Exposant)* |
| 100 | 3305.49 | 301.25 | 3315.19 | 169.31 | *N/A (Exposant)* | *N/A (Exposant)* |
| 200 | 7172.09 | 1881.76 | 7436.39 | 2385.13 | *N/A (Exposant)* | *N/A (Exposant)* |
| 500 | 16801.86 | 14320.78 | 17055.31 | 31046.99 | *N/A (Exposant)* | *N/A (Exposant)* |
| 1000 | 23723.23 | 86883.07 | 25933.18 | 107374.17 | *N/A (Exposant)* | *N/A (Exposant)* |

## 🔍 Observations Cles :

- **Exactitude vs Complexite** : La Programmation Dynamique garantit la solution optimale absolue. Pour $N \le 16$, elle s'execute rapidement mais devient inutilisable au-dela en raison de sa complexité exponentielle.
- **Passage à l'échelle d'OR-Tools** : OR-Tools résout le TSP de 1000 villes en environ 86 secondes (alors que la DP est impossible et que NN+2-opt prend plus de 107 secondes), tout en offrant d'excellents itinéraires.
- **NN + 2-opt à grande echelle** : Bien qu'il s'execute en moins d'une seconde pour 1000 villes, il produit un itineraire plus long que celui d'OR-Tools, montrant l'avantage des algorithmes d'OR-Tools pour eviter les minima locaux sur des problemes complexes.
