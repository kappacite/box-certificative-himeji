# Suivi — Couche d'Accès aux Données (dao)

Cette partie contient les objets d'accès aux données (DAO) et les modèles ORM SQLAlchemy responsables uniquement de la persistance et de l'interrogation de la base de données SQLite.

---

## 📂 Fichiers concernés
* [backend/dao/database.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/database.py)
* [backend/dao/models.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/models.py)
* [backend/dao/base_dao.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/base_dao.py)
* [backend/dao/user_dao.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/user_dao.py)
* [backend/dao/place_dao.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/place_dao.py)
* [backend/dao/tour_dao.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/tour_dao.py)
* [backend/dao/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - La couche DAO a pour unique responsabilité d'exécuter des requêtes SQL (via l'ORM SQLAlchemy) et de mapper les résultats ORM vers les objets de données purs (`dataobject`). Elle ne contient aucun calcul d'optimisation ni aucune validation HTTP.
* **O — Open/Closed Principle (OCP)** :
  - L'interface abstraite et générique `BaseDAO[T, ID]` permet d'étendre facilement le système à de nouvelles entités. Si un nouveau modèle doit être persisté, il suffit de créer une sous-classe héritant de `BaseDAO` sans altérer le reste de l'infrastructure de persistance.
* **L — Liskov Substitution Principle (LSP)** :
  - Toutes les DAO concrètes (`UserDAO`, `PlaceDAO`, `TourDAO`) implémentent fidèlement les signatures de `BaseDAO` et retournent les objets attendus. Elles sont substituables à l'interface `BaseDAO` dans les services.
* **I — Interface Segregation Principle (ISP)** :
  - `BaseDAO` fournit un ensemble minimal et cohérent de méthodes CRUD (`get_by_id`, `get_all`, `create`, `update`, `delete`). Les clients n'utilisant qu'une partie de ces fonctionnalités ne sont pas encombrés de méthodes inutiles.
* **D — Dependency Inversion Principle (DIP)** :
  - Les DAO s'appuient sur l'abstraction générique `BaseDAO`. Les services métier peuvent ainsi dépendre de l'interface abstraite plutôt que des classes concrètes (injection de DAO mockées facilitée lors des tests unitaires).

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `database.py` | 🟢 Complet | Aucun. Prévient les dépendances d'importation circulaires. | RAS. |
| `models.py` | 🟢 Complet | Manque d'index explicites sur les clés étrangères et la colonne `share_token`. | Ajouter `index=True` sur les clés de jointure et sur le jeton de partage public dans `TourModel` pour optimiser les performances. |
| `base_dao.py` | 🟢 Complet | Interface générique robuste et documentée en style Google. | RAS. |
| `user_dao.py` | 🟢 Complet | Méthodes spécifiques `get_by_email` et `get_by_username` opérationnelles. | RAS. |
| `place_dao.py` | 🟢 Complet | Recherche par propriétaire (`get_by_owner`) opérationnelle. | RAS. |
| `tour_dao.py` | 🟢 Complet | L'opération `update` recrée l'ensemble des liaisons d'itinéraires en supprimant d'abord les anciennes de manière inconditionnelle. | Optimiser la méthode `update` pour ne modifier les liaisons que si l'ordre ou la liste des lieux a effectivement changé. |
