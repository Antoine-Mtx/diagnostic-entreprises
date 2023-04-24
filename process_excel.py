import pandas as pd
import json
import re

def process_sheet(sheet):
    df = sheet.fillna(method='ffill', axis=0)
    categories = []

    for _, group in df.groupby('Unnamed: 0'):
        category_dict = {
            'Catégorie': group['Unnamed: 0'].iloc[0],
            'Questions': [],
            'Score': group['Score'].iloc[0]
        }

        for _, row in group.iterrows():
            if not pd.isna(row['Questionnements']):
                question_dict = {
                    'Question': row['Questionnements'],
                    'Réponse': int(row['Score.1']),
                    '2': row['2 points'],
                    '1': row['1 point'],
                    '0': row['0 point'],
                    'Commentaires': row['Commentaires/Justification (exemples concrets)'],
                }
                category_dict['Questions'].append(question_dict)

        categories.append(category_dict)

    return categories

def main():
    excel_file = 'J0_Grille_Acces_Editions.xlsx'
    company_name = re.sub(r'JO_Grille_(.*).xlsx', r'\1', excel_file).replace('_', ' ')
    xls = pd.read_excel(excel_file, sheet_name=['Axe Compétences', 'Axe Réactivité', 'Axe Numérique'])

    final_output = {
        'Entreprise': company_name,
        'Axe Compétences': process_sheet(xls['Axe Compétences']),
        'Axe Réactivité': process_sheet(xls['Axe Réactivité']),
        'Axe Numérique': process_sheet(xls['Axe Numérique']),
    }

    with open('output.json', 'w') as outfile:
        json.dump(final_output, outfile, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
