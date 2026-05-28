# Suivi — Algorithmes (services/algorithm)

Cette partie contient les modules de calculs mathématiques et d'optimisation (TSP) de l'application. Elle est isolée de toute considération HTTP ou de persistance de base de données.

---

## 📂 Fichiers concernés
* [backend/services/algorithm/distance.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/distance.py)
* [backend/services/algorithm/optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/optimizer.py)
* [backend/services/algorithm/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - `distance.py` a pour unique tâche le calcul de la distance orthodromique entre deux points de coordonnées.
  - `optimizer.py` a pour unique tâche de résoudre le problème du voyageur de commerce (TSP) pour une liste de lieux. Aucun de ces fichiers n'effectue d'appels à des bases de données ou à des APIs réseau.
* **O — Open/Closed Principle (OCP)** :
  - L'interface d'optimisation expose une fonction d'entrée unique `optimize(places)`. Le moteur de résolution interne (Nearest Neighbour combiné à 2-opt) peut être réécrit ou remplacé (ex: algorithme génétique ou recherche tabou) sans modifier la signature publique de la fonction ni impacter les couches supérieures.
* **L — Liskov Substitution Principle (LSP)** :
  - Les calculs reposent uniquement sur les abstractions de type `Place` (qui sont de simples structures de données). Toute extension de la classe `Place` sera supportée sans altérer le comportement des algorithmes.
* **I — Interface Segregation Principle (ISP)** :
  - Les modules exposent de simples fonctions ciblées au lieu de classes complexes avec des états internes volumineux, évitant ainsi d'imposer des dépendances d'interface inutiles.
* **D — Dependency Inversion Principle (DIP)** :
  - Les algorithmes ne dépendent d'aucune couche externe (ni de base de données, ni d'infrastructure). Ce sont des fonctions pures et autonomes qui se situent tout en bas de la pyramide des dépendances de l'application.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `distance.py` | 🟢 Complet | Risque d'erreur de domaine `math.acos` dû aux arrondis de précision des floats (sur deux points identiques). | *Corrigé* : Le paramètre d'entrée est désormais bridé avec `max(-1.0, min(1.0, cos_val))` avant l'appel à `acos`, ce qui prévient toute exception de calcul. |
| `optimizer.py` | 🟢 Complet | La complexité du 2-opt ($O(N^2)$) présente un risque d'épuisement de ressources CPU synchrone si la liste de lieux est trop grande. | Limiter le nombre maximum de lieux autorisés dans la couche route/service (ex: max 50 points par itinéraire). |
