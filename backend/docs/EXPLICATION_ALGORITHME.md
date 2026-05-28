# Algorithmes de Résolution du Voyageur de Commerce (TSP)

Ce document explique les concepts mathématiques et algorithmiques utilisés dans le backend pour calculer l'itinéraire optimal entre les différents lieux.

Le problème posé est une variante du **Problème du Voyageur de Commerce (TSP - Traveling Salesperson Problem)** : trouver le cycle le plus court passant exactement une fois par chaque lieu et revenant au point de départ.

---

## 1. Calcul des Distances : La Formule de Haversine

Pour calculer la distance réelle entre deux coordonnées géographiques (latitude/longitude) sur la Terre, nous utilisons la **formule de Haversine**. Elle calcule la distance du grand cercle (la plus courte distance à la surface d'une sphère) :

### Formule Mathématique
$$d = 2 R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1) \cos(\varphi_2) \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

Où :
* $\varphi_1, \varphi_2$ sont les latitudes en radians.
* $\lambda_1, \lambda_2$ sont les longitudes en radians.
* $\Delta \varphi = \varphi_2 - \varphi_1$ et $\Delta \lambda = \lambda_2 - \lambda_1$.
* $R$ est le rayon équatorial de la Terre, fixé précisément à **$6378.197$ km** selon le sujet.

### Implémentation
Le code est situé dans [services/algorithm/distance.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/distance.py) :

```python
import math

R_EARTH = 6378.197
PI = 3.141592

def to_rad(deg: float) -> float:
    return deg * (PI / 180.0)

def haversine(place_a, place_b) -> float:
    lat_a, lon_a = to_rad(place_a.latitude), to_rad(place_a.longitude)
    lat_b, lon_b = to_rad(place_b.latitude), to_rad(place_b.longitude)
    return R_EARTH * math.acos(
        math.sin(lat_a) * math.sin(lat_b)
        + math.cos(lat_a) * math.cos(lat_b) * math.cos(lon_b - lon_a)
    )
```

---

## 2. L'Algorithme Principal : Google OR-Tools (Production)

Pour la résolution en production (dans [services/algorithm/optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/optimizer.py)), le backend utilise **Google OR-Tools Routing**. Il combine des approches constructives robustes et de la programmation par contraintes.

### Stratégie Constructive : L'Algorithme de Christofides
Pour démarrer sa recherche, OR-Tools utilise l'heuristique de **Christofides** :
1. **Arbre Couvrant Minimal (MST)** : Calcule l'arbre couvrant de poids minimum reliant tous les sommets.
2. **Couplage Parfait** : Identifie les sommets de degré impair dans le MST et calcule un couplage parfait de poids minimum entre eux.
3. **Multi-graphe Eulerien** : Combine le MST et le couplage pour former un graphe où chaque sommet est de degré pair.
4. **Cycle Eulerien** : Trouve un circuit passant par toutes les arêtes.
5. **Raccourcis (Shortcuts)** : Transforme le circuit eulerien en cycle hamiltonien (TSP) en sautant les sommets déjà visités.

> [!TIP]
> **Christofides** garantit mathématiquement que la longueur du trajet trouvé est inférieure ou égale à **$1.5 \times$ la longueur optimale absolue** pour les espaces métriques.

---

## 3. Algorithmes de Benchmark et de Comparaison

Pour valider l'implémentation de production, deux autres algorithmes ont été écrits (situés dans [compare_algorithms.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/compare_algorithms.py)) :

### A. Nearest Neighbour + 2-opt (Heuristique Locale)
C'est l'approche heuristique classique :
1. **Nearest Neighbour (Voisin le plus proche)** : On part d'un point arbitraire, et on visite à chaque étape le point non visité le plus proche. Cela fournit une solution de départ rapide mais souvent imparfaite (avec des croisements de chemins).
2. **2-opt (Recherche locale)** : On parcourt l'itinéraire en essayant d'inverser des segments de trajet. Si l'inversion d'un segment reliant les arcs $(i, i+1)$ et $(j, j+1)$ par les arcs $(i, j)$ et $(i+1, j+1)$ diminue la distance totale (en éliminant un croisement), on valide l'inversion. On répète l'opération jusqu'à ce qu'aucune amélioration locale ne soit possible.

```
Cycle avec croisement :      Cycle amélioré (2-opt) :
    A --- B                      A     B
     \   /                        \   /
      \ /        ===========>      \ /
       X                          (Décroisement des arcs)
      / \                          / \
     /   \                        /   \
    C --- D                      C     D
```

### B. Programmation Dynamique (Held-Karp) - Résolution Exacte
Pour obtenir la solution optimale absolue à des fins de comparaison, l'algorithme exact de **Held-Karp** est utilisé :
* Il résout le problème en décomposant les sous-trajets à l'aide de la programmation dynamique.
* **Complexité temporelle** : $O(N^2 2^N)$.
* **Limitation** : Du fait de son coût exponentiel en temps et en mémoire, il est limité dans le code aux itinéraires de taille **$N \le 16$**. Au-delà, le temps de calcul et l'empreinte mémoire provoqueraient un crash du système.

---

## 4. Synthèse des Complexités

| Algorithme | Type | Complexité Temporelle | Idéal Pour |
| :--- | :---: | :---: | :---: |
| **Held-Karp (DP)** | Exact | $O(N^2 2^N)$ | Très petites tournées ($N \le 16$) |
| **Google OR-Tools** | Heuristique de pointe | Très rapide (Heuristique + Contraintes) | Production, de $5$ à $1000+$ lieux |
| **Nearest Neighbour + 2-opt** | Heuristique locale | $O(N^2)$ par itération | Benchmark et validation |
