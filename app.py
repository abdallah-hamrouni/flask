from flask import Flask, jsonify, request
import json
import os
from flask_cors import CORS
from fuzzywuzzy import fuzz

app = Flask(__name__)
CORS(app)


chemin_complet_dossier = "D:/result"


def charger_inverted_index():
    file_path = os.path.join(chemin_complet_dossier, "reslt.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

Inverted_Index = charger_inverted_index()

# Fonction pour trouver les parties de mots similaires
def find_exact_match(search_part):
    exact_matches = set()
    for pdf in Inverted_Index:
        if pdf.lower() == search_part.lower():  # Vérifier l'égalité exacte
            exact_matches.add(pdf)
        elif pdf.lower().startswith(search_part.lower() + " "):  # Vérifier si le mot commence par la partie recherchée
            exact_matches.add(pdf)
        elif pdf.lower().endswith(" " + search_part.lower()): 
            exact_matches.add(pdf)
        elif " " + search_part.lower() + " " in pdf.lower():  # Vérifier si la partie recherchée est dans le mot
            exact_matches.add(pdf)
    return exact_matches


# Route pour obtenir la liste des PDF qui contiennent la partie de mot spécifiée
@app.route('/api/pdf_contenant_partie_mot', methods=['GET'])
def obtenir_pdf_contenant_partie_mot():
    search_part = request.args.get('part', '')  # Récupérer la partie de mot de la requête, par défaut ''
    
    if search_part:
        # Si la partie de mot est spécifiée, obtenir les parties de mots similaires
        similar_parts = find_exact_match(search_part)

        if similar_parts:
            pdfs_with_part = []  # Liste pour stocker les résultats sous forme de dictionnaires
            
            # Parcourir les parties de mots similaires
            for part in similar_parts:
                # Parcourir les PDF correspondants à cette partie de mot
                for pdf, count in Inverted_Index[part].items():
                    # Ajouter chaque PDF sous forme de dictionnaire à la liste
                    pdfs_with_part.append({part: {pdf: count}})
            
            return jsonify({"pdf_names": pdfs_with_part})
        else:
            return jsonify({"message": f"Aucun PDF ne contient de partie de mot similaire à '{search_part}'."})
    else:
        return jsonify({"message": "Le paramètre 'part' est obligatoire."})

if __name__ == '__main__':
    app.run(debug=True,port=5001)