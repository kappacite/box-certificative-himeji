# Suivi — Modèles de Données (dataobject)

Cette partie contient les objets de données purs (dataclasses) transférés entre les différentes couches de l'application.

---

## 📂 Fichiers concernés
* [backend/dataobject/user.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/user.py)
* [backend/dataobject/place.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/place.py)
* [backend/dataobject/tour.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/tour.py)
* [backend/dataobject/\_\_init\_\_.py](file:///home/robyn/Documents/Programmation/box-certificative-himeji/backend/dataobject/__init__.py)

---

## 🛠️ Respect des principes SOLID

* **S — Single Responsibility Principle (SRP)** :
  - Les classes `User`, `Place` et `Tour` sont des conteneurs de données purs (dataclasses). Leur unique responsabilité est de structurer et de représenter l'état des entités. Elles ne contiennent aucune logique métier, aucun accès à la base de données, ni aucun traitement HTTP.
* **O — Open/Closed Principle (OCP)** :
  - Les dataclasses sont conçues pour être extensibles. L'ajout d'un champ ou d'une propriété n'altère pas les contrats d'échange existants et ne nécessite pas de modifier la structure interne des couches supérieures (services, routes).
* **L — Liskov Substitution Principle (LSP)** :
  - Les structures de données héritent directement de `object` et s'appuient sur le typage natif de Python, garantissant que toute sous-classe éventuelle respectera le contrat de typage.
* **I — Interface Segregation Principle (ISP)** :
  - Les interfaces des dataclasses sont extrêmement réduites (`to_dict` et `from_dict`), évitant d'exposer des méthodes inutiles aux clients de cette couche.
* **D — Dependency Inversion Principle (DIP)** :
  - Les objets de données ne dépendent d'aucune bibliothèque externe de persistance (comme SQLAlchemy) ni d'aucun framework de routage. Ils forment un noyau stable sur lequel reposent toutes les autres couches de l'application (DIP respecté par l'indépendance de ce noyau).

---

## 📝 Suivi détaillé des fonctionnalités

| Fichier / Élément | État | Problèmes identifiés | Actions correctives / Évolutions |
| :--- | :--- | :--- | :--- |
| `user.py` | 🟢 Complet | Aucune validation du format de l'adresse e-mail ou de la force du mot de passe dans l'objet de données. | Ajouter un validateur externe ou intégrer une validation dans `from_dict` pour s'assurer de l'intégrité de l'e-mail. |
| `place.py` | 🟢 Complet | Manque de validation géométrique des plages de coordonnées (latitude $\in [-90, 90]$, longitude $\in [-180, 180]$). | Ajouter une validation des coordonnées lors de l'instanciation de l'objet (ou dans la méthode `from_dict`). |
| `tour.py` | 🟢 Complet | Aucun problème identifié. Le chaînage récursif pour parser la liste des `Place` fonctionne correctement. | RAS. |
