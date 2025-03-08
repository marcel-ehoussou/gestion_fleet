# Fleet Advanced Management Module

## Vue d'ensemble
Le module Fleet Advanced Management fournit une solution complète de gestion de flotte pour Odoo. Il permet de gérer efficacement les véhicules, les conducteurs, la maintenance, les réservations et les documents associés.

## Fonctionnalités Principales

### Gestion des Véhicules
- **Informations Détaillées**
  - Caractéristiques techniques
  - Historique d'utilisation
  - Suivi des coûts
  - Documents associés

- **Suivi des Performances**
  - Consommation de carburant
  - Kilométrage
  - État général
  - Historique des interventions

### Gestion des Conducteurs
- **Profils Conducteurs**
  - Informations personnelles
  - Qualifications
  - Licences et permis
  - Historique de conduite

- **Suivi des Activités**
  - Assignations de véhicules
  - Historique des trajets
  - Évaluation des performances
  - Gestion des disponibilités

### Gestion de la Maintenance
- **Maintenance Préventive**
  - Planification des entretiens
  - Alertes automatiques
  - Suivi des interventions
  - Historique complet

- **Réparations**
  - Enregistrement des pannes
  - Suivi des réparations
  - Gestion des coûts
  - Rapports d'intervention

### Système de Réservation
- **Réservation de Véhicules**
  - Calendrier de disponibilité
  - Gestion des conflits
  - Validation des demandes
  - Suivi des utilisations

- **Gestion des Plannings**
  - Vue calendrier
  - Optimisation des ressources
  - Notifications automatiques
  - Rapports d'utilisation

### Gestion des Documents
- **Suivi Documentaire**
  - Stockage centralisé
  - Gestion des échéances
  - Alertes de renouvellement
  - Archivage numérique

- **Types de Documents**
  - Assurances
  - Contrôles techniques
  - Permis de conduire
  - Documents administratifs

### Gestion des Dépenses
- **Suivi des Coûts**
  - Carburant
  - Maintenance
  - Assurances
  - Autres dépenses

- **Analyse Financière**
  - Rapports détaillés
  - Analyse des coûts
  - Budgétisation
  - Prévisions

## Installation

### Prérequis
- Odoo 16.0 ou supérieur
- PostgreSQL 12+
- Python 3.8+

### Étapes d'Installation
1. Cloner le projet gestion_fleet dans le répertoire addons d'Odoo :
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/your-repository/gestion_fleet.git
   ```

2. Mettre à jour le fichier de configuration Odoo :
   ```
   addons_path = /path/to/odoo/addons,/path/to/odoo/addons/gestion_fleet
   ```

3. Installer les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

4. Redémarrer le serveur Odoo :
   ```bash
   service odoo restart
   ```

5. Installer le module via l'interface Odoo :
   - Aller dans Apps
   - Retirer le filtre 'Apps'
   - Rechercher 'Fleet Advanced Management'
   - Cliquer sur Installer

## Configuration

### Groupes de Sécurité
- **Utilisateur Fleet**
  - Accès en lecture aux données
  - Création de réservations
  - Consultation des documents

- **Manager Fleet**
  - Accès complet
  - Configuration du système
  - Gestion des droits
  - Validation des opérations

### Configuration Initiale
1. **Paramètres Généraux**
   - Types de véhicules
   - Catégories de dépenses
   - Types de documents
   - Règles de réservation

2. **Paramètres Avancés**
   - Workflow de validation
   - Règles de notification
   - Seuils d'alerte
   - Modèles de rapports

## Structure du Module
```
gestion_fleet/                 # Répertoire principal du projet
└── fleet_advanced_management/ # Module de gestion de flotte
    ├── README.md             # Documentation du module
    ├── __init__.py           # Point d'entrée du module
    ├── __manifest__.py       # Descripteur du module
    ├── models/               # Modèles de données
    │   ├── __init__.py
    │   ├── fleet_vehicle.py       # Gestion des véhicules
    │   ├── fleet_driver.py        # Gestion des conducteurs
    │   ├── fleet_maintenance.py   # Gestion de la maintenance
    │   ├── fleet_reservation.py   # Système de réservation
    │   ├── fleet_expense.py       # Gestion des dépenses
    │   └── fleet_document.py      # Gestion documentaire
    ├── views/                # Vues et interfaces utilisateur
    │   ├── fleet_vehicle_views.xml
    │   ├── fleet_driver_views.xml
    │   ├── fleet_maintenance_views.xml
    │   ├── fleet_reservation_views.xml
    │   ├── fleet_expense_views.xml
    │   └── fleet_document_views.xml
    ├── security/             # Configuration de sécurité
    │   ├── fleet_security.xml     # Règles de sécurité
    │   └── ir.model.access.csv    # Droits d'accès
    └── data/                # Données de configuration
        └── fleet_data.xml         # Données de démonstration
```

## Guide d'Utilisation

### Opérations Quotidiennes
1. **Gestion des Véhicules**
   ```
   Fleet > Véhicules > Véhicules
   ```
   - Ajout/modification de véhicules
   - Suivi de l'état
   - Consultation des documents

2. **Gestion des Conducteurs**
   ```
   Fleet > Conducteurs > Conducteurs
   ```
   - Gestion des profils
   - Assignation des véhicules
   - Suivi des activités

3. **Maintenance**
   ```
   Fleet > Opérations > Maintenance
   ```
   - Planification des entretiens
   - Suivi des réparations
   - Gestion des coûts

4. **Réservations**
   ```
   Fleet > Opérations > Réservations
   ```
   - Création de réservations
   - Gestion du calendrier
   - Suivi des utilisations

### Rapports et Analyses
- Coûts par véhicule
- Utilisation de la flotte
- Performance des conducteurs
- Analyse des dépenses

## Développement

### Extension du Module
1. Respecter l'architecture Odoo
2. Utiliser l'héritage approprié
3. Maintenir la sécurité
4. Documenter les modifications

### Bonnes Pratiques
- Tests unitaires
- Documentation du code
- Gestion des dépendances
- Optimisation des performances

## Support et Maintenance

### Support Technique
- Documentation en ligne
- Support par email
- Formation utilisateur
- Assistance développeur

### Maintenance
- Mises à jour régulières
- Corrections de bugs
- Améliorations continues
- Sauvegardes recommandées

## Licence
LGPL-3

## Auteurs
- Votre Entreprise
- Liste des contributeurs
