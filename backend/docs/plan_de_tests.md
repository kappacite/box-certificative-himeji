# Plan de Test API — Travel Planner Backend

Ce document définit le plan de test exhaustif, route par route, de l'API Flask. Il décrit pour chaque point d'accès (endpoint) les préconditions, les scénarios de réussite (happy paths), les cas d'erreur (edge cases) et les commandes `curl` associées pour valider le comportement du serveur.

---

## 📋 Structure Générale des Réponses

Toutes les réponses de l'API doivent correspondre au format enveloppe JSON standard :

### Cas de succès :
* **Code HTTP** : `200 OK` ou `201 Created`
* **Format** :
  ```json
  {
    "status": "success",
    "data": { ... }
  }
  ```
* **Exception (204 No Content)** : Les requêtes de suppression réussies renvoient un code HTTP `204` sans corps de réponse.

### Cas d'erreur :
* **Code HTTP** : `400`, `401`, `403`, `404` ou `500`
* **Format** :
  ```json
  {
    "status": "error",
    "message": "Description humaine du problème",
    "code": "SNAKE_CASE_ERROR_CODE"
  }
  ```

---

## 🔐 1. Module Authentification (`/api/auth/*`)

### 1.1 Inscription (`POST /api/auth/register`)
* **Description** : Permet de créer un nouveau compte utilisateur.
* **Champs requis** : `username` (string), `email` (string), `password` (string).
* **Cas à tester** :
  1. **Succès (201 Created)** : Inscription avec des identifiants valides.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/register \
            -H "Content-Type: application/json" \
            -d '{"username": "testuser", "email": "testuser@example.com", "password": "password123"}'
       ```
     - *Résultat attendu* : Code 211, utilisateur enregistré retourné sans son hash de mot de passe.
  2. **Erreur - Champs manquants (400 Bad Request)** : Omettre un champ obligatoire.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/register \
            -H "Content-Type: application/json" \
            -d '{"username": "testuser"}'
       ```
     - *Résultat attendu* : Code 400, `"code": "BAD_REQUEST"`.
  3. **Erreur - Mot de passe trop court (400 Bad Request)** : Mot de passe inférieur à 6 caractères.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/register \
            -H "Content-Type: application/json" \
            -d '{"username": "testuser", "email": "testuser@example.com", "password": "123"}'
       ```
     - *Résultat attendu* : Code 400, `"code": "BAD_REQUEST"`.
  4. **Erreur - Doublon d'e-mail/pseudo (409 Conflict)** : Tenter d'utiliser un e-mail ou un pseudo existant.
     - *Commande* : Exécuter la commande de succès (1) une deuxième fois.
     - *Résultat attendu* : Code 409, `"code": "CONFLICT"`.

---

### 1.2 Connexion (`POST /api/auth/login`)
* **Description** : Permet à l'utilisateur de se connecter pour récupérer un jeton Bearer JWT.
* **Champs requis** : `email` (string), `password` (string).
* **Cas à tester** :
  1. **Succès (200 OK)** : Authentification valide.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/login \
            -H "Content-Type: application/json" \
            -d '{"email": "testuser@example.com", "password": "password123"}'
       ```
     - *Résultat attendu* : Code 200, retour d'un jeton `token` exploitable et des infos de l'utilisateur.
  2. **Erreur - Identifiants incorrects (401 Unauthorized)** : Mauvais e-mail ou mot de passe incorrect.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/login \
            -H "Content-Type: application/json" \
            -d '{"email": "testuser@example.com", "password": "wrongpassword"}'
       ```
     - *Résultat attendu* : Code 401, `"code": "UNAUTHORIZED"`.

---

### 1.3 Déconnexion (`POST /api/auth/logout`)
* **Description** : Informe le serveur de la déconnexion de l'utilisateur (le client doit supprimer le jeton stocké).
* **Préconditions** : Nécessite l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (200 OK)** : Envoi d'un jeton valide.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/logout \
            -H "Authorization: Bearer <TOKEN_OBTENU_CI_DESSUS>"
       ```
     - *Résultat attendu* : Code 200, message de confirmation de déconnexion.
  2. **Erreur - Non authentifié (401 Unauthorized)** : Jeton manquant ou mal formé.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/auth/logout
       ```
     - *Résultat attendu* : Code 401, `"code": "UNAUTHORIZED"`.

---

## 📍 2. Module Lieux (`/api/places/*`)

> **Préconditions** : Toutes ces requêtes nécessitent l'en-tête `Authorization: Bearer <token>`.

### 2.1 Lister les Lieux (`GET /api/places`)
* **Cas à tester** :
  1. **Succès (200 OK)** : Récupération de la liste.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/places \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 200, liste (tableau JSON) des lieux créés par cet utilisateur.

---

### 2.2 Créer un Lieu (`POST /api/places`)
* **Champs requis** : `name` (string)
* **Champs optionnels** : `latitude` (float), `longitude` (float)
* **Cas à tester** :
  1. **Succès - Résolution Nominatim (201 Created)** : Envoi d'un nom valide sans coordonnées (géocodage auto).
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/places \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Paris"}'
       ```
     - *Résultat attendu* : Code 201, lieu créé avec latitude (`48.8566`) et longitude (`2.3522`) résolues.
  2. **Succès - Coordonnées manuelles (201 Created)** : Envoi d'un nom avec des coordonnées précises.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/places \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Custom Spot", "latitude": 10.0, "longitude": 20.0}'
       ```
     - *Résultat attendu* : Code 201, lieu enregistré avec les coordonnées passées en paramètre.
  3. **Erreur - Lieu inconnu (400 Bad Request)** : Nom impossible à résoudre géographiquement par le service externe.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/places \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "InconnulandiaXYZ"}'
       ```
     - *Résultat attendu* : Code 400, `"code": "BAD_REQUEST"`, message d'erreur indiquant l'échec de résolution des coordonnées.

---

### 2.3 Détail d'un Lieu (`GET /api/places/<id>`)
* **Cas à tester** :
  1. **Succès (200 OK)** : Récupération par son propriétaire.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN_PROPRIETAIRE>"
       ```
     - *Résultat attendu* : Code 200, données du lieu retournées.
  2. **Erreur - Lieu inexistant (404 Not Found)** : Demander un ID qui n'existe pas en base.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/places/9999 \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 404, `"code": "NOT_FOUND"`.
  3. **Erreur - Non propriétaire (403 Forbidden)** : Tenter d'accéder au lieu d'un autre utilisateur.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN_AUTRE_USER>"
       ```
     - *Résultat attendu* : Code 403, `"code": "FORBIDDEN"`.

---

### 2.4 Modifier un Lieu (`PUT /api/places/<id>`)
* **Cas à tester** :
  1. **Succès (200 OK)** : Modification du nom et coordonnées par le propriétaire.
     - *Commande* :
       ```bash
       curl -X PUT http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN_PROPRIETAIRE>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Paris Modifie", "latitude": 48.0, "longitude": 2.0}'
       ```
     - *Résultat attendu* : Code 200, données mises à jour retournées.
  2. **Erreur - Droits insuffisants (403 Forbidden)** : Tentative de modification par un autre utilisateur.
     - *Commande* :
       ```bash
       curl -X PUT http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN_AUTRE_USER>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Piratage"}'
       ```
     - *Résultat attendu* : Code 403, `"code": "FORBIDDEN"`.

---

### 2.5 Supprimer un Lieu (`DELETE /api/places/<id>`)
* **Cas à tester** :
  1. **Succès (204 No Content)** : Suppression par le propriétaire.
     - *Commande* :
       ```bash
       curl -X DELETE http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN_PROPRIETAIRE>"
       ```
     - *Résultat attendu* : Code 204, aucun corps de message retourné.
  2. **Erreur - Droits insuffisants (403 Forbidden)** : Tentative de suppression par un autre utilisateur.
     - *Commande* :
       ```bash
       curl -X DELETE http://localhost:5000/api/places/2 \
            -H "Authorization: Bearer <TOKEN_AUTRE_USER>"
       ```
     - *Résultat attendu* : Code 403, `"code": "FORBIDDEN"`.

---

## 🗺️ 3. Module Itinéraires (`/api/tours/*`)

### 3.1 Lister les Itinéraires (`GET /api/tours`)
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (200 OK)** : Récupération.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/tours \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 200, liste des itinéraires de l'utilisateur.

---

### 3.2 Générer un Itinéraire (`POST /api/tours`)
* **Préconditions** : L'utilisateur doit avoir préalablement créé au moins 2 lieux en base de données et posséder l'en-tête `Authorization: Bearer <token>`.
* **Champs requis** : `name` (string), `place_ids` (tableau d'entiers).
* **Cas à tester** :
  1. **Succès (201 Created)** : Génération avec $\ge 2$ lieux valides appartenant à l'utilisateur.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Mon Itinéraire", "place_ids": [3, 4]}'
       ```
     - *Résultat attendu* : Code 201, circuit créé avec visibilité `"private"`, jeton `share_token` (UUID) généré, liste des lieux réordonnée par Nearest Neighbor + 2-opt, et distance totale en kilomètres calculée.
  2. **Erreur - Moins de 2 lieux (400 Bad Request)** : Passer un seul ou aucun ID de lieu.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Mon Itinéraire", "place_ids": [3]}'
       ```
     - *Résultat attendu* : Code 400, `"code": "BAD_REQUEST"`.
  3. **Erreur - Lieu non possédé (403 Forbidden)** : Passer un ID de lieu appartenant à un autre utilisateur.
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"name": "Mon Itinéraire", "place_ids": [3, 99]}'  # 99 appartient à un autre user
       ```
     - *Résultat attendu* : Code 403, `"code": "FORBIDDEN"`.

---

### 3.3 Partager un Itinéraire (`PATCH /api/tours/<id>/share`)
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Champs requis** : `visibility` (string : `"public"` ou `"private"`).
* **Cas à tester** :
  1. **Succès (200 OK)** : Passage en public ou privé par le propriétaire.
     - *Commande* :
       ```bash
       curl -X PATCH http://localhost:5000/api/tours/1/share \
            -H "Authorization: Bearer <TOKEN_PROPRIETAIRE>" \
            -H "Content-Type: application/json" \
            -d '{"visibility": "public"}'
       ```
     - *Résultat attendu* : Code 200, données du parcours modifiées avec `"visibility": "public"`.
  2. **Erreur - Valeur incorrecte (400 Bad Request)** : Passer une chaîne invalide (ex: `"visible"` au lieu de `"public"`).
     - *Commande* :
       ```bash
       curl -X PATCH http://localhost:5000/api/tours/1/share \
            -H "Authorization: Bearer <TOKEN_PROPRIETAIRE>" \
            -H "Content-Type: application/json" \
            -d '{"visibility": "visible"}'
       ```
     - *Résultat attendu* : Code 400, `"code": "BAD_REQUEST"`.

---

### 3.4 Accéder à un Itinéraire Public (`GET /api/tours/shared/<token>`)
* **Préconditions** : **Aucune authentification requise**. Le parcours ciblé doit avoir sa visibilité définie sur `"public"`.
* **Cas à tester** :
  1. **Succès (200 OK)** : Requête avec un token valide d'un parcours public.
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/tours/shared/<SHARE_TOKEN_UUID>
       ```
     - *Résultat attendu* : Code 200, données complètes du circuit retournées. L'accès est libre et anonyme.
  2. **Erreur - Parcours privé (404 Not Found)** : Requête avec le token d'un parcours configuré en `"private"`.
     - *Commande* :
       ```bash
       # Mettre d'abord le parcours en privé, puis tenter d'y accéder :
       curl -X GET http://localhost:5000/api/tours/shared/<SHARE_TOKEN_UUID>
       ```
     - *Résultat attendu* : Code 404, `"code": "NOT_FOUND"`. Le serveur masque l'existence du jeton pour des raisons de confidentialité.

---

## ⚡ 4. Nouvelles Routes Utiles (Utilitaires & Optimisations)

### 4.1 Profil Courant (`GET /api/auth/me`)
* **Description** : Renvoie le profil de l'utilisateur connecté à partir de son JWT.
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (200 OK)** :
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/auth/me \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 200, profil de l'utilisateur retourné (id, username, email).

---

### 4.2 Modification Partielle de Lieu (`PATCH /api/places/<id>`)
* **Description** : Permet de modifier uniquement certains champs d'un lieu (ex. la visibilité ou les coordonnées).
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (200 OK)** : Modification de la visibilité uniquement.
     - *Commande* :
       ```bash
       curl -X PATCH http://localhost:5000/api/places/1 \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"visibility": "public"}'
       ```
     - *Résultat attendu* : Code 200, le lieu est mis à jour en public sans exiger de fournir à nouveau le nom ou les coordonnées.

---

### 4.3 Recalculer un Itinéraire (`POST /api/tours/<id>/recalculate`)
* **Description** : Force le recalcul de l'itinéraire (ordre optimal et distance totale) suite à un changement de coordonnées des lieux.
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>` et la propriété du parcours.
* **Cas à tester** :
  1. **Succès (200 OK)** :
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours/1/recalculate \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 200, l'itinéraire recalculé avec ses nouvelles coordonnées et la nouvelle distance totale.

---

### 4.4 Dupliquer un Itinéraire (`POST /api/tours/<id>/duplicate`)
* **Description** : Permet de copier un itinéraire public ou possédé dans son espace personnel en clonant les lieux privés d'autrui.
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (201 Created)** :
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours/2/duplicate \
            -H "Authorization: Bearer <TOKEN>"
       ```
     - *Résultat attendu* : Code 201, un nouveau parcours cloné privé est créé pour l'utilisateur.

---

### 4.5 Optimisation Standalone de Lieux (`POST /api/tours/optimize`)
* **Description** : Calcule l'ordre optimal et la distance d'un parcours pour une liste de lieux et de verrous, sans sauvegarde.
* **Préconditions** : Requiert l'en-tête `Authorization: Bearer <token>`.
* **Cas à tester** :
  1. **Succès (200 OK)** :
     - *Commande* :
       ```bash
       curl -X POST http://localhost:5000/api/tours/optimize \
            -H "Authorization: Bearer <TOKEN>" \
            -H "Content-Type: application/json" \
            -d '{"place_ids": [1, 2, 3], "locked_positions": {"3": 1}}'
       ```
     - *Résultat attendu* : Code 200, liste ordonnée des lieux (Marseille d'ID 3 est à l'index 1) et distance totale calculée.

---

### 4.6 Recherche et Pagination de Lieux/Itinéraires (`GET /api/places` / `GET /api/tours/public`)
* **Description** : Permet de chercher et paginer les résultats.
* **Cas à tester** :
  1. **Lieux publics paginés (200 OK)** :
     - *Commande* :
       ```bash
       curl -X GET "http://localhost:5000/api/places?visibility=public&q=Paris&page=1&limit=2"
       ```
     - *Résultat attendu* : Liste paginée filtrée contenant au plus 2 éléments.
  2. **Itinéraires publics paginés (200 OK)** :
     - *Commande* :
       ```bash
       curl -X GET "http://localhost:5000/api/tours/public?q=Voyage&page=1&limit=5"
       ```
     - *Résultat attendu* : Liste paginée des itinéraires publics filtrés par le terme "Voyage".

---

### 4.7 Santé Réseau et Base de Données (`GET /api/health/ready`)
* **Description** : Healthcheck complet testant la connectivité SQLite/PostgreSQL.
* **Cas à tester** :
  1. **Succès (200 OK)** :
     - *Commande* :
       ```bash
       curl -X GET http://localhost:5000/api/health/ready
       ```
     - *Résultat attendu* : Code 200, base de données joignable.
