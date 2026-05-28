# Suivi — Services Métier (services)

Cette partie contient la couche de logique métier (services), responsable de l'orchestration entre les DAO (accès aux données) et les algorithmes de calcul.

---

## 📂 Fichiers concernés
* [backend/services/auth_service.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/auth_service.py)
* [backend/services/place_service.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/place_service.py)
* [backend/services/tour_service.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/tour_service.py)
* [backend/services/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - Chaque service a un domaine de responsabilité distinct : `AuthService` (sessions utilisateurs, hachage, tokens JWT), `PlaceService` (gestion des points d'intérêt, géocodage Nominatim) et `TourService` (orchestration de l'optimisation, calculs de distance globaux, jetons de partage). Ils ne traitent aucun routage HTTP ni aucune requête SQL brute.
* **O — Open/Closed Principle (OCP)** :
  - Les méthodes des services sont conçues pour être extensibles. L'ajout d'une nouvelle règle métier (ex: validation de mot de passe plus stricte ou vérification de doublons de lieux) s'effectue localement sans modifier la structure des autres services ni de la couche HTTP.
* **L — Liskov Substitution Principle (LSP)** :
  - Les services interagissent via des interfaces typées claires. Aucun héritage complexe n'est utilisé ici, favorisant la simplicité et la robustesse du typage.
* **I — Interface Segregation Principle (ISP)** :
  - Les services exposent des méthodes publiques ciblées correspondant précisément aux cas d'utilisation métier requis par l'application (ex: `login`, `register`, `geocode_place_name`).
* **D — Dependency Inversion Principle (DIP)** :
  - Les services reçoivent leurs DAO en paramètre de constructeur (Dependency Injection) :
    `def __init__(self, user_dao: UserDAO = None): self.user_dao = user_dao or UserDAO()`
    Cela permet de découpler totalement la logique métier de la base de données et de pouvoir substituer les DAO réelles par des mocks/stubs lors des tests unitaires, respectant le principe d'inversion des dépendances.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `auth_service.py` | 🟢 Complet | La durée d'expiration du jeton (24h) est codée en dur par défaut dans l'environnement. | Rendre ce paramètre entièrement configurable depuis le fichier d'environnement `.env`. |
| `place_service.py` | 🟢 Complet | L'appel synchrone au service externe Nominatim (sans cache) ralentit la création de lieux et peut être bloqué par les limites de requêtes (rate-limiting). | Implémenter une table SQL locale de cache pour les requêtes Nominatim (`GeocodingCache`) afin d'accélérer l'expérience utilisateur et fiabiliser l'API en mode déconnecté. |
| `tour_service.py` | 🟢 Complet | Aucun contrôle de limite supérieure sur le nombre de lieux associés à un itinéraire à optimiser. | Ajouter une validation imposant un nombre de lieux maximum (ex: 50) pour protéger le serveur d'une surcharge CPU synchrone. |
