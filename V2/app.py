# -*- coding: utf-8 -*-
"""
Application Streamlit pour convertir des fichiers CSV en format VCF (carnet d'adresses).
Développé par Michel Safars pour Romain.
"""

import os
import csv
import io
import base64
import streamlit as st
import datetime
import pytz
import json
from typing import Dict, List, Optional, Tuple, Any

# Définition de la version et autres constantes
APP_VERSION = "2.0.9"
DATE_CREATION = "2025-05-05"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

# Définition du titre et de la description de l'application
st.set_page_config(
    page_title="Convertisseur CSV vers VCF",
    page_icon="📇",
    layout="wide",  # Utilisation de la mise en page large
    initial_sidebar_state="collapsed"  # Masquer la barre latérale par défaut
)

# Ajouter du CSS personnalisé pour élargir les colonnes des tableaux
st.markdown("""
<style>
    .stTable {
        width: 100% !important;
    }
    .stTable td {
        min-width: 120px !important;
        max-width: 300px !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* Limite la largeur maximale du contenu principal */
    .block-container {
        max-width: 1400px;
        padding-left: 5rem;
        padding-right: 5rem;
    }
</style>
""", unsafe_allow_html=True)

def formater_nom(nom: str, conserver_majuscules: bool = False) -> str:
    """
    Formate un nom pour avoir les premières lettres de chaque mot en majuscules.
    Exemple: "DUPONT" -> "Dupont", "DE LA TOUR" -> "De La Tour"

    Args:
        nom: Le nom à formater
        conserver_majuscules: Si True, conserve les noms entiers en majuscules tels quels
    """
    if not nom:
        return ""

    # Si le nom est entièrement en majuscules et qu'on veut conserver cela
    if conserver_majuscules and nom.upper() == nom:
        return nom

    # Séparer les mots et les formater individuellement
    mots = nom.lower().split()
    mots_formates = [mot.capitalize() for mot in mots]

    return " ".join(mots_formates)


def separer_prenom_nom(chaine: str) -> Tuple[str, str]:
    """
    Sépare une chaîne contenant prénom et nom.
    Le prénom est supposé être en premier, et le nom (souvent en majuscules) après.

    Exemples:
    - "Michel DUPONT" -> ("Michel", "Dupont")
    - "Jean-Pierre MARTIN" -> ("Jean-Pierre", "Martin")
    - "Marie-France de la TOUR" -> ("Marie-France", "De La Tour")
    """
    if not chaine:
        return "", ""

    # Diviser la chaîne en mots
    mots = chaine.strip().split()
    if not mots:
        return "", ""

    # Si un seul mot, le considérer comme prénom
    if len(mots) == 1:
        return mots[0], ""

    # Chercher la position de transition prénom/nom
    position_nom = 1  # Position par défaut

    # Cas spéciaux pour les prénoms composés avec tiret
    if len(mots) >= 2 and "-" in mots[0]:
        position_nom = 1

    # Cas des prénoms composés (Jean Pierre, Marie France, etc.)
    elif len(mots) >= 3:
        # Si le deuxième mot n'est pas en majuscules, il fait probablement partie du prénom
        if not mots[1].isupper() and len(mots[1]) > 1:
            position_nom = 2

    # Construire le prénom et le nom
    prenom = " ".join(mots[:position_nom])
    nom = " ".join(mots[position_nom:])

    # Formater le nom avec les premières lettres en majuscules
    nom = formater_nom(nom)

    return prenom, nom


def trouver_colonne_correspondante(colonnes: List[str], noms_possibles: List[str]) -> Optional[str]:
    """
    Trouve la colonne correspondante parmi plusieurs noms possibles.
    Retourne None si aucune correspondance n'est trouvée.
    """
    for nom in noms_possibles:
        if nom in colonnes:
            return nom
    return None


def generer_lien_telechargement_json(nom_fichier: str, mappings: Dict[str, str]) -> str:
    """
    Génère un lien de téléchargement pour un fichier JSON contenant les mappings.

    Args:
        nom_fichier: Nom du fichier CSV (utilisé pour nommer le fichier de configuration)
        mappings: Dictionnaire des mappings de colonnes

    Returns:
        HTML pour le lien de téléchargement
    """
    try:
        # Préparer les données de configuration
        config = {
            "nom_fichier": nom_fichier,
            "date_creation": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version_app": APP_VERSION,
            "mappings": mappings
        }

        # Convertir en JSON formaté
        json_str = json.dumps(config, indent=4, ensure_ascii=False)

        # Encoder en base64 pour le téléchargement
        b64 = base64.b64encode(json_str.encode('utf-8')).decode()

        # Créer le nom du fichier de configuration
        nom_base = os.path.splitext(nom_fichier)[0]
        nom_config = f"{nom_base}_config.json"

        # Générer le HTML pour le bouton de téléchargement
        href = f'<a href="data:application/json;base64,{b64}" download="{nom_config}">Télécharger la configuration</a>'
        return href
    except Exception as e:
        st.error(f"Erreur lors de la génération du lien de téléchargement : {str(e)}")
        return ""


def analyser_json_config(contenu_json: str) -> Dict[str, Any]:
    """
    Analyse le contenu d'un fichier JSON de configuration.

    Args:
        contenu_json: Contenu du fichier JSON

    Returns:
        Dictionnaire avec les informations de configuration
    """
    try:
        # Charger le JSON
        config = json.loads(contenu_json)

        # Vérifier la structure minimale requise
        if "mappings" not in config:
            st.error("Le fichier de configuration n'a pas le bon format (mappings manquants).")
            return {}

        return config
    except json.JSONDecodeError:
        st.error("Le fichier n'est pas un JSON valide.")
        return {}
    except Exception as e:
        st.error(f"Erreur lors de l'analyse du fichier de configuration : {str(e)}")
        return {}


def convertir_csv_en_vcf(contenu_csv: str, mappings_colonnes: Dict[str, str], note_commune: Optional[str] = None, delimiter: str = ';') -> str:
    """
    Convertit le contenu d'un fichier CSV en format VCF en utilisant des mappings de colonnes dynamiques.

    Args:
        contenu_csv: Contenu du fichier CSV en texte
        mappings_colonnes: Dictionnaire associant les types de champs aux noms de colonnes du CSV
        note_commune: Note à ajouter à toutes les fiches (optionnel)
        delimiter: Délimiteur utilisé dans le CSV (par défaut ';')

    Returns:
        Contenu du fichier VCF généré
    """
    try:
        # Préparer le tampon pour le VCF
        vcf_buffer = io.StringIO()

        # Lecture du CSV depuis le contenu
        csv_buffer = io.StringIO(contenu_csv)
        lecteur = csv.DictReader(csv_buffer, delimiter=delimiter)

        # Vérifiez si des colonnes sont détectées
        colonnes_disponibles = lecteur.fieldnames
        if not colonnes_disponibles:
            st.error("Aucune colonne détectée dans le fichier CSV.")
            return ""

        # Extraire les colonnes à partir des mappings
        prenom_nom_colonne = mappings_colonnes.get('nom', None)
        prenom_colonne = mappings_colonnes.get('prenom', None)
        nom_famille_colonne = mappings_colonnes.get('nom_famille', None)
        role_colonne = mappings_colonnes.get('role', None)
        tel_colonne = mappings_colonnes.get('telephone', None)
        email_colonne = mappings_colonnes.get('email', None)
        adresse_colonne = mappings_colonnes.get('adresse', None)
        agent_colonne = mappings_colonnes.get('agent', None)
        mots_cle_colonne = mappings_colonnes.get('mots_cle', None)
        relation_colonne = mappings_colonnes.get('relation', None)

        # Vérifier que les colonnes essentielles sont présentes
        # On doit avoir soit la colonne combinée nom/prénom, soit les deux colonnes nom et prénom séparées
        colonnes_nom_presentes = False
        if prenom_nom_colonne and prenom_nom_colonne in colonnes_disponibles:
            colonnes_nom_presentes = True
        elif prenom_colonne and nom_famille_colonne and prenom_colonne in colonnes_disponibles and nom_famille_colonne in colonnes_disponibles:
            colonnes_nom_presentes = True
        elif prenom_colonne and prenom_colonne in colonnes_disponibles:
            # On accepte d'avoir juste le prénom comme minimum
            colonnes_nom_presentes = True
        elif nom_famille_colonne and nom_famille_colonne in colonnes_disponibles:
            # On accepte d'avoir juste le nom comme minimum
            colonnes_nom_presentes = True

        if not colonnes_nom_presentes:
            st.error("Les colonnes pour le nom et le prénom ne sont pas correctement configurées dans le mapping.")
            return ""

        # Si une note commune est fournie, l'utiliser comme nom du carnet d'adresses
        if note_commune:
            vcf_buffer.write(f"X-ADDRESSBOOK-NAME:{note_commune}\n\n")

        for contact in lecteur:
            # Fonction helper pour gérer les valeurs None
            def get_safe_value(key: Optional[str]) -> str:
                if not key:
                    return ""
                value = contact.get(key, "")
                return str(value).strip() if value is not None else ""

            # Récupérer les informations de manière sécurisée
            role = get_safe_value(role_colonne)
            telephone = get_safe_value(tel_colonne)
            email = get_safe_value(email_colonne)
            adresse = get_safe_value(adresse_colonne)
            agent = get_safe_value(agent_colonne)
            mots_cle = get_safe_value(mots_cle_colonne)
            relation = get_safe_value(relation_colonne)

            # Deux cas possibles : soit on a une colonne combinée nom/prénom, soit deux colonnes séparées
            if prenom_nom_colonne and prenom_nom_colonne in colonnes_disponibles:
                prenom_nom = get_safe_value(prenom_nom_colonne)
                # Ne créer une carte que si au moins le nom ou le prénom est présent
                if not prenom_nom:
                    continue
                # Utiliser la fonction de séparation prénom/nom
                prenom, nom = separer_prenom_nom(prenom_nom)
            else:
                # Utiliser les colonnes séparées pour le nom et le prénom
                prenom = get_safe_value(prenom_colonne)
                nom = get_safe_value(nom_famille_colonne)
                # Ne créer une carte que si au moins le nom ou le prénom est présent
                if not prenom and not nom:
                    continue
                # Formater le nom et le prénom
                # Pour le prénom, on utilise la fonction de formatage standard
                if prenom:
                    prenom = formater_nom(prenom)
                # Pour le nom de famille, on conserve les majuscules si c'est le cas dans le CSV
                if nom:
                    nom = formater_nom(nom, conserver_majuscules=True)

            vcf_buffer.write("BEGIN:VCARD\n")
            vcf_buffer.write("VERSION:3.0\n")

            # Ajouter le nom et le prénom
            # Format VCF: N:Nom_de_famille;Prénom;Nom_additionnel;Préfix;Suffix
            vcf_buffer.write(f"N:{nom};{prenom};;;\n")
            # Format VCF: FN:Affichage_complet_du_nom
            vcf_buffer.write(f"FN:{prenom} {nom}\n")

            # Ajouter le rôle si présent
            if role:
                vcf_buffer.write(f"TITLE:{role}\n")

            # Ajouter l'agent si présent
            if agent:
                vcf_buffer.write(f"RELATED;type=agent:{agent}\n")

            # Ajouter la relation si présente
            if relation:
                vcf_buffer.write(f"RELATED;type=relation:{relation}\n")

            # Ajouter les mots clé si présents
            if mots_cle:
                vcf_buffer.write(f"CATEGORIES:{mots_cle}\n")

            # Ajouter le téléphone
            if telephone:
                # Ajouter indicatif par défaut (+33) si aucun n'est présent
                if not telephone.startswith('+'):
                    if telephone.startswith('0'):
                        telephone = f"+33{telephone[1:]}"
                    else:
                        telephone = f"+33{telephone}"
                # Nettoyer le numéro de téléphone en enlevant les espaces et les points
                telephone = telephone.replace(' ', '').replace('.', '')
                vcf_buffer.write(f"TEL;TYPE=CELL:{telephone}\n")

            # Ajouter l'email
            if email:
                vcf_buffer.write(f"EMAIL;TYPE=INTERNET:{email}\n")

            # Ajouter l'adresse
            if adresse:
                vcf_buffer.write(f"ADR;TYPE=HOME:;;{adresse};;;;\n")

            # Ajouter la note commune si elle existe
            if note_commune:
                vcf_buffer.write(f"NOTE:{note_commune}\n")

            vcf_buffer.write("END:VCARD\n\n")

        # Récupérer le contenu du buffer
        vcf_content = vcf_buffer.getvalue()
        return vcf_content

    except Exception as e:
        st.error(f"Une erreur s'est produite : {str(e)}")
        return ""

def get_colonnes_suggérées() -> Dict[str, List[str]]:
    """
    Renvoie un dictionnaire des noms de colonnes suggérés pour chaque type de champ.

    Returns:
        Dictionnaire avec les types de champs et les noms de colonnes suggérés
    """
    return {
        'nom': ["Prénom Nom", "Nom Prénom", "Nom", "Nom complet", "Fullname", "Nom et prénom", "Contact", "Identité"],
        'prenom': ["Prénom", "Prenom", "First name", "First", "Firstname"],
        'nom_famille': ["NOM", "Nom de famille", "Last name", "Last", "Lastname", "Surname"],
        'role': ["Role", "Rôle", "Fonction", "Titre", "Poste", "Title", "Job", "Position"],
        'telephone': ["Téléphone", "Tel", "Tél", "Mobile", "Portable", "Phone", "Cellulaire", "GSM", "Numéro", "Cell"],
        'email': ["Mail", "Email", "Courriel", "E-mail", "Adresse mail", "Adresse email", "Email address"],
        'adresse': ["Adresse", "Adresse postale", "Address", "Localisation", "Domicile", "Lieu", "Location"],
        'agent': ["Agent", "Agence", "Agency", "Représentant", "Representative", "Manager", "Responsable"],
        'mots_cle': ["Mots clé", "Mots-clés", "Keywords", "Tags", "Catégories", "Thèmes"],
        'relation': ["Relation", "Lien", "Connexion", "Relationship", "Link", "Contact Type"]
    }


def get_configuration_par_défaut() -> Dict[str, str]:
    """
    Renvoie la configuration par défaut standard pour les champs.
    Ces valeurs sont celles utilisées dans les versions initiales de l'application.

    Returns:
        Dictionnaire avec les types de champs et les noms de colonnes par défaut
    """
    return {
        'nom': "Prénom Nom",
        'prenom': "Prénom",
        'nom_famille': "NOM",
        'role': "Rôle",
        'telephone': "Téléphone",
        'email': "Email",
        'adresse': "Adresse",
        'agent': "Agent",
        'mots_cle': "Mots clé",
        'relation': "Relation"
    }


def afficher_documentation_champs() -> None:
    """
    Affiche une documentation détaillée des champs utilisés dans le format VCF.
    """
    with st.expander("Documentation des champs"):
        st.markdown("""
        ## Champs utilisés dans le format VCF

        ### Nom et prénom (obligatoire)
        Vous pouvez utiliser soit :
        - Une colonne combinée avec le nom complet de la personne. L'application sépare automatiquement
          le prénom et le nom. Par exemple : "Michel DUPONT" sera séparé en prénom "Michel" et nom "Dupont".
        - Deux colonnes séparées "Prénom" et "NOM" pour une meilleure précision.

        ### Rôle/Fonction (optionnel)
        Le titre ou la fonction professionnelle de la personne. Exemple : "Directeur commercial", "Médecin", etc.

        ### Téléphone (optionnel)
        Le numéro de téléphone, de préférence mobile. L'application ajoute automatiquement l'indicatif français (+33)
        si nécessaire et formate correctement le numéro.

        ### Email (optionnel)
        L'adresse email de contact.

        ### Adresse (optionnel)
        L'adresse postale complète.

        ### Agent/Agence (optionnel)
        Le nom de l'agent ou de l'agence associée au contact.

        ### Mots clé (optionnel)
        Tags ou catégories pour classer le contact. Plusieurs mots clés peuvent être séparés par des virgules.

        ### Relation (optionnel)
        Type de relation avec le contact (ami, collègue, famille, etc.)

        ## Note commune
        Vous pouvez également ajouter une note commune qui sera ajoutée à tous les contacts.
        """)


def suggerer_colonnes(colonnes_disponibles: List[str]) -> Dict[str, str]:
    """
    Suggère automatiquement les mappings de colonnes en fonction des colonnes disponibles.

    Args:
        colonnes_disponibles: Liste des noms de colonnes disponibles dans le CSV

    Returns:
        Dictionnaire avec les types de champs et les noms de colonnes suggérés
    """
    suggestions = {}
    colonnes_suggérées = get_colonnes_suggérées()

    # Pour chaque type de champ, chercher la meilleure correspondance
    for type_champ, noms_possibles in colonnes_suggérées.items():
        colonne_correspondante = trouver_colonne_correspondante(colonnes_disponibles, noms_possibles)
        if colonne_correspondante:
            suggestions[type_champ] = colonne_correspondante

    return suggestions


def main() -> None:
    """Fonction principale de l'application Streamlit."""

    # Initialiser la session state pour les mappings de colonnes
    if 'mappings_colonnes' not in st.session_state:
        st.session_state.mappings_colonnes = {}
    if 'colonnes_disponibles' not in st.session_state:
        st.session_state.colonnes_disponibles = []
    if 'fichier_actuel' not in st.session_state:
        st.session_state.fichier_actuel = ""
    if 'configurations_stockees' not in st.session_state:
        st.session_state.configurations_stockees = {}
    if 'config_sauvegardee' not in st.session_state:
        st.session_state.config_sauvegardee = False

    # Fonction pour vérifier le décalage horaire
    def verifier_decalage_horaire() -> None:
        """Vérifie si l'heure affichée est décalée de plus de 2 minutes par rapport à l'heure actuelle."""
        # Obtenir l'heure actuelle en UTC
        heure_actuelle_utc = datetime.datetime.now(pytz.UTC)

        # Obtenir l'heure de Paris (fuseau local)
        fuseau_paris = pytz.timezone('Europe/Paris')
        heure_paris = heure_actuelle_utc.astimezone(fuseau_paris)

        # Formater pour affichage
        heure_affichage = heure_paris.strftime(TIME_FORMAT)

        # Stocker l'heure dans la session pour vérification ultérieure
        if 'heure_derniere_verification' not in st.session_state:
            st.session_state.heure_derniere_verification = heure_actuelle_utc

        # Calculer le décalage
        decalage = (heure_actuelle_utc - st.session_state.heure_derniere_verification).total_seconds()

        # Afficher l'information de version et d'heure
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Version {APP_VERSION}** - Créée le {DATE_CREATION}")
            st.markdown(f"Heure du serveur: **{heure_affichage}**")

        # Vérifier si le décalage est important (plus de 2 minutes = 120 secondes)
        if abs(decalage) > 120:
            with col2:
                st.warning(f"⚠️ Décalage détecté: {int(abs(decalage)//60)} min {int(abs(decalage)%60)} sec")

        # Mettre à jour l'heure de référence
        st.session_state.heure_derniere_verification = heure_actuelle_utc

    # Vérifier le décalage horaire
    verifier_decalage_horaire()

    # Titre et introduction
    st.title("Convertisseur CSV vers VCF - v2.0.1")
    st.markdown("""
    Application développée par Michel Safars pour Romain, futur grand réalisateur de cinéma.

    Cette application convertit votre fichier CSV en carnet d'adresses au format VCF (vCard), compatible avec tous les appareils et applications de contacts.
    """)

    # Expliquer le fonctionnement
    st.markdown("""
    ### ℹ️ Mode d'emploi

    **Voici comment utiliser cette application :**

    1ère étape ➡️ **Importez votre fichier CSV** contenant les contacts

    2ème étape ➡️ **Configurez les correspondances de colonnes**
       - Option rapide : Utilisez le bouton "Configuration par défaut"
       - Option personnalisée : Associez manuellement vos colonnes

    3ème étape ➡️ **Convertissez et téléchargez** le fichier VCF généré
    """)


    # Séparateur
    st.markdown("---")

    # Upload de fichier CSV
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=['csv'])

    # Upload de fichier de configuration (optionnel)
    with col2:
        uploaded_config = st.file_uploader("Importer configuration", type=['json'])
        if uploaded_config is not None:
            # Lecture de la configuration
            contenu_config = uploaded_config.getvalue().decode('utf-8')
            config = analyser_json_config(contenu_config)
            if "mappings" in config:
                st.session_state.mappings_colonnes = config["mappings"]
                st.success("Configuration importée avec succès !")

    if uploaded_file is not None:
        # Lecture du contenu du fichier
        contenu_csv = uploaded_file.getvalue().decode('utf-8-sig')

        # Si le fichier a changé, réinitialiser les mappings sauf si une config a été importée
        if st.session_state.fichier_actuel != uploaded_file.name and not uploaded_config:
            st.session_state.fichier_actuel = uploaded_file.name
            # Réinitialiser le flag de sauvegarde de configuration
            st.session_state.config_sauvegardee = False

            # Vérifier si on a une configuration stockée pour ce fichier
            if uploaded_file.name in st.session_state.configurations_stockees:
                st.session_state.mappings_colonnes = st.session_state.configurations_stockees[uploaded_file.name]

        # Détection du délimiteur
        délimiteur = st.selectbox(
            "Sélectionnez le délimiteur utilisé dans votre fichier",
            options=[';', ',', '\t'],
            index=0,
            format_func=lambda x: "Point-virgule (;)" if x == ';' else "Virgule (,)" if x == ',' else "Tabulation (\\t)"
        )

        # Visualisation du CSV
        try:
            csv_buffer = io.StringIO(contenu_csv)
            lecteur = csv.DictReader(csv_buffer, delimiter=délimiteur)
            colonnes = lecteur.fieldnames

            if colonnes:
                st.session_state.colonnes_disponibles = colonnes
                st.success(f"Colonnes détectées : {', '.join(colonnes)}")

                # Prévisualisation du CSV
                try:
                    csv_buffer.seek(0)  # Remettre le curseur au début
                    df_preview = []
                    for i, row in enumerate(csv.DictReader(csv_buffer, delimiter=délimiteur)):
                        if i < 5:  # Limiter à 5 lignes pour la prévisualisation
                            df_preview.append(row)
                        else:
                            break
                except Exception as e:
                    st.error(f"Erreur lors de la prévisualisation : {str(e)}")
                    df_preview = []

                if df_preview:
                    st.subheader("Aperçu des données (5 premières lignes)")
                    st.table(df_preview)

                # Configuration des mappings de colonnes
                st.subheader("Configuration des champs")

                # Si aucun mapping existant, suggérer automatiquement
                if not st.session_state.mappings_colonnes:
                    st.session_state.mappings_colonnes = suggerer_colonnes(colonnes)

                # Afficher la documentation des champs
                afficher_documentation_champs()

                # Créer une liste avec tous les champs et leur description
                champs_descriptions = {
                    'nom': "Nom et prénom (combiné)",
                    'prenom': "Prénom",
                    'nom_famille': "Nom de famille",
                    'role': "Rôle/Fonction",
                    'telephone': "Numéro de téléphone",
                    'email': "Adresse email",
                    'adresse': "Adresse postale",
                    'agent': "Agent/Agence",
                    'mots_cle': "Mots clé",
                    'relation': "Relation"
                }

                # Afficher les configurations possibles
                st.markdown("### Configuration des correspondances de colonnes")

                # Obtenir la configuration par défaut
                config_par_défaut = get_configuration_par_défaut()

                # Vérifier quels champs par défaut existent dans le CSV actuel
                mappings_valides = {}
                champs_manquants = []
                for champ, valeur in config_par_défaut.items():
                    if valeur in colonnes:
                        mappings_valides[champ] = valeur
                    else:
                        champs_manquants.append(valeur)

                # Afficher la configuration par défaut disponible
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("#### Option 1 : Configuration par défaut")
                    if 'nom' in mappings_valides or ('prenom' in mappings_valides and 'nom_famille' in mappings_valides):  # Vérifier que les champs obligatoires sont présents
                        # Afficher les mappings disponibles avec fond vert
                        st.markdown("<div style='background-color: #e6ffe6; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
                        st.markdown("**Mappings disponibles avec ce fichier :**")
                        for champ, desc in champs_descriptions.items():
                            if champ in mappings_valides:
                                st.markdown(f"✅ **{desc}** ➡️ *{mappings_valides[champ]}*")
                            else:
                                st.markdown(f"❌ **{desc}** ➡️ *Non trouvé*")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        # Afficher un avertissement si les champs requis ne sont pas disponibles
                        st.warning(f"⚠️ La configuration par défaut n'est pas compatible avec ce fichier.")
                        st.markdown(f"**Colonnes attendues :** {', '.join(config_par_défaut.values())}")
                        st.markdown(f"**Colonnes manquantes :** {', '.join(champs_manquants)}")

                # Bouton pour appliquer la configuration par défaut
                with col2:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    condition_bouton = 'nom' in mappings_valides or ('prenom' in mappings_valides and 'nom_famille' in mappings_valides)
                    if condition_bouton and st.button("Appliquer configuration par défaut"):
                        st.session_state.mappings_colonnes = mappings_valides
                        st.session_state.configurations_stockees[uploaded_file.name] = mappings_valides
                        st.session_state.config_sauvegardee = True
                        st.success("✅ Configuration par défaut appliquée avec succès !")

                # Option de configuration manuelle
                st.markdown("#### Option 2 : Configuration manuelle")
                st.markdown("**Associez chaque type de champ à la colonne correspondante dans votre fichier CSV :**")

                # La case à cocher pour le débogage a été déplacée au niveau de la conversion

                # Créer un formulaire pour les mappings
                with st.form("form_mappings"):
                    nouveaux_mappings = {}

                    # Ajouter une option vide et "Ne pas utiliser" pour les champs optionnels
                    colonnes_avec_vide = ['', 'Ne pas utiliser'] + colonnes

                    # Pour chaque type de champ, créer un sélecteur
                    for champ, description in champs_descriptions.items():
                        # Déterminer l'index par défaut
                        default_index = 0
                        if champ in st.session_state.mappings_colonnes:
                            colonne_actuelle = st.session_state.mappings_colonnes[champ]
                            if colonne_actuelle in colonnes_avec_vide:
                                default_index = colonnes_avec_vide.index(colonne_actuelle)

                        # Créer le sélecteur
                        colonne_selectionnee = st.selectbox(
                            f"{description}:",
                            options=colonnes_avec_vide,
                            index=default_index,
                            key=f"select_{champ}"
                        )

                        # Stocker la sélection
                        if colonne_selectionnee and colonne_selectionnee != 'Ne pas utiliser':
                            nouveaux_mappings[champ] = colonne_selectionnee

                    # Bouton pour valider l'option 2
                    submit_button = st.form_submit_button("Valider l'option 2")

                    if submit_button:
                        # Vérifier qu'au moins une des options d'identification est configurée
                        # Soit le champ combiné 'nom', soit les deux champs séparés 'prenom' et 'nom_famille'
                        a_nom_combine = 'nom' in nouveaux_mappings and nouveaux_mappings['nom']
                        a_champs_separes = ('prenom' in nouveaux_mappings and nouveaux_mappings['prenom'] and
                                           'nom_famille' in nouveaux_mappings and nouveaux_mappings['nom_famille'])

                        if not a_nom_combine and not a_champs_separes:
                            st.error("Vous devez configurer soit le champ 'Nom et prénom' combiné, soit les champs 'Prénom' et 'Nom de famille' séparés.")
                        else:
                            st.session_state.mappings_colonnes = nouveaux_mappings
                            # Stocker les mappings dans la session
                            st.session_state.configurations_stockees[uploaded_file.name] = nouveaux_mappings
                            st.session_state.config_sauvegardee = True
                            st.success("Configuration enregistrée avec succès !")

                # Proposer de télécharger la configuration actuelle si elle a été enregistrée
                if st.session_state.config_sauvegardee and st.session_state.mappings_colonnes:
                    st.markdown("***")
                    st.subheader("Exporter la configuration")
                    st.markdown("Vous pouvez télécharger cette configuration pour la réutiliser ultérieurement :")
                    lien_telechargement = generer_lien_telechargement_json(uploaded_file.name, st.session_state.mappings_colonnes)
                    st.markdown(lien_telechargement, unsafe_allow_html=True)
                    st.info("**Astuce :** Enregistrez cette configuration pour réutiliser les mêmes mappings avec des fichiers similaires à l'avenir.")
            else:
                st.warning("Aucune colonne détectée dans le fichier CSV.")

        except Exception as e:
            st.error(f"Erreur lors de la lecture du CSV : {str(e)}")

        # Note commune
        note_commune = st.text_input(
            "Note commune (optionnelle)",
            help="Cette note sera ajoutée à tous les contacts"
        )

        # Case à cocher pour le débogage - placée au niveau de la conversion pour être accessible
        debug_mode = st.checkbox("Afficher le contenu brut du fichier VCF (mode débogage)", value=False)
        
        # Bouton de conversion
        if st.button("Convertir en VCF"):
            # Vérifier que les mappings sont configurés
            # Vérification adaptée pour prendre en compte les colonnes séparées
            a_nom_combine = 'nom' in st.session_state.mappings_colonnes
            a_colonnes_separees = ('prenom' in st.session_state.mappings_colonnes or 'nom_famille' in st.session_state.mappings_colonnes)
            
            if not st.session_state.mappings_colonnes or (not a_nom_combine and not a_colonnes_separees):
                st.error("Veuillez configurer correctement les champs avant de convertir.")
            else:
                with st.spinner("Conversion en cours..."):
                    # Convertir le fichier avec les mappings configurés
                    vcf_content = convertir_csv_en_vcf(contenu_csv, st.session_state.mappings_colonnes, note_commune, délimiteur)

                if vcf_content:
                    # Créer un nom de fichier de sortie
                    nom_fichier_base = os.path.splitext(uploaded_file.name)[0]
                    nom_fichier_vcf = f"{nom_fichier_base}.vcf"

                    # Créer un bouton de téléchargement
                    download_link = f"[Télécharger le fichier VCF]({nom_fichier_vcf})"
                    st.download_button(
                        label="Télécharger le fichier VCF",
                        data=vcf_content,
                        file_name=nom_fichier_vcf,
                        mime="text/vcard"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)

                    # Afficher le contenu brut du fichier VCF si le mode débogage est activé
                    if debug_mode:
                        st.subheader("Contenu brut du fichier VCF (débogage)")
                        st.text(vcf_content)

                    # Instructions pour l'importation
                    with st.expander("Instructions pour importer le fichier dans l'application Contacts"):
                        st.info("""
                        **Pour importer dans Contacts sur macOS :**
                        1. Téléchargez le fichier VCF
                        2. Ouvrez l'application Contacts
                        3. Dans le menu Fichier, sélectionnez Importer
                        """)
                else:
                    st.error("La conversion a échoué. Veuillez vérifier votre fichier CSV.")


if __name__ == "__main__":
    main()
