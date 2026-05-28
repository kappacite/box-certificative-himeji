# Documentation de l'API REST — Travel Planner Backend

Cette documentation présente l'intégralité des endpoints du backend Travel Planner, y compris les paramètres requis, les formats de requêtes et de réponses (succès et erreurs) et les codes d'état HTTP associés.

---

## 📌 Spécifications Générales

### Enveloppe de Réponse Standard

Toutes les réponses de l'API respectent une structure JSON constante.

#### Succès (HTTP 200, 201, 204)
```json
{
  "status": "success",
  "data": {
    // Les données de l'entité retournée
  }
}
```
*Note : Pour les codes HTTP 204 (No Content), le corps de la réponse est vide.*

#### Erreur (HTTP 400, 401, 403, 404, 409, 500)
```json
{
  "status": "error",
  "message": "Description humaine de l'erreur survenue",
  "code": "SNAKE_CASE_ERROR_CODE"
}
```

### Authentification

La plupart des routes nécessitent d'être authentifié via un jeton **JWT**.
- Ce jeton doit être passé dans les en-têtes HTTP sous la forme suivante :
  ```http
  Authorization: Bearer <VOTRE_JWT_TOKEN>
  ```
- Les routes nécessitant cette authentification sont marquées par la mention **[Auth Requise]** ci-dessous.

---

## 🔐 1. Authentification (`/api/auth/*`)

### 📝 Inscription d'un utilisateur
Permet de créer un nouveau compte utilisateur.

* **Méthode** : `POST`
* **URL** : `/api/auth/register`
* **Corps de la requête (JSON)** :
  ```json
  {
    "username": "monpseudo",
    "email": "user@example.com",
    "password": "password123"
  }
  ```
* **Codes HTTP de réponse** :
  * **`201 Created`** : Inscription réussie.
    ```json
    {
      "status": "success",
      "data": {
        "user": {
          "id": 2,
          "username": "monpseudo",
          "email": "user@example.com"
        }
      }
    }
    ```
  * **`400 Bad Request`** : Champs manquants ou mot de passe trop court (min. 6 caractères).
    ```json
    {
      "status": "error",
      "message": "Password must be at least 6 characters long",
      "code": "VALIDATION_ERROR"
    }
    ```
  * **`409 Conflict`** : Pseudo ou adresse e-mail déjà utilisé.
    ```json
    {
      "status": "error",
      "message": "Email is already registered",
      "code": "CONFLICT_ERROR"
    }
    ```

---

### 🔑 Connexion d'un utilisateur
Vérifie les identifiants et génère un jeton JWT de session.

* **Méthode** : `POST`
* **URL** : `/api/auth/login`
* **Corps de la requête (JSON)** :
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Authentification réussie. Renvoie le token de session JWT.
    ```json
    {
      "status": "success",
      "data": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user": {
          "id": 2,
          "username": "monpseudo",
          "email": "user@example.com"
        }
      }
    }
    ```
  * **`401 Unauthorized`** : Email ou mot de passe incorrect, ou hash invalide.
    ```json
    {
      "status": "error",
      "message": "Invalid email or password",
      "code": "UNAUTHORIZED"
    }
    ```

---

### 🚪 Déconnexion d'un utilisateur **[Auth Requise]**
Invalide (côté client) la session en cours.

* **Méthode** : `POST`
* **URL** : `/api/auth/logout`
* **Corps de la requête (JSON)** : Aucun (transmettre le header d'Auth)
* **Codes HTTP de réponse** :
  * **`200 OK`** : Déconnexion confirmée.
    ```json
    {
      "status": "success",
      "data": {
        "message": "Logged out successfully"
      }
    }
    ```
  * **`401 Unauthorized`** : Token manquant ou invalide.
    ```json
    {
      "status": "error",
      "message": "Missing or invalid token",
      "code": "UNAUTHORIZED"
    }
    ```

---

## 📍 2. Gestion des Lieux (`/api/places/*`)

### 📋 Lister mes lieux **[Auth Requise]**
Renvoie tous les lieux personnels créés par l'utilisateur connecté.

* **Méthode** : `GET`
* **URL** : `/api/places`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Liste récupérée.
    ```json
    {
      "status": "success",
      "data": {
        "places": [
          {
            "id": 201,
            "name": "Mon Lieu Privé",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": 2,
            "visibility": "private"
          }
        ]
      }
    }
    ```

---

### 🌍 Lister tous les lieux publics
Renvoie la liste globale de tous les lieux publics présents en base de données. Ne nécessite aucune authentification.

* **Méthode** : `GET`
* **URL** : `/api/places/public`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Liste récupérée (ex: les 200 lieux notables français).
    ```json
    {
      "status": "success",
      "data": {
        "places": [
          {
            "id": 1,
            "name": "Tour Eiffel, Paris",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "owner_id": 1,
            "visibility": "public"
          }
          // ...
        ]
      }
    }
    ```

---

### ➕ Créer un lieu **[Auth Requise]**
Crée un nouveau lieu géographique. Si les coordonnées géographiques (`latitude`/`longitude`) ne sont pas fournies, l'API utilise automatiquement l'API OpenStreetMap Nominatim pour géocoder le nom.

* **Méthode** : `POST`
* **URL** : `/api/places`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Lyon",
    "latitude": 45.7640,          // Optionnel
    "longitude": 4.8357,         // Optionnel
    "visibility": "public"       // Optionnel ("private" ou "public", défaut: "private")
  }
  ```
* **Codes HTTP de réponse** :
  * **`201 Created`** : Lieu enregistré avec succès.
    ```json
    {
      "status": "success",
      "data": {
        "place": {
          "id": 202,
          "name": "Lyon",
          "latitude": 45.764,
          "longitude": 4.8357,
          "owner_id": 2,
          "visibility": "public"
        }
      }
    }
    ```
  * **`400 Bad Request`** : Nom manquant ou coordonnées géographiques non résolues.
    ```json
    {
      "status": "error",
      "message": "Could not resolve coordinates for place name: UnknownCity",
      "code": "VALIDATION_ERROR"
    }
    ```

---

### 🔍 Obtenir les détails d'un lieu **[Auth Requise]**
Affiche les informations d'un lieu par son ID.

* **Méthode** : `GET`
* **URL** : `/api/places/<int:place_id>`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Détails envoyés.
  * **`403 Forbidden`** : Le lieu est marqué privé et n'appartient pas à l'utilisateur connecté.
    ```json
    {
      "status": "error",
      "message": "You do not have access to this place",
      "code": "FORBIDDEN"
    }
    ```
  * **`404 Not Found`** : Le lieu n'existe pas en base de données.
    ```json
    {
      "status": "error",
      "message": "Place not found",
      "code": "NOT_FOUND"
    }
    ```

---

### ✏️ Modifier un lieu **[Auth Requise / Propriétaire uniquement]**
Met à jour les informations d'un lieu. Si le nom est modifié et que les coordonnées sont omises, le lieu est à nouveau géocodé.

* **Méthode** : `PUT`
* **URL** : `/api/places/<int:place_id>`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Lyon Modifié",
    "latitude": 45.7,            // Optionnel
    "longitude": 4.8,            // Optionnel
    "visibility": "private"      // Optionnel ("private" ou "public")
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Modification validée et persistée.
  * **`403 Forbidden`** : L'utilisateur n'est pas le créateur de ce lieu.
  * **`404 Not Found`** : Le lieu n'existe pas.

---

### 🗑️ Supprimer un lieu **[Auth Requise / Propriétaire uniquement]**
Supprime définitivement un lieu.

* **Méthode** : `DELETE`
* **URL** : `/api/places/<int:place_id>`
* **Codes HTTP de réponse** :
  * **`204 No Content`** : Suppression réussie (corps vide).
  * **`403 Forbidden`** : L'utilisateur n'est pas le propriétaire du lieu.
  * **`404 Not Found`** : Le lieu n'existe pas.

---

## 🗺️ 3. Gestion des Itinéraires (`/api/tours/*`)

### 📋 Lister mes itinéraires **[Auth Requise]**
Renvoie tous les itinéraires appartenant à l'utilisateur connecté.

* **Méthode** : `GET`
* **URL** : `/api/tours`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Liste d'itinéraires retournée.

---

### 🌍 Lister tous les itinéraires publics
Affiche tous les itinéraires de la plateforme configurés avec une visibilité `"public"`. Aucun jeton n'est requis.

* **Méthode** : `GET`
* **URL** : `/api/tours/public`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Liste récupérée.
    ```json
    {
      "status": "success",
      "data": {
        "tours": [
          {
            "id": 12,
            "name": "Grand Tour de France (200 Lieux)",
            "owner_id": 1,
            "places": [ ... ],
            "total_distance": 3209.43,
            "visibility": "public",
            "share_token": "a1b2c3d4-..."
          }
        ]
      }
    }
    ```

---

### 🧩 Générer et créer un itinéraire optimisé **[Auth Requise]**
Prend une liste d'IDs de lieux (qui doivent appartenir à l'utilisateur, ou être publics), calcule l'ordre optimal pour parcourir ces points (problème TSP résolu par Google OR-Tools) et enregistre l'itinéraire résultant en circuit fermé (retour au point de départ).

* **Méthode** : `POST`
* **URL** : `/api/tours`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Mon Circuit Opti",
    "place_ids": [1, 201, 202],
    "visibility": "public"       // Optionnel ("private" ou "public", défaut: "private")
  }
  ```
* **Codes HTTP de réponse** :
  * **`201 Created`** : Itinéraire généré et persisté avec succès.
    ```json
    {
      "status": "success",
      "data": {
        "tour": {
          "id": 15,
          "name": "Mon Circuit Opti",
          "owner_id": 2,
          "places": [
            { "id": 1, "name": "Tour Eiffel, Paris", ... },
            { "id": 202, "name": "Lyon", ... },
            { "id": 201, "name": "Mon Lieu Privé", ... }
          ],
          "total_distance": 783.52,
          "visibility": "public",
          "share_token": "59b8d2d1-9f93-4a11-a83d-9de1e9a2bcae"
        }
      }
    }
    ```
  * **`400 Bad Request`** : Moins de 2 points fournis, ou ID de lieu inexistant.
    ```json
    {
      "status": "error",
      "message": "At least 2 places are required to generate a tour",
      "code": "VALIDATION_ERROR"
    }
    ```
  * **`403 Forbidden`** : Contient un lieu appartenant à autrui qui n'est **pas** configuré en visibilité `"public"`.
    ```json
    {
      "status": "error",
      "message": "You do not own the place with ID 3 and it is not public",
      "code": "FORBIDDEN"
    }
    ```

---

### 🔍 Obtenir un itinéraire spécifique **[Auth Requise]**
Renvoie les détails d'un itinéraire par son ID (seulement s'il appartient à l'utilisateur).

* **Méthode** : `GET`
* **URL** : `/api/tours/<int:tour_id>`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Détails du circuit.
  * **`403 Forbidden`** : L'itinéraire appartient à un autre utilisateur.
  * **`404 Not Found`** : L'itinéraire n'existe pas.

---

### 🗑️ Supprimer un itinéraire **[Auth Requise / Propriétaire uniquement]**
Supprime définitivement un circuit.

* **Méthode** : `DELETE`
* **URL** : `/api/tours/<int:tour_id>`
* **Codes HTTP de réponse** :
  * **`204 No Content`** : Suppression réussie (corps vide).
  * **`403 Forbidden`** : Vous n'êtes pas le propriétaire de cet itinéraire.

---

### 🔄 Basculer ou modifier la visibilité d'un itinéraire **[Auth Requise / Propriétaire uniquement]**
Modifie la visibilité d'un itinéraire. Si aucun corps n'est passé, la route agit comme un commutateur de visibilité (public ↔ privé).

* **Méthode** : `PATCH`
* **URL** : `/api/tours/<int:tour_id>/share`
* **Corps de la requête (JSON)** :
  * `{"visibility": "public"}` (pour forcer le partage)
  * `{"visibility": "private"}` (pour révoquer le partage)
  * `{}` ou aucun corps (pour commuter / toggle la visibilité)
* **Codes HTTP de réponse** :
  * **`200 OK`** : Changement appliqué.
    ```json
    {
      "status": "success",
      "data": {
        "tour": {
          "id": 15,
          "visibility": "private", // ou "public"
          "share_token": "59b8d2d1-9f93-4a11-a83d-9de1e9a2bcae",
          // ...
        }
      }
    }
    ```
  * **`400 Bad Request`** : Valeur de visibilité non valide.
  * **`403 Forbidden`** : Utilisateur non propriétaire.

---

### 🔗 Accéder à un itinéraire partagé
Permet à n'importe quel internaute d'accéder aux détails d'un itinéraire via son UUID de partage (`share_token`). Aucune authentification n'est requise.

* **Méthode** : `GET`
* **URL** : `/api/tours/shared/<string:share_token>`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Détails du circuit public.
    ```json
    {
      "status": "success",
      "data": {
        "tour": {
          "name": "Mon Circuit Opti",
          "places": [ ... ],
          "total_distance": 783.52,
          "visibility": "public",
          "share_token": "59b8d2d1-9f93-4a11-a83d-9de1e9a2bcae"
        }
      }
    }
    ```
  * **`404 Not Found`** : Le jeton de partage est inexistant, ou l'itinéraire a été repassé en visibilité `"private"`.
    ```json
    {
      "status": "error",
      "message": "Shared tour not found or is private",
      "code": "NOT_FOUND"
    }
    ```

---

## 📈 4. Santé de l'API (`/api/health`)

### 🔍 Vérification de la disponibilité (Healthcheck)
Permet à Docker, Kubernetes ou aux outils de monitoring de tester l'état du backend.

* **Méthode** : `GET`
* **URL** : `/api/health`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Le service est en bonne santé.
    ```json
    {
      "status": "success",
      "data": {
        "message": "Service is healthy"
      }
    }
    ```
