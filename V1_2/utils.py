# utils.py MS

import csv
from typing import Dict, List, Optional


def formater_nom(nom: str) -> str:
	"""
	Formate un nom pour avoir les premières lettres de chaque mot en majuscules.
	Exemple: "DUPONT" -> "Dupont", "DE LA TOUR" -> "De La Tour"
	"""
	if not nom:
		return ""

	# Séparer les mots et les formater individuellement
	mots = nom.lower().split()
	mots_formates = [mot.capitalize() for mot in mots]

	return " ".join(mots_formates)


def separer_prenom_nom(chaine: str) -> tuple[str, str]:
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


def convertir_csv_en_vcf(fichier_csv: str, fichier_vcf: str, note_commune: Optional[str] = None) -> None:
	"""
	Convertit un fichier CSV en fichier VCF.

	:param fichier_csv: Chemin du fichier CSV source
	:param fichier_vcf: Chemin du fichier VCF destination
	:param note_commune: Note à ajouter à toutes les fiches (optionnel)
	"""
	try:
		with open(fichier_csv, 'r', encoding='utf-8-sig') as fichier:
			lecteur = csv.DictReader(fichier, delimiter=';')

			# Vérifiez si des colonnes sont détectées
			colonnes_disponibles = lecteur.fieldnames
			if not colonnes_disponibles:
				print("Erreur : Aucune colonne détectée dans le fichier CSV.")
				return

			print(f"Colonnes détectées : {colonnes_disponibles}")

			# Définir les noms possibles pour chaque type de colonne
			noms_role = ["Role", "Rôle", "Fonction"]
			noms_nom = ["Prénom Nom", "Nom Prénom", "Nom"]
			noms_tel = ["Téléphone", "Tel", "Tél", "Mobile"]
			noms_email = ["Mail", "Email", "Courriel"]
			noms_adresse = ["Adresse", "Adresse postale"]
			noms_agent = ["Agent", "Agence"]  # Noms possibles pour la colonne agent

			# Trouver les colonnes correspondantes
			role_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_role)
			prenom_nom_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_nom)
			tel_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_tel)
			email_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_email)
			adresse_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_adresse)
			agent_colonne = trouver_colonne_correspondante(colonnes_disponibles, noms_agent)

			# Vérifier que les colonnes essentielles sont présentes
			if not prenom_nom_colonne:
				print("Erreur : Impossible de trouver la colonne nom/prénom dans le CSV.")
				return

			# Écriture dans le fichier VCF
			with open(fichier_vcf, 'w', encoding='utf-8') as fichier_vcf:
				# Si une note commune est fournie, l'utiliser comme nom du carnet d'adresses
				if note_commune:
					fichier_vcf.write(f"X-ADDRESSBOOK-NAME:{note_commune}\n\n")

				for contact in lecteur:
					# Fonction helper pour gérer les valeurs None
					def get_safe_value(key: Optional[str]) -> str:
						if not key:
							return ""
						value = contact.get(key, "")
						return str(value).strip() if value is not None else ""

					# Récupérer les informations de manière sécurisée
					role = get_safe_value(role_colonne)
					prenom_nom = get_safe_value(prenom_nom_colonne)
					telephone = get_safe_value(tel_colonne)
					email = get_safe_value(email_colonne)
					adresse = get_safe_value(adresse_colonne)
					agent = get_safe_value(agent_colonne)

					# Ne créer une carte que si au moins le nom ou le prénom est présent
					if not prenom_nom:
						continue

					fichier_vcf.write("BEGIN:VCARD\n")
					fichier_vcf.write("VERSION:3.0\n")

					# Utiliser la nouvelle fonction de séparation prénom/nom
					prenom, nom = separer_prenom_nom(prenom_nom)

					# Ajouter le nom et le prénom :
					#  - N : nom complet sous forme "Nom;Prénom;Mme/Mr/etc;Titre;Suffixe"
					#  - FN : nom complet sous forme "Prénom Nom"
					# Les autres champs ne sont pas pertinents pour nos besoins
					fichier_vcf.write(f"N:{nom};{prenom};;;\n")
					fichier_vcf.write(f"FN:{prenom} {nom}\n")

					# Ajouter le rôle si présent
					if role:
						fichier_vcf.write(f"TITLE:{role}\n")

					# Ajouter l'agent si présent
					if agent:
						fichier_vcf.write(f"RELATED;type=agent:{agent}\n")

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
						fichier_vcf.write(f"TEL;TYPE=CELL:{telephone}\n")

					# Ajouter l'email
					if email:
						fichier_vcf.write(f"EMAIL;TYPE=INTERNET:{email}\n")

					# Ajouter l'adresse
					if adresse:
						fichier_vcf.write(f"ADR;TYPE=HOME:;;{adresse};;;;\n")

					# Ajouter la note commune si elle existe
					if note_commune:
						fichier_vcf.write(f"NOTE:{note_commune}\n")

					fichier_vcf.write("END:VCARD\n\n")

				print(f"Conversion terminée. Le fichier VCF est disponible : {fichier_vcf.name}")

	except Exception as e:
		print(f"Une erreur s'est produite : {str(e)}")
		raise
