import pandas as pd
import json

def concat_cells(group, col_index):
    non_empty_cells = group[group.columns[col_index]].dropna()
    deduplicated_cells = []
    for cell in non_empty_cells:
        if cell not in deduplicated_cells:
            deduplicated_cells.append(cell)
    return '\n'.join(deduplicated_cells)

def process_sheet(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', header=3)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')
    df.iloc[:, 2] = df.iloc[:, 2].fillna(method='ffill')
    progress_step_col_index = df.columns.get_loc("Démarche pour progresser") if "Démarche pour progresser" in df.columns else df.columns.get_loc("Vos idées pour progresser")
    df.iloc[:, progress_step_col_index] = df.iloc[:, progress_step_col_index].fillna(method='ffill')
    df = df.rename(columns={'Items': 'Catégorie'})
    grouped = df.groupby('Catégorie')
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
        category_group = group.loc[group['Catégorie'] == name]
        category_dict['Démarche pour progresser'] = concat_cells(category_group, progress_step_col_index)
        output.append(category_dict)

    return output

file_path = 'J0_Grille_Acces_Editions.xlsx'
sheets = ['Axe Compétences', 'Axe Réactivité', 'Axe Numérique']
data = {}

# Extraire le nom de l'entreprise à partir du nom du fichier
file_name = file_path.split('.')[0]  # Enlever l'extension '.xlsx'
name_parts = file_name.split('_')[2:]  # Ignorer les deux premières parties ('J0' et 'Grille')
entreprise_name = ' '.join(name_parts)  # Joindre les parties restantes avec un espace

data['Entreprise'] = entreprise_name


for sheet_name in sheets:
    data[sheet_name] = process_sheet(file_path, sheet_name)

json_data = json.dumps(data, ensure_ascii=False, indent=4)

with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)
