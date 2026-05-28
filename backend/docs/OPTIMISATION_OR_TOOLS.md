# Optimisation du Solveur Google OR-Tools

Ce document détaille les optimisations apportées à l'implémentation de Google OR-Tools au sein du service de planification de tournées (TSP). Ces optimisations visent à maximiser la vitesse d'exécution pour s'approcher de celle du Nearest Neighbour tout en conservant (et améliorant) la précision globale.

---

## 1. Contexte & Problématique initiale

OR-Tools est un solveur de recherche opérationnelle écrit en C++. 
Dans l'implémentation initiale, le calcul de la distance entre deux lieux s'effectuait par le biais d'un **callback Python** appelé à chaque fois que le solveur évaluait une transition :

```python
# CODE NON OPTIMISÉ (Callback dynamique)
def distance_callback(from_index: int, to_index: int) -> int:
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    # L'appel à la fonction Python haversine se répète des millions de fois
    return int(haversine(places[from_node], places[to_node]) * 1000)

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
```

### Le problème : L'overhead de liaison
Puisque le solveur s'exécute en C++ natif, chaque appel à `distance_callback` obligeait le programme à franchir la frontière C++/Python (via SWIG). Multiplié par le nombre d'arcs évalués dans le graphe, cet "overhead" représentait plus de **80% du temps de calcul total** sur de grandes tailles d'itinéraires.

---

## 2. Optimisations implémentées

Deux améliorations majeures ont été apportées dans [services/algorithm/optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/optimizer.py).

### A. Chargement de la matrice de distances en mémoire native (`RegisterTransitMatrix`)
Pour éliminer les appels répétés à Python, nous calculons au préalable la matrice de distance complète en $O(N^2)$ en Python. Cette matrice d'entiers est passée en une seule fois au solveur :

```python
# CODE OPTIMISÉ (Matrice directe)
dist_matrix = [
    [int(haversine(places[i], places[j]) * 1000) for j in range(num_places)]
    for i in range(num_places)
]

# Enregistrement direct sans callback dynamique
transit_callback_index = routing.RegisterTransitMatrix(dist_matrix)
```
**Bénéfice** : OR-Tools accède désormais aux distances à la vitesse du C++ compilé, sans aucun appel au runtime Python.

### B. Changement de l'heuristique de démarrage (`CHRISTOFIDES`)
Au lieu de la stratégie par défaut `PATH_CHEAPEST_ARC` (gloutonne), nous utilisons la stratégie de **Christofides** :

```python
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
)
```
**Bénéfice** : L'algorithme de Christofides est conçu pour les espaces métriques (comme les coordonnées GPS). Il offre une garantie mathématique de trouver une solution de départ à moins de $1,5 \times$ de l'optimum. En partant d'une solution de meilleure qualité, le solveur converge beaucoup plus rapidement.

---

## 3. Impact sur les Performances (Avant vs Après)

Les résultats compilés ci-dessous proviennent de simulations réelles effectuées sur les scripts de benchmark :

### Comparatif Temps de Calcul moyen
| Taille de l'itinéraire ($N$) | Avant (Callback) | Après (Matrice Directe) | NN + 2-opt (Python) | Rapport de Vitesse |
| :--- | :---: | :---: | :---: | :---: |
| **$N = 25$** | 12.66 ms | **4.31 ms** | 3.80 ms | ~3x plus rapide |
| **$N = 50$** | 57.03 ms | **15.14 ms** | 27.89 ms | **~4x plus rapide** |
| **$N = 100$** | ~280 ms | **69.99 ms** | 177.75 ms | ~4x plus rapide |
| **$N = 250$** | ~3100 ms | **666.95 ms** | 3352.82 ms | **~5x plus rapide** |

> [!NOTE]
> À partir de $N=50$, OR-Tools devient **plus rapide** que notre implémentation locale `NN + 2-opt` écrite en Python, tout en trouvant des trajets nettement plus courts.

### Gain de Distance Moyen (Précision accrue)
Grâce à la stratégie Christofides, la précision géométrique globale s'est également améliorée :
* **N = 25** : OR-Tools réduit la distance de **2.04%** face à NN+2-opt (contre 1.74% auparavant).
* **N = 50** : OR-Tools réduit la distance de **3.00%** face à NN+2-opt (contre 2.00% auparavant).
* **N = 250** : OR-Tools réduit la distance de **4.78%** face à NN+2-opt, avec un taux de victoire de 100%.

---

## 4. Synthèse des modifications
* **Fichier de production mis à jour** : [services/algorithm/optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/optimizer.py)
* **Script de benchmark mis à jour** : [compare_algorithms.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/compare_algorithms.py)
* **Nouveau script de test de charge** : [benchmark_n100_n250.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/benchmark_n100_n250.py)
* **Rapports associés** : 
  - [docs/benchmark_100_runs.md](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/benchmark_100_runs.md) (N=25 et N=50)
  - [docs/benchmark_n100_n250.md](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/benchmark_n100_n250.md) (N=100 et N=250)
