# Convertisseur CSV vers VCF — Version 1.2 (Tkinter)

**Auteur : Michel Safars**

---

## Présentation
Cette version 1.2 (A1.2) est une application locale avec interface graphique Tkinter permettant de convertir facilement un fichier CSV de contacts en carnet d’adresses VCF (vCard 3.0).

- **100% locale** : aucune connexion internet requise
- **Interface graphique native** (fenêtres Windows/macOS/Linux)
- **Ajout d’une note commune** à tous les contacts
- **Champs gérés** : Rôle, Nom, Téléphone, Email, Agent
- **Fichier VCF généré** au même emplacement que le CSV source

### Genèse de la version 1.2
Cette application a été développée par Michel Safars pour son fils Romain qui avait besoin de convertir rapidement et simplement des fichiers de noms en fiches VCF pour ses contacts professionnels et personnels. Il s'agit de la toute première version, pensée pour fonctionner entièrement en local, sans connexion internet ni installation complexe. L'objectif était la simplicité, la rapidité et l'efficacité pour un usage familial immédiat.

---

## Installation

1. **Prérequis** :
   - Python 3.11+ (installé via Homebrew sur Mac)
   - Aucun package externe requis (Tkinter est inclus dans Python standard)

2. **Structure du dossier** :
   ```
   V1_2/
   ├── main.py      # Lanceur de l’application graphique
   ├── utils.py     # Fonctions de conversion et utilitaires
   ```

---

## Utilisation

1. Double-cliquez sur `main.py` ou lancez-le en console :
   ```bash
   python main.py
   ```
2. Suivez les instructions à l’écran :
   - Sélectionnez le fichier CSV à convertir
   - Saisissez une note commune (optionnelle)
   - Le fichier VCF sera généré automatiquement

**Remarque** :
- Le CSV doit comporter des colonnes standards (Nom, Prénom, Téléphone, etc.).
- Le formatage des noms est automatique.

---

## Historique
- **v1.2** : Version Tkinter locale (ex-Conv-1.0) — Mai 2025
- **v2**   : Version web Streamlit

---

## Auteur
Michel Safars — 2025
