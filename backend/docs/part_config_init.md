# Suivi — Configuration et Initialisation

Cette partie regroupe les fichiers de configuration de l'application et la fabrique Flask.

---

## 📂 Fichiers concernés
* [backend/config.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/config.py)
* [backend/app.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/app.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - `config.py` a pour unique responsabilité la définition des variables de configuration pour chaque environnement de l'application.
  - `app.py` a pour unique responsabilité la création et l'assemblage de l'instance Flask (configuration, enregistrement des Blueprints, liaisons des middlewares et création des tables initiales).
* **O — Open/Closed Principle (OCP)** :
  - La configuration utilise le principe de spécialisation de classe : `Config` définit les variables communes, tandis que `DevelopmentConfig`, `TestingConfig`, et `ProductionConfig` étendent cette configuration sans modifier la classe parente. L'ajout d'un nouvel environnement (ex: `StagingConfig`) s'effectue par extension sans toucher au code existant.
* **L — Liskov Substitution Principle (LSP)** :
  - Les classes dérivées de `Config` sont substituables entre elles dans la fabrique d'application Flask sans risque de rupture logicielle.
* **I — Interface Segregation Principle (ISP)** :
  - Flask-SQLAlchemy et CORS utilisent des interfaces simples d'initialisation (`init_app`), ne forçant pas l'application à dépendre de méthodes inutiles.
* **D — Dependency Inversion Principle (DIP)** :
  - La fabrique d'application `create_app` accepte un nom de configuration dynamique en paramètre, évitant un couplage fort avec une configuration spécifique codée en dur.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `config.py` | 🟢 Complet | Aucun problème majeur de sécurité ou d'architecture. | RAS. |
| `app.py` (Fabrique) | 🟢 Complet | L'appel à `db.create_all()` est synchrone au démarrage de l'app. | Pour la production, migrer vers `Flask-Migrate` (Alembic) pour des migrations découplées et versionnées. |
| Configuration CORS | 🟢 Complet | CORS accepte actuellement toutes les origines (`CORS(app)`). | En production, restreindre aux domaines autorisés (ex: l'URL du frontend uniquement). |
