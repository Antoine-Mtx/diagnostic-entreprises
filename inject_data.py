import pandas as pd
import json

file_path = 'J0_Grille_Antoine.xlsx'
sheet_name = 'Axe Compétences'

df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=3)

# Exclure les colonnes 5 et 10
df = df.drop(columns=[df.columns[4], df.columns[9]])

# Gérer les cellules fusionnées dans la première colonne
df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')

# Gérer les cellules fusionnées dans la troisième colonne
df.iloc[:, 2] = df.iloc[:, 2].fillna(method='ffill')

# Gérer les cellules fusionnées dans la onzième colonne
df.iloc[:, 8] = df.iloc[:, 8].fillna(method='ffill')

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
            'Commentaires': row['Commentaires/Justification (exemples concrets)'],
        }
        questions.append(question_dict)

    category_dict['Questions'] = questions
    category_dict['Score'] = group['Score'].iloc[0]
    category_dict['Démarche pour progresser'] = group['Démarche pour progresser'].iloc[0]
    output.append(category_dict)

# Convertir la liste des dictionnaires en JSON
json_data = json.dumps(output, ensure_ascii=False, indent=4)

with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)
