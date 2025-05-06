# Convertisseur CSV vers VCF - Version 2.0

Application web permettant de convertir facilement et rapidement des listes de contacts provenant de fichiers CSV (typiquement exportés depuis Excel, Google Sheets ou autres tableurs) en format VCF (vCard) directement importable dans votre carnet d'adresses.

## Pourquoi cette application ?

La saisie manuelle de nombreux contacts dans une application de carnet d'adresses est extrêmement fastidieuse et chronophage. Cette application résout ce problème en permettant de :

1. Importer en une seule fois des dizaines ou centaines de contacts depuis un fichier CSV
2. Mapper automatiquement les colonnes (nom, téléphone, email) sans configuration complexe
3. Formater correctement les données (numéros de téléphone, séparation prénom/nom)
4. Générer un fichier VCF prêt à être importé dans n'importe quelle application de contacts

## Fonctionnalités

### Fonctionnalités de base
- Interface web conviviale et responsive
- Upload de fichiers CSV (exportés depuis Excel, Google Sheets, etc.)
- Prévisualisation des données CSV avant conversion
- Traitement intelligent de séparation prénom/nom
- Formatage automatique des numéros de téléphone (ajout de l'indicatif +33)
- Ajout d'une note commune à tous les contacts (optionnel)
- Traitement par lots de centaines de contacts en quelques secondes
- Téléchargement du fichier VCF généré
- Instructions d'importation pour l'application Contacts sur macOS

### Nouvelles fonctionnalités de la version 2.0
- Configuration dynamique des correspondances de colonnes
- Bouton de configuration par défaut pour une utilisation rapide
- Export/import des configurations pour réutilisation ultérieure
- Documentation intégrée dépliable pour chaque type de champ
- Détection de colonnes améliorée avec support de nombreux formats
- Mémorisation des configurations pendant la session
- Interface restructurée pour plus de clarté

## Prérequis

- Python 3.11+
- Un environnement virtuel Python (venv)

## Installation

1. Cloner le dépôt ou télécharger les fichiers
2. Activer l'environnement virtuel :
```
source .venv/bin/activate  # Sur macOS
```
3. Installer les dépendances :
```
pip install -r requirements.txt
```

## Utilisation

1. Lancer l'application :
```
streamlit run app.py
```

2. Accéder à l'application via le navigateur (par défaut : http://localhost:8503)

3. Importer un fichier CSV

4. Configurer les correspondances de colonnes 
   - Option 1 : Utiliser la configuration par défaut
   - Option 2 : Configurer manuellement via le formulaire

5. Convertir et télécharger le fichier VCF

## Gestion des configurations

L'application permet d'exporter et d'importer des configurations pour faciliter l'utilisation avec différents formats de fichiers CSV. Une fois une configuration enregistrée, vous pouvez :

1. Télécharger la configuration sous format JSON
2. Réutiliser cette configuration ultérieurement via la fonction d'import

1. Lancer l'application :
```
streamlit run app.py
```
2. Ouvrir votre navigateur à l'adresse indiquée (généralement http://localhost:8501)
3. Suivre les instructions à l'écran pour :
   - Télécharger votre fichier CSV
   - Sélectionner le délimiteur (si différent de ';')
   - Ajouter une note commune (facultatif)
   - Convertir et télécharger le fichier VCF

## Format des fichiers CSV attendus

L'application recherche les colonnes suivantes (différentes variantes sont acceptées) :
- "Prénom Nom", "Nom Prénom", ou "Nom" pour les informations de nom
- "Téléphone", "Tel", "Tél", ou "Mobile" pour les numéros de téléphone
- "Mail", "Email", ou "Courriel" pour les adresses email
- "Role", "Rôle", ou "Fonction" pour les fonctions/rôles
- "Agent" ou "Agence" pour les informations d'agent
- "Adresse" ou "Adresse postale" pour les adresses

## Déploiement sur Streamlit Cloud

Cette application peut être facilement déployée sur Streamlit Cloud :
1. Créer un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connecter votre dépôt GitHub
3. Déployer l'application en quelques clics

## Développeur

Développé par Michel Safars pour Romain.
