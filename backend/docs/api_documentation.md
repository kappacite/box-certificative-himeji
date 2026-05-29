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

### 👤 Obtenir l'utilisateur connecté **[Auth Requise]**
Renvoie les détails du profil de l'utilisateur actuellement authentifié par son JWT.

* **Méthode** : `GET`
* **URL** : `/api/auth/me`
* **Corps de la requête (JSON)** : Aucun (transmettre le header d'Auth)
* **Codes HTTP de réponse** :
  * **`200 OK`** : Profil récupéré avec succès.
    ```json
    {
      "status": "success",
      "data": {
        "user": {
          "id": 1,
          "username": "monpseudo",
          "email": "user@example.com"
        }
      }
    }
    ```
  * **`401 Unauthorized`** : Token manquant ou invalide.

---

## 📍 2. Gestion des Lieux (`/api/places/*`)

### 📋 Lister les lieux **[Auth Requise si privé / Facultatif si public]**
Renvoie la liste des lieux personnels ou publics avec filtres et pagination.

* **Méthode** : `GET`
* **URL** : `/api/places`
* **Paramètres de requête (Query Params)** :
  * `visibility` : Optionnel (`public` ou `private`, par défaut `private`). Si `public`, liste les lieux publics (aucune authentification requise).
  * `q` : Optionnel. Terme de recherche pour filtrer les lieux par nom (insensible à la casse).
  * `page` : Optionnel (défaut `1`). Numéro de page.
  * `limit` : Optionnel. Nombre de résultats par page.
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

### 🗺️ Rechercher les coordonnées d'un lieu (GET)
Récupère les coordonnées (latitude et longitude) et la ville d'une adresse ou d'un nom de lieu via le service Nominatim, sans enregistrer le lieu en base de données.

* **Méthode** : `GET`
* **URL** : `/api/places/search?q=<nom_du_lieu>`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Recherche réussie.
    ```json
    {
      "status": "success",
      "data": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "city": "Paris"
      }
    }
    ```
  * **`400 Bad Request`** : Paramètre `q` manquant ou vide, ou géolocalisation impossible.

---

### 🗺️ Prévisualiser les coordonnées d'un lieu (POST)
Identique à la route de recherche GET, mais via un corps de requête POST. Utile pour envoyer des noms complexes.

* **Méthode** : `POST`
* **URL** : `/api/places/geocode`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Paris"
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Géocodage réussi.
    ```json
    {
      "status": "success",
      "data": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "city": "Paris"
      }
    }
    ```
  * **`400 Bad Request`** : Champ `name` manquant, ou géolocalisation impossible.

---

### 🌍 Lister tous les lieux publics
Renvoie la liste globale de tous les lieux publics présents en base de données. Ne nécessite aucune authentification.

* **Méthode** : `GET`
* **URL** : `/api/places/public`
* **Paramètres de requête (Query Params)** :
  * `q` : Optionnel. Terme de recherche pour filtrer les lieux publics par nom.
  * `page` : Optionnel (défaut `1`). Numéro de page.
  * `limit` : Optionnel. Nombre de résultats par page.
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
Crée un nouveau lieu géographique. Si les coordonnées géographiques (`latitude`/`longitude`) ne sont pas fournies, l'API utilise automatiquement l'API OpenStreetMap Nominatim pour géocoder le nom et en résoudre la ville.

* **Méthode** : `POST`
* **URL** : `/api/places`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Lyon",
    "latitude": 45.7640,          // Optionnel
    "longitude": 4.8357,         // Optionnel
    "city": "Lyon",              // Optionnel (défaut: extrait via géocodage si coordonnées non fournies)
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
          "visibility": "public",
          "city": "Lyon",
          "is_hotel": false,
          "locked": false
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
  * **`400 Bad Request`** : Coordonnées partielles fournies. `latitude` et `longitude` doivent être envoyées ensemble si l'on ne veut pas utiliser le géocodage automatique.
    ```json
    {
      "status": "error",
      "message": "Latitude and longitude must be provided together.",
      "code": "VALIDATION_ERROR"
    }
    ```

---

### 🔍 Obtenir les détails d'un lieu **[Accès Public si public / Auth Requise si privé]**
Affiche les informations d'un lieu par son ID. Si le lieu est marqué public, n'importe qui (sans jeton) peut y accéder. S'il est privé, l'utilisateur doit être connecté et être le propriétaire du lieu.

* **Méthode** : `GET`
* **URL** : `/api/places/<int:place_id>`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Détails envoyés.
  * **`401 Unauthorized`** : Le lieu est privé et l'utilisateur n'est pas authentifié.
    ```json
    {
      "status": "error",
      "message": "Authentication required",
      "code": "UNAUTHORIZED"
    }
    ```
  * **`403 Forbidden`** : Le lieu est privé et n'appartient pas à l'utilisateur connecté.
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
  * **`400 Bad Request`** : Coordonnées partielles fournies. Si vous envoyez `latitude` ou `longitude`, il faut envoyer les deux.
    ```json
    {
      "status": "error",
      "message": "Latitude and longitude must be provided together.",
      "code": "VALIDATION_ERROR"
    }
    ```

---

### ✏️ Modifier partiellement un lieu **[Auth Requise / Propriétaire uniquement]**
Permet de modifier un ou plusieurs champs d'un lieu (nom, coordonnées ou visibilité) sans avoir à ré-envoyer l'ensemble des données. Si le nom est modifié et que les coordonnées ne sont pas fournies, une nouvelle géolocalisation automatique s'effectue.

* **Méthode** : `PATCH`
* **URL** : `/api/places/<int:place_id>`
* **Corps de la requête (JSON)** :
  ```json
  {
    "visibility": "public"
  }
  ```
  *(Vous pouvez spécifier "name", "latitude", "longitude" ou "visibility")*
* **Codes HTTP de réponse** :
  * **`200 OK`** : Modification partielle enregistrée avec succès.
  * **`401 Unauthorized`** : Token absent ou invalide.
  * **`403 Forbidden`** : L'utilisateur n'est pas le propriétaire du lieu.
  * **`404 Not Found`** : Le lieu n'existe pas.
  * **`400 Bad Request`** : Une seule coordonnée est fournie sans sa paire.

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
Renvoie tous les itinéraires appartenant à l'utilisateur connecté avec filtres et pagination.

* **Méthode** : `GET`
* **URL** : `/api/tours`
* **Paramètres de requête (Query Params)** :
  * `q` : Optionnel. Terme de recherche pour filtrer par nom d'itinéraire.
  * `page` : Optionnel (défaut `1`). Numéro de page.
  * `limit` : Optionnel. Nombre de résultats par page.
* **Codes HTTP de réponse** :
  * **`200 OK`** : Liste d'itinéraires retournée.

---

### 🌍 Lister tous les itinéraires publics
Affiche tous les itinéraires de la plateforme configurés avec une visibilité `"public"` avec recherche et pagination. Aucun jeton n'est requis.

* **Méthode** : `GET`
* **URL** : `/api/tours/public`
* **Paramètres de requête (Query Params)** :
  * `q` : Optionnel. Terme de recherche pour filtrer les itinéraires publics par nom.
  * `page` : Optionnel (défaut `1`). Numéro de page.
  * `limit` : Optionnel. Nombre de résultats par page.
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
Prend une liste d'IDs de lieux (qui doivent appartenir à l'utilisateur, ou être publics), calcule l'ordre optimal pour parcourir ces points (problème TSP avec regroupement par hôtels et allers-retours via OR-Tools) et enregistre l'itinéraire résultant en circuit fermé (retour au point de départ).

L'API supporte le **verrouillage de certaines étapes** (lieux) à des positions fixes de l'itinéraire et le **regroupement par hôtels** basé sur la distance maximale fournie.

* **Méthode** : `POST`
* **URL** : `/api/tours`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Mon Circuit Opti",
    "place_ids": [
      1,
      {"id": 201, "locked": true}, // Reste à sa position d'entrée (index 1)
      {"id": 202, "position": 0}   // Reste à l'index 0 (départ de la boucle)
    ],
    // Optionnel : dictionnaire de verrous (ID lieu -> Position cible)
    "locked_positions": {
      "202": 0
    },
    // Optionnel : liste des IDs des lieux à figer à leur index d'entrée
    "locked_places": [201],
    // Optionnel : distance maximale en km pour allers-retours depuis l'hôtel (défaut: 100.0)
    "max_distance": 100.0,
    "visibility": "public" // Optionnel ("private" ou "public", défaut: "private")
  }
  ```
* **Codes HTTP de réponse** :
  * **`201 Created`** : Itinéraire généré et persisté avec succès.
    * *Note sur la boucle fermée* : Le tableau `places` renvoyé comporte $N + 1$ éléments. Le premier et le dernier élément sont identiques (par exemple `[A, B, C, A]`) afin de matérialiser le retour au point de départ.
    ```json
    {
      "status": "success",
      "data": {
        "tour": {
          "id": 15,
          "name": "Mon Circuit Opti",
          "owner_id": 2,
          "places": [
            { "id": 202, "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "owner_id": 2, "visibility": "public", "locked": true, "is_hotel": true },
            { "id": 201, "name": "Mon Lieu Privé", "latitude": 48.8566, "longitude": 2.3522, "owner_id": 2, "visibility": "private", "locked": true, "is_hotel": false },
            { "id": 1, "name": "Tour Eiffel, Paris", "latitude": 48.8584, "longitude": 2.2945, "owner_id": 1, "visibility": "public", "locked": false, "is_hotel": false },
            { "id": 202, "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "owner_id": 2, "visibility": "public", "locked": true, "is_hotel": true }
          ],
          "total_distance": 783.52,
          "visibility": "public",
          "share_token": "59b8d2d1-9f93-4a11-a83d-9de1e9a2bcae",
          "max_distance": 100.0
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

### 🧩 Prévisualiser un itinéraire optimisé (sans sauvegarde) **[Auth Requise]**
Identique à la création d'itinéraire (`POST /api/tours`), mais **ne persiste pas** l'itinéraire en base de données. Renvoie la liste ordonnée optimisée des lieux et la distance totale calculée.

* **Méthode** : `POST`
* **URL** : `/api/tours/preview`
* **Corps de la requête (JSON)** :
  ```json
  {
    "place_ids": [
      1,
      {"id": 201, "locked": true},
      {"id": 202, "position": 0}
    ],
    "locked_positions": {
      "202": 0
    },
    "locked_places": [201],
    "max_distance": 100.0
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Aperçu calculé avec succès. (Le champ `id` retourné est à `null`).
    ```json
    {
      "status": "success",
      "data": {
        "tour": {
          "id": null,
          "name": "Preview",
          "owner_id": 2,
          "places": [
            { "id": 202, "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "owner_id": 2, "visibility": "public", "locked": true, "is_hotel": true },
            { "id": 201, "name": "Mon Lieu Privé", "latitude": 48.8566, "longitude": 2.3522, "owner_id": 2, "visibility": "private", "locked": true, "is_hotel": false },
            { "id": 1, "name": "Tour Eiffel, Paris", "latitude": 48.8584, "longitude": 2.2945, "owner_id": 1, "visibility": "public", "locked": false, "is_hotel": false },
            { "id": 202, "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "owner_id": 2, "visibility": "public", "locked": true, "is_hotel": true }
          ],
          "total_distance": 783.52,
          "visibility": "private",
          "share_token": "",
          "max_distance": 100.0
        }
      }
    }
    ```
  * **`400 Bad Request`** : Moins de 2 points fournis, ou ID de lieu inexistant.
  * **`403 Forbidden`** : Contient un lieu appartenant à autrui qui n'est **pas** configuré en visibilité `"public"`.

---

### ✏️ Modifier un itinéraire **[Auth Requise / Propriétaire uniquement]**
Permet de modifier les informations d'un itinéraire (nom, visibilité, liste de lieux, contraintes de verrous et distance maximale de regroupement). Si la liste des lieux, les verrous ou `max_distance` sont modifiés, l'itinéraire est ré-optimisé. Si aucun verrou n'est spécifié, les verrous existants encore présents dans la liste de lieux sont conservés par défaut.

* **Méthode** : `PATCH`
* **URL** : `/api/tours/<int:tour_id>`
* **Corps de la requête (JSON)** :
  ```json
  {
    "name": "Mon Nouveau Nom",                   // Optionnel
    "visibility": "private",                      // Optionnel ("private" ou "public")
    "place_ids": [1, 201, 202, 203],              // Optionnel (nouvelle liste de lieux)
    "locked_positions": {                         // Optionnel (nouveau dictionnaire de verrous)
      "203": 0
    },
    "locked_places": [201],                       // Optionnel (nouvelle liste de verrous d'origine)
    "max_distance": 120.0                         // Optionnel (nouvelle distance max en km pour regroupement)
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Modification appliquée et tournée recalculée si nécessaire.
  * **`400 Bad Request`** : Données invalides.
  * **`403 Forbidden`** : L'utilisateur n'est pas le propriétaire de cet itinéraire.
  * **`404 Not Found`** : L'itinéraire n'existe pas.

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
          "max_distance": 100.0
          // ...
        }
      }
    }
    ```
  * **`400 Bad Request`** : Valeur de visibilité non valide.
  * **`403 Forbidden`** : Utilisateur non propriétaire.

---

### 🔄 Recalculer un itinéraire **[Auth Requise / Propriétaire uniquement]**
Recalcule l'ordre optimal et la distance totale d'un itinéraire existant. Utile si les coordonnées de l'un des lieux de l'itinéraire ont été modifiées entre-temps.

* **Méthode** : `POST`
* **URL** : `/api/tours/<int:tour_id>/recalculate`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Recalcul réussi.
  * **`403 Forbidden`** : Utilisateur non propriétaire.
  * **`404 Not Found`** : L'itinéraire n'existe pas.

---
### ⚡ Optimiser un itinéraire (sans sauvegarde) **[Auth Requise]**
Calcule l'ordre optimal et la distance totale pour une liste de lieux donnée sans créer ni enregistrer de tournée en base de données. Il permet également de tester l'impact de verrous de position, de lieux spécifiques, ou de la distance de clustering `max_distance`.

* **Méthode** : `POST`
* **URL** : `/api/tours/optimize`
* **Corps de la requête (JSON)** :
  ```json
  {
    "place_ids": [1, 2, 3], // Liste d'identifiants de lieux à inclure (ou objets {"id": 1, "locked": true, "position": 0})
    "locked_positions": {   // Optionnel (dictionnaire identifiant_lieu_str -> position_int)
      "3": 1
    },
    "locked_places": [1],   // Optionnel (liste d'identifiants à verrouiller à leur index d'entrée dans place_ids)
    "max_distance": 100.0   // Optionnel (défaut: 100.0) — distance max en km pour les allers-retours depuis l'hôtel
  }
  ```
* **Codes HTTP de réponse** :
  * **`200 OK`** : Calcul d'optimisation réussi.
    ```json
    {
      "status": "success",
      "data": {
        "places": [
          {
            "id": 1,
            "name": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "owner_id": 1,
            "visibility": "private",
            "locked": true,
            "is_hotel": true
          },
          {
            "id": 3,
            "name": "Marseille",
            "latitude": 43.2964,
            "longitude": 5.3697,
            "owner_id": 1,
            "visibility": "private",
            "locked": true,
            "is_hotel": true
          },
          {
            "id": 2,
            "name": "Lyon",
            "latitude": 45.7640,
            "longitude": 4.8357,
            "owner_id": 1,
            "visibility": "private",
            "locked": false,
            "is_hotel": false
          }
        ],
        "total_distance": 783.52
      }
    }
    ```
  * **`400 Bad Request`** : Moins de 2 lieux fournis ou ID non valides.
  * **`403 Forbidden`** : L'un des lieux spécifiés est privé et appartient à un tiers.

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
          "places": [
            { "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "visibility": "public", "locked": true, "is_hotel": true },
            { "name": "Tour Eiffel, Paris", "latitude": 48.8584, "longitude": 2.2945, "visibility": "public", "locked": false, "is_hotel": false },
            { "name": "Lyon", "latitude": 45.7640, "longitude": 4.8357, "visibility": "public", "locked": true, "is_hotel": true }
          ],
          "total_distance": 783.52,
          "visibility": "public",
          "share_token": "59b8d2d1-9f93-4a11-a83d-9de1e9a2bcae",
          "max_distance": 100.0
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

---

### 🔍 Vérification de l'état de préparation (Ready Healthcheck)
Vérifie que le backend et la base de données SQLite/PostgreSQL sont connectés et prêts à répondre.

* **Méthode** : `GET`
* **URL** : `/api/health/ready`
* **Codes HTTP de réponse** :
  * **`200 OK`** : Le service et la base de données sont prêts.
    ```json
    {
      "status": "success",
      "data": {
        "message": "Database and service are ready"
      }
    }
    ```
  * **`500 Internal Server Error`** : La base de données n'est pas joignable.
    ```json
    {
      "status": "error",
      "message": "Database is not ready: <détails_erreur>",
      "code": "DATABASE_ERROR"
    }
    ```
