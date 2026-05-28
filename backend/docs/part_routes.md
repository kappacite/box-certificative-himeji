# Suivi — Couche HTTP (routes)

Cette partie contient les Blueprints Flask responsables uniquement de l'interface HTTP (validation des requêtes entrantes, décodage JSON et structuration des réponses JSON de l'API).

---

## 📂 Fichiers concernés
* [backend/routes/auth_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/routes/auth_routes.py)
* [backend/routes/place_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/routes/place_routes.py)
* [backend/routes/tour_routes.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/routes/tour_routes.py)
* [backend/routes/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/routes/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - Les Blueprints gèrent uniquement les aspects HTTP : réception des requêtes, décapsulage des données JSON, appel des méthodes de services appropriées, renvoi des codes de statut HTTP adéquats (200, 201, 204). Ils ne contiennent aucun accès SQL direct ni aucune logique métier.
* **O — Open/Closed Principle (OCP)** :
  - Les routes délèguent l'exécution de la logique métier aux services. Une modification des règles de calcul (ex: changement de l'algorithme d'optimisation) ne nécessite aucun changement dans les fichiers de routes.
* **L — Liskov Substitution Principle (LSP)** :
  - Les réponses HTTP s'appuient sur les dataclasses stables de `dataobject`. Le remplacement ou la spécialisation d'une structure de données respecte toujours le format de sérialisation JSON attendu par les routes.
* **I — Interface Segregation Principle (ISP)** :
  - Les Blueprints séparent logiquement les domaines fonctionnels de l'application (`auth_routes` pour l'authentification, `place_routes` pour les lieux, `tour_routes` pour les itinéraires), empêchant un couplage global.
* **D — Dependency Inversion Principle (DIP)** :
  - Les Blueprints dépendent de la couche de services métier globale. Pour pousser le découplage encore plus loin, il serait possible d'injecter les services dans les Blueprints plutôt que de les instancier au niveau du module.

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `auth_routes.py` | 🟢 Complet | RAS. Les routes `/register`, `/login` et `/logout` sont conformes. | RAS. |
| `place_routes.py` | 🟢 Complet | La conversion des coordonnées (`latitude`/`longitude`) est faite manuellement dans la route avec des blocs try/except implicites ou conversions de types directes (`float`). | Utiliser une validation de schéma plus robuste pour s'assurer que les valeurs reçues sont bien des nombres réels valides avant de faire appel au service. |
| `tour_routes.py` | 🟢 Complet | Les opérations de suppression renvoient un corps vide avec le code `204 No Content`, ce qui est conforme au protocole HTTP, mais le frontend pourrait préférer un message de confirmation JSON standardisé. | Rester sur la norme stricte `204 No Content` sans corps, ou retourner un message de succès selon le choix final de conception de l'application cliente. |
