# Suivi — Suite de Tests (tests)

Cette partie contient la suite de tests automatisée du projet (tests unitaires de logique pure et tests d'intégration des routes avec une base de données en mémoire).

---

## 📂 Fichiers concernés
* [backend/tests/conftest.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/conftest.py)
* [backend/tests/unit/test_distance.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/unit/test_distance.py)
* [backend/tests/unit/test_optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/unit/test_optimizer.py)
* [backend/tests/unit/test_auth_service.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/unit/test_auth_service.py)
* [backend/tests/integration/test_auth_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/integration/test_auth_routes.py)
* [backend/tests/integration/test_place_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/integration/test_place_routes.py)
* [backend/tests/integration/test_tour_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/integration/test_tour_routes.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - Chaque fichier de test a pour unique rôle de valider un périmètre restreint et clair : `test_distance` teste la formule de Haversine, `test_optimizer` valide le TSP, les tests de routes simulent des requêtes HTTP et comparent les codes de retour et enveloppes.
* **O — Open/Closed Principle (OCP)** :
  - La suite de tests tire profit du fichier global [tests/conftest.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/tests/conftest.py) fournissant des fixtures réutilisables (client de test, configuration de base de données). L'ajout de nouveaux tests ou l'intégration d'un nouveau cas d'utilisation s'effectue sans modifier les tests préexistants.
* **L — Liskov Substitution Principle (LSP)** :
  - La configuration de test remplace de façon transparente la base SQLite de développement par une base SQLite en mémoire (`sqlite:///:memory:`) sans altérer le comportement logique de l'ORM ou de la DAO.
* **I — Interface Segregation Principle (ISP)** :
  - Les fixtures sont injectées de manière sélective dans chaque fonction de test via pytest (ex: les tests unitaires de calcul n'importent pas la fixture de base de données ni celle de client HTTP).
* **O — Dependency Inversion Principle (DIP)** :
  - Les appels réseau à l'API géocodage externe Nominatim sont interceptés et simulés avec une fixture de mock de requêtes (`mock_geocoding` via monkeypatch), éliminant toute dépendance vis-à-vis d'une connexion internet externe pour garantir des tests rapides et déterministes.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `conftest.py` | 🟢 Complet | RAS. Gère correctement l'initialisation et la destruction de la DB à chaque test. | RAS. |
| `test_distance.py` | 🟢 Complet | RAS. Couvre les calculs limites (antipodes) et les points identiques. | RAS. |
| `test_optimizer.py` | 🟢 Complet | RAS. Teste les cas dégénérés (0 ou 1 ville) et la réduction effective de distance du 2-opt. | RAS. |
| `test_auth_service.py` | 🟢 Complet | RAS. Teste le chiffrement bcrypt et la signature JWT. | RAS. |
| `test_auth_routes.py` | 🟢 Complet | RAS. Valide les codes status (200, 201, 400, 401). | RAS. |
| `test_place_routes.py` | 🟢 Complet | RAS. Valide le geocoding fictif mocké et l'erreur en cas de ville inconnue. | RAS. |
| `test_tour_routes.py` | 🟢 Complet | RAS. Valide l'optimisation complète de circuit et l'autorisation d'accès par token partagé. | RAS. |
