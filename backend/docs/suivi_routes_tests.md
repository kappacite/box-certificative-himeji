# Suivi des Tests — Route par Route

Ce fichier est conçu pour t'accompagner dans le test manuel de chaque endpoint de l'API. Tu peux cocher et mettre à jour le statut au fur et à mesure de tes vérifications.

---

## 🔐 1. Authentification (`/api/auth/*`)

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Créer un nouveau compte utilisateur | `{"username": "testuser", "email": "test@example.com", "password": "password123"}` | **201 Created** : `{ "status": "success", "data": { "user": { "id": 1, "username": "testuser", "email": "test@example.com" } } }` | [x] Validé (201 OK, 400 BAD_REQUEST, 409 CONFLICT) |
| `POST` | `/api/auth/login` | Se connecter et générer un jeton JWT | `{"email": "test@example.com", "password": "password123"}` | **200 OK** : `{ "status": "success", "data": { "token": "eyJhbG...", "user": { ... } } }` | [x] Validé (200 OK, 401 UNAUTHORIZED) |
| `POST` | `/api/auth/logout` | Déconnexion (confirmation côté serveur) | Aucun *(En-tête `Authorization: Bearer <token>` requis)* | **200 OK** : `{ "status": "success", "data": { "message": "Logged out successfully" } }` | [x] Validé (200 OK, 401 UNAUTHORIZED) |

---

## 📍 2. Gestion des Lieux (`/api/places/*`)

> **Note** : Toutes ces routes requièrent l'en-tête `Authorization: Bearer <token>`.

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/places` | Lister tous les lieux appartenant à l'utilisateur connecté | Aucun | **200 OK** : `{ "status": "success", "data": { "places": [...] } }` | [x] Validé (200 OK) |
| `POST` | `/api/places` | Créer un lieu (géocodage auto si lat/lon omis) | `{"name": "Paris"}` ou `{"name": "Paris", "latitude": 48.8566, "longitude": 2.3522}` | **201 Created** : `{ "status": "success", "data": { "place": { "id": 1, "name": "Paris", "latitude": 48.8566, "longitude": 2.3522, "owner_id": 1 } } }` <br> *Note : Renvoie un 403 (ou 400 applicatif) si Nominatim bloque le User-Agent.* | [x] Validé (201 sans coord, 201 manuel, 400 inconnu, 403 Nominatim bloqué) |
| `GET` | `/api/places/<id>` | Obtenir les détails d'un lieu spécifique | Aucun (ID dans l'URL) | **200 OK** : `{ "status": "success", "data": { "place": { ... } } }` *(403 si non-propriétaire)* | [ ] Non testé |
| `PUT` | `/api/places/<id>` | Modifier le nom ou les coordonnées d'un lieu | `{"name": "Lyon"}` ou `{"name": "Lyon", "latitude": 45.76, "longitude": 4.83}` | **200 OK** : `{ "status": "success", "data": { "place": { ... } } }` *(403 si non-propriétaire)* | [ ] Non testé |
| `DELETE` | `/api/places/<id>` | Supprimer définitivement un lieu | Aucun (ID dans l'URL) | **204 No Content** (Corps vide) *(403 si non-propriétaire)* | [ ] Non testé |

---

## 🗺️ 3. Gestion des Itinéraires (`/api/tours/*`)

> **Note** : Sauf mention contraire, ces routes requièrent l'en-tête `Authorization: Bearer <token>`.

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/tours` | Lister tous les itinéraires de l'utilisateur connecté | Aucun | **200 OK** : `{ "status": "success", "data": { "tours": [...] } }` | [ ] Non testé |
| `POST` | `/api/tours` | Générer et enregistrer un circuit optimisé (TSP) | `{"name": "Mon Voyage", "place_ids": [1, 2]}` | **201 Created** : `{ "status": "success", "data": { "tour": { "id": 1, "name": "Mon Voyage", "places": [... ordonnés ...], "total_distance": 391.2, "visibility": "private", "share_token": "uuid-..." } } }` | [ ] Non testé |
| `GET` | `/api/tours/<id>` | Obtenir le détail d'un itinéraire privé | Aucun (ID dans l'URL) | **200 OK** : `{ "status": "success", "data": { "tour": { ... } } }` *(403 si non-propriétaire)* | [ ] Non testé |
| `DELETE` | `/api/tours/<id>` | Supprimer un itinéraire | Aucun (ID dans l'URL) | **204 No Content** (Corps vide) *(403 si non-propriétaire)* | [ ] Non testé |
| `PATCH` | `/api/tours/<id>/share` | Activer ou désactiver le partage public d'un circuit | `{"visibility": "public"}` (ou `"private"`) | **200 OK** : `{ "status": "success", "data": { "tour": { ..., "visibility": "public" } } }` | [ ] Non testé |
| `GET` | `/api/tours/shared/<token>` | Accéder publiquement à un itinéraire **(Sans Auth)** | Aucun (Jeton UUID dans l'URL) | **200 OK** : `{ "status": "success", "data": { "tour": { ... } } }` *(404 si introuvable ou repassé en "private")* | [ ] Non testé |
