import os
import json
from process_excel import process_excel

# Dossier contenant les fichiers Excel à traiter
data_folder = 'data'

# Objet JSON qui va contenir tous les résultats des évaluations
all_evaluations = {}

# Parcourir tous les fichiers dans le dossier
for filename in os.listdir(data_folder):
    if filename.endswith('.xlsx'):
        # Extraire le nom de l'entreprise à partir du nom du fichier
        entreprise = filename.split('_')[-1][:-5]

        # Appeler la fonction process_excel pour traiter le fichier
        filepath = os.path.join(data_folder, filename)
        evaluation = process_excel(filepath)

        # Ajouter les évaluations à l'objet JSON global
        all_evaluations[entreprise] = evaluation

# Enregistrer l'objet JSON global dans un fichier
with open('evaluations.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_evaluations, json_file, ensure_ascii=False, indent=4)
