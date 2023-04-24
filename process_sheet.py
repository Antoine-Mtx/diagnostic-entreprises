import pandas as pd
import json

def concat_cells(group, col_index):
    result = ''
    for _, row in group.iterrows():
        cell_value = row.iloc[col_index]
        if pd.notnull(cell_value):
            result += ' ' + str(cell_value)
    return result.strip()


file_path = 'J0_Grille_Acces_Editions.xlsx'
sheet_name = 'Axe Réactivité'

df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=3)

# Exclure les colonnes avec un en-tête vide
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Gérer les cellules fusionnées dans la première colonne
df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')

# Gérer les cellules fusionnées dans la troisième colonne
df.iloc[:, 2] = df.iloc[:, 2].fillna(method='ffill')

# Gérer les cellules fusionnées dans la dernière colonne
progress_step_col_index = 8 if len(df.columns) > 7 else 7
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
    category_dict['Démarche pour progresser'] = concat_cells(group, progress_step_col_index)
    output.append(category_dict)

# Convertir la liste des dictionnaires en JSON
json_data = json.dumps(output, ensure_ascii=False, indent=4)

with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)