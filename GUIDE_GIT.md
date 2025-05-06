# Guide Git — Projet Convertisseur CSV vers VCF

## Objectif
Mettre en place un suivi de version clair, sécurisé et adapté au développement collaboratif ou individuel du projet, en respectant les bonnes pratiques modernes et la structure souhaitée.

---

## 1. Initialisation du dépôt

1. Placez-vous à la racine du projet :
   ```bash
   cd /Users/M/Documents/Dev_Mike_All/PYTHON_Michel/DEV_PyMike/pyMS_CarnetCode_1.2/convertisseur_csv_vers_vcf_Streamlit
   ```
2. Initialisez le dépôt Git :
   ```bash
   git init
   ```
3. Ajoutez tous les fichiers existants :
   ```bash
   git add .
   ```
4. Premier commit :
   ```bash
   git commit -m "Initialisation du dépôt : version stable locale et Streamlit"
   ```

---

## 2. Fichier .gitignore recommandé

Créez un fichier `.gitignore` à la racine avec :
```gitignore
# Environnements virtuels
.venv/

# Fichiers temporaires Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Fichiers système
.DS_Store
Thumbs.db

# Fichiers de configuration d’IDE
.idea/
.vscode/
*.swp

# Données utilisateur/test
/data/
*.csv
*.vcf
*.json

# Sauvegardes
*~
```

---

## 3. Bonnes pratiques de commit
- Commits courts, explicites et en français.
- Un commit = une idée/un changement logique.
- Toujours tester avant de pousser.
- Utiliser des branches pour les évolutions majeures ou expérimentales :
  ```bash
  git checkout -b nouvelle-fonctionnalite
  ```

---

## 4. Structure recommandée

```
convertisseur_csv_vers_vcf_Streamlit/
├── V1_2/          # Version locale Tkinter (stable)
├── V2/            # Version Streamlit (web)
├── data/          # Fichiers de test (à ignorer dans git)
├── pyproject.toml # Dépendances et métadonnées
├── GUIDE_GIT.md   # Ce guide
└── ...
```

---

## 5. Publication sur GitHub

1. Créez un nouveau dépôt vide sur GitHub (web).
2. Ajoutez le remote :
   ```bash
   git remote add origin git@github.com:<utilisateur>/<nom-du-depot>.git
   ```
3. Poussez la branche principale :
   ```bash
   git push -u origin master
   # ou
   git push -u origin main
   ```

---

## 6. Sécurité et confidentialité
- **Ne jamais versionner les données personnelles, fichiers CSV/VCF réels, ni les fichiers de configuration contenant des secrets.**
- Vérifier le `.gitignore` avant chaque commit.

---

## 7. Collaboration
- Toujours synchroniser (`git pull`) avant de commencer une nouvelle session de développement.
- Privilégier les Pull Requests pour les modifications majeures.
- Documenter les choix importants dans le README ou un fichier `DEVBOOK.md`.

---

## 8. Restauration
- Pour restaurer un fichier ou le projet :
   ```bash
   git checkout <commit> -- <chemin/du/fichier>
   ```
- Pour cloner le projet sur une autre machine :
   ```bash
   git clone git@github.com:<utilisateur>/<nom-du-depot>.git
   ```

---

**En cas de doute, demander conseil avant de forcer un push ou de manipuler l’historique !**
