# DEVBOOK - Convertisseur CSV vers VCF

## Présentation du projet

Ce projet est une application Streamlit conçue pour convertir des fichiers CSV contenant des contacts en format VCF (vCard), compatible avec la plupart des applications de carnet d'adresses.

### Fonctionnalités principales

- Importation de fichiers CSV avec détection automatique du délimiteur
- Conversion en format VCF (vCard version 3.0)
- Prévisualisation des données CSV importées
- Ajout d'une note commune à tous les contacts
- Téléchargement direct du fichier VCF généré
- Séparation intelligente des prénoms et noms
- Formatage des numéros de téléphone avec l'indicatif international (+33)

### Technologie utilisée

- Python 3.11+
- Streamlit pour l'interface web
- Bibliothèques standard Python (csv, io, os, datetime, etc.)

## Architecture de l'application

### Structure du code

Le code est organisé autour de plusieurs fonctions principales :

- `formater_nom`: Formate un nom pour avoir les premières lettres en majuscule
- `separer_prenom_nom`: Sépare intelligemment une chaîne contenant prénom et nom
- `trouver_colonne_correspondante`: Trouve la colonne correspondante parmi plusieurs noms possibles
- `convertir_csv_en_vcf`: Fonction principale qui réalise la conversion CSV → VCF
- `main`: Point d'entrée de l'application Streamlit et interface utilisateur

### Logique de conversion

1. L'utilisateur téléverse un fichier CSV
2. Le système identifie les colonnes du CSV et tente de les associer aux champs attendus (nom, téléphone, email, etc.)
3. Pour chaque ligne du CSV, une entrée VCard est générée avec les informations disponibles
4. Le fichier VCF complet est généré et proposé au téléchargement

## Améliorations

### Version 1.0.0 - 1.1.0 (versions locales)
- Version initiale avec conversion basique
- Ajout de la prévisualisation des données
- Amélioration du formatage des noms et de la séparation prénom/nom
- Gestion des indicatifs téléphoniques internationaux
- Détection du délimiteur CSV

### Version 2.0.0 - 2.0.7 (versions Streamlit)
- Migration vers une interface web avec Streamlit
- Amélioration de la gestion dynamique des noms de colonnes
- Interface pour configurer manuellement les correspondances de colonnes
- Support de formats CSV plus variés
- Documentation complète (DEVBOOK)

### Version 2.0.8 (stable)
- Interface optimisée pour ordinateur (mise en page large)
- Support des colonnes séparées "Prénom" et "NOM" ou colonne combinée
- Conservation des majuscules dans les noms de famille
- Mode débogage pour afficher le contenu brut du fichier VCF
- Correction de tous les bugs connus

### Version 2.0.9
- Mise à jour des métadonnées du projet
- Amélioration de la documentation
- Cohérence des versions entre l'application et le projet

### Version 2.1.0 (actuelle)
- Correction du problème d'importation VCF dans les applications de contacts
- Suppression de l'en-tête non standard `X-ADDRESSBOOK-NAME` qui causait des problèmes d'importation
- Uniformisation du titre avec "V2" au lieu de "v2.0.1"
- Configuration du dépôt GitHub pour le partage du code
- Améliorations mineures du formatage du code

## Gestion des noms de colonnes

### Approche actuelle (v2.0.9)

L'application tente de trouver les colonnes utiles dans le CSV en cherchant parmi des noms prédéfinis :

```python
# Définir les noms possibles pour chaque type de colonne
noms_role = ["Role", "Rôle", "Fonction"]
noms_nom = ["Prénom Nom", "Nom Prénom", "Nom"]
noms_tel = ["Téléphone", "Tel", "Tél", "Mobile"]
noms_email = ["Mail", "Email", "Courriel"]
noms_adresse = ["Adresse", "Adresse postale"]
noms_agent = ["Agent", "Agence"]
```

Cette approche présente des limitations quand les fichiers CSV utilisent des noms de colonnes différents.

### Nouvelle approche (v1.2.0)

L'idée est de permettre à l'utilisateur de configurer lui-même les correspondances entre les colonnes de son CSV et les champs VCF, avec une interface intuitive et une détection automatique améliorée.

#### Améliorations prévues :

1. Détection automatique intelligente avec une liste étendue de noms possibles
2. Interface permettant à l'utilisateur de sélectionner manuellement les correspondances
3. Sauvegarde des préférences pour une réutilisation future
4. Support de colonnes personnalisées pour des champs VCF additionnels

## Prochaines étapes

1. Implémenter l'interface de configuration des colonnes
2. Ajouter le support de formats CSV plus exotiques
3. Améliorer la gestion des erreurs
4. Ajouter des tests unitaires complets
