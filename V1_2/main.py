# main.py MS
#
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from utils import convertir_csv_en_vcf


def afficher_message_accueil():
    message = """CONVERTISSEUR CSV VERS CONTACTS (VCF)

Programme développé par Michel Safars pour Romain, le futur grand réalisateur de cinéma.

Ce programme va vous aider à convertir votre fichier CSV en carnet d'adresses.

Fonctionnalités :
• Conversion d'un fichier CSV en format VCF (compatible avec l'app Contacts)
• Gestion des champs : Rôle, Nom, Téléphone, Email et Agent
• Possibilité d'ajouter une note commune à tous les contacts
• Le fichier VCF sera créé au même endroit que votre fichier CSV

À la prochaine étape, vous devrez :
1. Sélectionner votre fichier CSV
2. Entrer une note commune (optionnelle) qui sera ajoutée à toutes les fiches dans le champ Note

(Utiliser la touche "ESC" pour annuler)

Cliquez sur OK pour commencer."""

    root = tk.Tk()
    root.withdraw()
    reponse = messagebox.showinfo("Bienvenue", message)
    return reponse


def main():
    # Afficher le message d'accueil
    afficher_message_accueil()

    # Obtenir le répertoire du script main.py
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Initialiser tkinter et cacher la fenêtre principale
    root = tk.Tk()
    root.withdraw()

    # Ouvrir la boîte de dialogue de sélection de fichier
    fichier_choisi = filedialog.askopenfilename(
        title="Sélectionner le fichier CSV des contacts",
        filetypes=[("Fichiers CSV", "*.csv")],
        initialdir=os.path.join(script_dir, "../data")
    )

    # Si aucun fichier n'est choisi, afficher un message et quitter
    if not fichier_choisi:
        messagebox.showwarning(
            "Aucun fichier sélectionné",
            "Vous n'avez pas sélectionné de fichier CSV.\nLe programme va se terminer."
        )
        return

    # Utiliser le fichier choisi
    chemin_csv = fichier_choisi

    # Créer le chemin du fichier VCF avec le même nom que le CSV
    nom_base = os.path.splitext(os.path.basename(chemin_csv))[0]  # Récupère le nom sans extension
    chemin_vcf = os.path.join(os.path.dirname(chemin_csv), f"{nom_base}.vcf")

    # Demander à l'utilisateur s'il souhaite ajouter une note commune
    note_commune = simpledialog.askstring(
        "Note commune",
        "Souhaitez-vous ajouter une note commune à toutes les fiches ?\n"
        "(Laissez vide si non)",
        parent=root
    )

    # Normaliser les chemins
    chemin_csv = os.path.normpath(chemin_csv)
    chemin_vcf = os.path.normpath(chemin_vcf)

    # Impressions de débogage
    print(f"Chemin CSV résolu : {chemin_csv}")
    print(f"Chemin VCF résolu : {chemin_vcf}")

    # Convertir le fichier avec la note commune si elle existe
    print("Conversion en cours...")
    convertir_csv_en_vcf(chemin_csv, chemin_vcf, note_commune)
    print(f"Conversion terminée. Le fichier VCF a été créé : {chemin_vcf}")

    # Afficher un message de succès
    messagebox.showinfo(
        "Conversion terminée",
        f"Le fichier de contacts a été créé avec succès !\n\n"
        f"Vous le trouverez ici :\n{chemin_vcf}\n\n"
        "Pour l'importer dans Contacts :\n"
        "1. Ouvrez l'application Contacts\n"
        "2. Menu Fichier > Importer\n"
        "3. Sélectionnez le fichier VCF créé"
    )


if __name__ == "__main__":
    main()
