import pandas as pd
import json

def concat_cells(group, col_index):
    # Récupérer toutes les cellules non vides
    non_empty_cells = group[group.columns[col_index]].dropna()

    # Supprimer les doublons tout en conservant l'ordre
    deduplicated_cells = []
    for cell in non_empty_cells:
        if cell not in deduplicated_cells:
            deduplicated_cells.append(cell)

    # Fusionner les cellules en une seule chaîne avec des retours à la ligne
    return '\n'.join(deduplicated_cells)


file_path = 'J0_Grille_Acces_Editions.xlsx'
sheet_name = 'Axe Compétences'

df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=3)

# Exclure les colonnes avec un en-tête vide
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Gérer les cellules fusionnées dans la première colonne
df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')

# Gérer les cellules fusionnées dans la troisième colonne
df.iloc[:, 2] = df.iloc[:, 2].fillna(method='ffill')

# Gérer les cellules fusionnées dans la dernière colonne
if "Démarche pour progresser" in df.columns:
    progress_step_col_index = df.columns.get_loc("Démarche pour progresser")
elif "Vos idées pour progresser" in df.columns:
    progress_step_col_index = df.columns.get_loc("Vos idées pour progresser")
else:
    raise ValueError("La colonne 'Démarche pour progresser' ou 'Vos idées pour progresser' est introuvable.")

col1 = df.columns[progress_step_col_index]
if col1 in df.columns:
    df[col1] = df[col1].fillna(method='ffill')

# Renommer la colonne "Items" en "Catégorie"
df = df.rename(columns={'Items': 'Catégorie'})

# Grouper les lignes du DataFrame par catégorie
grouped = df.groupby('Catégorie')

# Créer un dictionnaire pour chaque catégorie avec les questions et leurs informations correspondantes
output = []

for name, group in grouped:
    category_dict = {'Catégorie': name}
    questions = []

    for index, row in group.iterrows():
        if pd.isnull(row['Questionnements']):
            continue
        question_dict = {
            'Question': row['Questionnements'],
            'Réponse': int(row['Score.1']),
            '2': row['2 points'],
            '1': row['1 point'],
            '0': row['0 point'],
        }
        if 'Commentaires/Justification (exemples concrets)' in row:
            question_dict['Commentaire'] = row['Commentaires/Justification (exemples concrets)']
        questions.append(question_dict)

    category_dict['Questions'] = questions
    category_dict['Score'] = group['Score'].iloc[0]

    # Utiliser la fonction concat_cells sur le bon ensemble de lignes pour la catégorie actuelle
    category_group = group.loc[group['Catégorie'] == name]
    category_dict['Démarche pour progresser'] = concat_cells(category_group, progress_step_col_index)

    output.append(category_dict)

# Convertir la liste des dictionnaires en JSON
json_data = json.dumps(output, ensure_ascii=False, indent=4)

with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)