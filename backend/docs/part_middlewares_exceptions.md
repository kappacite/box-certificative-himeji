# Suivi — Middlewares et Exceptions

Cette partie regroupe les middlewares Flask de gestion de requêtes (sécurité, authentification, vérification de propriété) et les exceptions personnalisées du projet.

---

## 📂 Fichiers concernés
* [backend/exceptions/app_exceptions.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/exceptions/app_exceptions.py)
* [backend/exceptions/auth_exceptions.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/exceptions/auth_exceptions.py)
* [backend/exceptions/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/exceptions/__init__.py)
* [backend/middleware/auth_middleware.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/middleware/auth_middleware.py)
* [backend/middleware/error_handler.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/middleware/error_handler.py)
* [backend/middleware/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/middleware/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - Les exceptions modélisent uniquement des anomalies typées avec un statut HTTP et un code d'erreur (`NotFoundException`, `ForbiddenException`, etc.).
  - `auth_middleware.py` gère exclusivement la vérification des droits (JWT valide, propriété du ressource).
  - `error_handler.py` gère uniquement le reformatage des exceptions Python en réponses HTTP normalisées.
* **O — Open/Closed Principle (OCP)** :
  - La structure des exceptions permet d'ajouter une nouvelle classe d'erreur (ex: `PaymentRequiredException` ou `TooManyRequestsException`) par simple héritage de la classe de base sans perturber le fonctionnement du gestionnaire global `error_handler.py`.
* **L — Liskov Substitution Principle (LSP)** :
  - Toutes les exceptions personnalisées héritent de `Exception` et exposent des attributs communs (`status_code` et `code`). Elles peuvent donc être interceptées indifféremment par le middleware de gestion des erreurs (`error_handler`).
* **I — Interface Segregation Principle (ISP)** :
  - Les décorateurs d'authentification (`@require_auth`, `@require_owner`) sont granulaires. Les routes n'appliquant que l'authentification ne sont pas forcées d'importer ou de subir les vérifications de propriété.
* **D — Dependency Inversion Principle (DIP)** :
  - `error_handler.py` dépend de l'abstraction `Exception` et inspecte dynamiquement la présence des propriétés `status_code` et `code`, permettant à l'application de ne pas être couplée de manière rigide aux implémentations spécifiques d'erreurs.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `exceptions` | 🟢 Complet | RAS. | RAS. |
| `auth_middleware.py` | 🟢 Complet | Le décorateur `@require_owner` instancie dynamiquement les services en dur (`PlaceService` et `TourService`) à chaque appel de route. | Centraliser la validation de propriété ou utiliser un conteneur de services pour injecter les instances nécessaires plutôt que de faire des imports locaux tardifs. |
| `error_handler.py` | 🟢 Complet | Les erreurs critiques serveurs (500) sont tracées avec la fonction `logger.error` standard mais mériteraient des informations contextuelles supplémentaires (ex: ID de la requête, IP du client). | Enrichir les logs système des erreurs 500 pour faciliter le débogage en production. |
