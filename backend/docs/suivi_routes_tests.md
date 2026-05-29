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

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/places` | Lister tous les lieux appartenant à l'utilisateur connecté | Aucun *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "places": [...] } }` | [x] Validé (200 OK) |
| `GET` | `/api/places/public` | Lister tous les lieux publics **(Sans Auth)** | Aucun | **200 OK** : `{ "status": "success", "data": { "places": [...] } }` | [x] Validé (200 OK) |
| `POST` | `/api/places` | Créer un lieu (géocodage auto si lat/lon omis) | `{"name": "Paris", "visibility": "public"}` | **201 Created** : `{ "status": "success", "data": { "place": { "id": 1, "name": "Paris", "latitude": 48.8566, "longitude": 2.3522, "owner_id": 1, "visibility": "public" } } }` | [x] Validé (201 sans coord, 201 manuel, 400 inconnu, 403 Nominatim bloqué, visibilité prise en compte) |
| `GET` | `/api/places/<id>` | Obtenir les détails d'un lieu spécifique | Aucun (ID dans l'URL) *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "place": { ... } } }` | [x] Validé (200 OK, 403 Forbidden si privé et possédé par autrui) |
| `PUT` | `/api/places/<id>` | Modifier le nom, les coordonnées ou la visibilité d'un lieu | `{"name": "Lyon", "visibility": "public"}` | **200 OK** : `{ "status": "success", "data": { "place": { ... } } }` | [x] Validé (200 OK, 403 Forbidden si non-propriétaire) |
| `DELETE` | `/api/places/<id>` | Supprimer définitivement un lieu | Aucun (ID dans l'URL) *(En-tête Auth requis)* | **204 No Content** (Corps vide) | [x] Validé (204 No Content, 403 Forbidden si non-propriétaire) |

---

## 🗺️ 3. Gestion des Itinéraires (`/api/tours/*`)

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/tours` | Lister tous les itinéraires de l'utilisateur connecté | Aucun *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "tours": [...] } }` | [x] Validé (200 OK) |
| `GET` | `/api/tours/public` | Lister tous les itinéraires publics **(Sans Auth)** | Aucun | **200 OK** : `{ "status": "success", "data": { "tours": [...] } }` | [x] Validé (200 OK) |
| `POST` | `/api/tours` | Générer et enregistrer un circuit optimisé (TSP) | `{"name": "Mon Voyage", "place_ids": [1, 2], "visibility": "public"}` | **201 Created** : `{ "status": "success", "data": { "tour": { "id": 1, "name": "Mon Voyage", "places": [... ordonnés ...], "total_distance": 391.2, "visibility": "public", "share_token": "uuid-..." } } }` | [x] Validé (201 Created, 400 validation, 403 Forbidden si lieu privé possédé par autrui) |
| `GET` | `/api/tours/<id>` | Obtenir le détail d'un itinéraire privé | Aucun (ID dans l'URL) *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "tour": { ... } } }` | [x] Validé (200 OK, 403 Forbidden si non-propriétaire) |
| `DELETE` | `/api/tours/<id>` | Supprimer un itinéraire | Aucun (ID dans l'URL) *(En-tête Auth requis)* | **204 No Content** (Corps vide) | [x] Validé (204 No Content, 403 Forbidden si non-propriétaire) |
| `PATCH` | `/api/tours/<id>/share` | Activer/désactiver/basculer le partage public d'un circuit | `{"visibility": "public"}` (ou vide `{}` pour basculer/toggle) | **200 OK** : `{ "status": "success", "data": { "tour": { ..., "visibility": "public" } } }` | [x] Validé (200 OK, basculement/toggle automatique validé) |
| `GET` | `/api/tours/shared/<token>` | Accéder publiquement à un itinéraire **(Sans Auth)** | Aucun (Jeton UUID dans l'URL) | **200 OK** : `{ "status": "success", "data": { "tour": { ... } } }` | [x] Validé (200 OK, 404 si introuvable ou repassé en "private") |

---

## ⚡ 4. Nouvelles Routes Utiles

| Méthode | Route | Description | Corps de requête (JSON) | Réponse attendue | Statut du Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/auth/me` | Récupérer le profil courant | Aucun *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "user": { ... } } }` | [x] Validé (200 OK, 401 si jeton absent) |
| `PATCH` | `/api/places/<id>` | Mise à jour partielle d'un lieu | `{"visibility": "public"}` | **200 OK** : `{ "status": "success", "data": { "place": { ... } } }` | [x] Validé (200 OK, modification partielle validée) |
| `POST` | `/api/tours/<id>/recalculate` | Forcer le recalcul d'un parcours | Aucun *(En-tête Auth requis)* | **200 OK** : `{ "status": "success", "data": { "tour": { ... } } }` | [x] Validé (200 OK, 403 si non-propriétaire) |
| `POST` | `/api/tours/<id>/duplicate` | Dupliquer un parcours public/possédé | Aucun *(En-tête Auth requis)* | **201 Created** : `{ "status": "success", "data": { "tour": { ... } } }` | [x] Validé (201 Created, clonage auto des lieux privés validé) |
| `POST` | `/api/tours/optimize` | Optimiser une liste de lieux (sans sauvegarde) | `{"place_ids": [1, 2], "locked_positions": {"2": 1}}` | **200 OK** : `{ "status": "success", "data": { "places": [...], "total_distance": 12.3 } }` | [x] Validé (200 OK, contraintes globales OR-Tools validées) |
| `GET` | `/api/places` / `/api/tours/public` | Recherche, filtres et pagination | Aucun (Paramètres URL : `q`, `page`, `limit`) | **200 OK** : Liste paginée et filtrée | [x] Validé (200 OK) |
| `GET` | `/api/health/ready` | Healthcheck complet (API + DB) | Aucun | **200 OK** : `{ "status": "success", "data": { ... } }` | [x] Validé (200 OK, 500 si DB non joignable) |
