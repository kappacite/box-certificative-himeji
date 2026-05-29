# Suivi du Projet Backend — Himeji Planner API

Ce document récapitule l'état d'avancement de l'implémentation du backend, l'analyse des fichiers sources, les problèmes identifiés, ainsi que les pistes d'amélioration ou de corrections en attente.

---

## 📊 État d'avancement général

| Composant | Statut | Description |
| :--- | :--- | :--- |
| [Configuration & Initialisation](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#1-single-responsibility-principle-srp) | 🟢 Complet | Configuration d'environnement et initialisation de l'application Flask. |
| [Couche Modèles (dataobject/)](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#1-single-responsibility-principle-srp) | 🟢 Complet | Conteneurs de données purs pour `User`, `Place` et `Tour`. |
| [Couche Accès Données (dao/)](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#3-liskov-substitution-principle-lsp) | 🟢 Complet | Architecture BaseDAO générique, modèles SQLAlchemy et classes DAO spécifiques. |
| [Couche Services métier (services/)](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#5-dependency-inversion-principle-dip) | 🟢 Complet | Chiffrement bcrypt, gestion JWT, géocodage Nominatim et heuristique TSP. |
| [Algorithmes d'optimisation](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#%F0%9F%A7%A0-core-optimization-engine-tsp-solver) | 🟢 Complet | Distance de Haversine exacte et solveur TSP professionnel avec Google OR-Tools. |
| [Couche Routes API (routes/)](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#4-interface-segregation-principle-isp) | 🟢 Complet | Endpoints REST conformes, gestion des réponses normalisées et codes HTTP. |
| [Middlewares & Exceptions](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#architectural-layers) | 🟢 Complet | Décorateurs d'authentification (`@require_auth`) et de propriété (`@require_owner`), gestionnaire global d'erreurs. |
| [Suite de Tests (tests/)](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/docs/TECHNICAL_DOCUMENTATION.md#%F0%9F%A7%AA-testing--verification) | 🟢 Complet | 19 tests unitaires et intégration couvrant 100% des cas d'utilisation clés. |
| **Formatage & Linting** | 🟢 Complet | Nettoyage complet sous `black` et linter `flake8` valide à 100%. |

*Légende : 🔴 Non démarré | 🟡 En cours | 🟢 Complet / Validé*

---

## 🔍 Analyse détaillée par fichier source

### 1. Configuration & Initialisation

#### 📄 [backend/app.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/app.py)
* **Rôle** : Fabrique d'application Flask, initialisation CORS, SQLAlchemy, routes et gestion globale.
* **Problèmes identifiés** :
  - Utilisation de `db.create_all()` pour initialiser la base SQLite. C'est pratique en développement, mais peu adapté pour la production en cas de mise à jour de schéma.
* **Actions à mener / Pistes d'amélioration** :
  - Envisager l'intégration de `Flask-Migrate` (Alembic) pour gérer de vraies migrations de base de données.

#### 📄 [backend/config.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/config.py)
* **Rôle** : Classes de configuration pour les environnements de développement, test et production.
* **Problèmes identifiés** :
  - Aucun problème majeur de sécurité détecté (la clé secrète est bien chargée depuis les variables d'environnement).
* **Actions à mener / Pistes d'amélioration** :
  - Ajouter des configurations optionnelles de timeout pour les connexions DB.

---

### 2. Modèles de Données (`dataobject/`)

#### 📄 [backend/dataobject/user.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/user.py)
* **Rôle** : Dataclass représentant un utilisateur avec méthode de sérialisation.
* **Problèmes identifiés** :
  - Pas de validation stricte du format des données directement dans la dataclass (ex. format de l'e-mail ou longueur minimale du pseudo).
* **Actions à mener** :
  - Ajouter une méthode de validation interne ou un validateur dédié dans un module utilitaire.

#### 📄 [backend/dataobject/place.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/place.py)
* **Rôle** : Dataclass représentant un lieu géographique (latitude/longitude).
* **Problèmes identifiés** :
  - Pas de validation sur les plages de coordonnées acceptables (la latitude doit être entre -90 et 90, la longitude entre -180 et 180).
* **Actions à mener** :
  - Ajouter une vérification lors du `from_dict` pour lever une `ValidationException` si les coordonnées sont hors limites.

#### 📄 [backend/dataobject/tour.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/tour.py)
* **Rôle** : Dataclass représentant un itinéraire ordonné.
* **Problèmes identifiés** :
  - Aucun. La reconstruction récursive à partir d'un dictionnaire est correctement gérée.

---

### 3. Couche d'Accès aux Données (`dao/`)

#### 📄 [backend/dao/models.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/models.py)
* **Rôle** : Modèles SQLAlchemy définissant les tables SQL (`users`, `places`, `tours`, `tour_places`).
* **Problèmes identifiés** :
  - Manque d'index sur les colonnes fréquemment recherchées en base de données comme `places.owner_id` ou `tours.owner_id`.
* **Actions à mener** :
  - Ajouter `index=True` sur les clés étrangères et sur la colonne `share_token` de `TourModel` pour optimiser les requêtes de lecture.

#### 📄 [backend/dao/tour_dao.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dao/tour_dao.py)
* **Rôle** : Persistance complexe de l'itinéraire et de sa relation ordonnée plusieurs-à-plusieurs.
* **Problèmes identifiés** :
  - En cas de modification d'itinéraire (`update`), la DAO supprime toutes les liaisons dans `tour_places` avant d'insérer les nouvelles. Bien que simple et fonctionnel, cela peut générer des pics d'écriture inutiles si la liste n'a pas changé.
* **Actions à mener** :
  - Optimiser l'écriture en comparant les listes de lieux avant de procéder à une suppression globale.

---

### 4. Algorithmes (`services/algorithm/`)

#### 📄 [backend/services/algorithm/distance.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/distance.py)
* **Rôle** : Formule de Haversine pour la distance de grand cercle.
* **Problèmes identifiés** :
  - Le calcul utilise `math.acos`. Pour de très courtes distances ou des points identiques, les arrondis en virgule flottante peuvent générer des valeurs supérieures à `1.0` (ex: `1.0000000002`), ce qui lève une exception mathématique dans `acos`.
* **Actions à mener** :
  - *Corrigé* : Le code bride désormais la valeur d'entrée de `acos` entre `-1.0` et `1.0` avec `max(-1.0, min(1.0, cos_val))`, résolvant définitivement ce problème.

#### 📄 [backend/services/algorithm/optimizer.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/algorithm/optimizer.py)
* **Rôle** : Solveur TSP de production utilisant la bibliothèque Google OR-Tools.
* **Problèmes identifiés** :
  - L'application de contraintes de dimension strictes (Step) directement dans OR-Tools provoquait des freezes (boucles de recherche locale infinies) sur des tournées volumineuses (ex: 200 lieux).
* **Actions menées & Corrections** :
  - *Corrigé* : Passage à une méthode hybride de résolution par sous-tours et insertion. Les lieux verrouillés sont retirés, les lieux restants sont optimisés via OR-Tools en moins d'une seconde, puis les lieux verrouillés sont réinsérés à leurs positions respectives.
  - *Garde-fou* : Ajout d'un paramètre de time-limit à 3 secondes dans les paramètres de recherche de la bibliothèque OR-Tools.

---

### 5. Services Métier (`services/`)

#### 📄 [backend/services/place_service.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/services/place_service.py)
* **Rôle** : Logique de gestion des points géographiques et géocodage.
* **Problèmes identifiés** :
  - L'API Nominatim d'OpenStreetMap possède des limites de requêtes strictes (rate-limiting) et peut être lente. Lancer une requête HTTP réseau synchrone à chaque création ou modification de lieu ralentit l'expérience utilisateur et s'avère fragile si le service externe subit une panne.
* **Actions à mener** :
  - Implémenter une table de cache SQL locale `geocoding_cache` pour éviter de requêter Nominatim plusieurs fois pour le même nom de ville.

---

### 6. Middlewares & Erreurs

#### 📄 [backend/middleware/auth_middleware.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/middleware/auth_middleware.py)
* **Rôle** : Décorateurs d'authentification (`require_auth`) et de propriété (`require_owner`).
* **Problèmes identifiés** :
  - Le décorateur `@require_owner` importe et instancie dynamiquement les services à chaque requête pour vérifier les droits. Cela crée des dépendances d'importation circulaires tardives bien que fonctionnelles.
* **Actions à mener** :
  - Utiliser un mécanisme d'injection de dépendances ou centraliser les vérifications de propriété dans la couche de service pour alléger le décorateur HTTP.

#### 📄 [backend/middleware/error_handler.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/middleware/error_handler.py)
* **Rôle** : Gestion globale des erreurs avec formatage enveloppe JSON normalisé.
* **Problèmes identifiés** :
  - Aucun. Gère parfaitement les erreurs HTTP standard, les exceptions métier et les crashs serveurs inattendus (500) en masquant la stack trace aux clients.

---

## 📅 Roadmap / Éléments en attente

### Court terme (Sécurité & Robustesse)
1. **Validation fine des entrées** : Mettre en place un système de regex robuste pour la validation des formats d'e-mail dans le `AuthService` et la validation géométrique des coordonnées (-90/90, -180/180) dans le `PlaceService`.
2. **Indexation SQL** : Indexer la colonne `share_token` (UUID) de la table `tours` pour accélérer l'accès aux circuits publics partagés.

### Moyen terme (Optimisation & Production)
1. **Cache de géocodage** : Mettre en cache les requêtes de géocodage Nominatim afin de respecter les conditions d'utilisation d'OpenStreetMap et d'accélérer drastiquement la création de lieux.
2. **Migrations de base de données** : Configurer `Flask-Migrate` pour faciliter le déploiement en production et les futures évolutions du schéma de base de données.
3. **Limitation de taille du TSP** : Mettre en place une validation de taille maximale dans la requête POST `/api/tours` (ex: limite de 50 lieux maximum) afin de prémunir le serveur synchrone contre les attaques par déni de service (CPU exhaustion sur le 2-opt).
