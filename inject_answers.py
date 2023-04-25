import openpyxl
import mysql.connector
import os
from datetime import datetime

file_path = 'data/J0_Grille_Acces_Editions.xlsx'

# Ouvrir le fichier Excel
workbook = openpyxl.load_workbook(file_path)

# Connexion à la base de données
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="diagnostic",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
    use_unicode=True  # Cette ligne garantit que les données sont traitées en Unicode
)
cursor = connection.cursor()

# Extraire le nom de l'entreprise à partir du nom du fichier
file_name_with_extension = os.path.basename(file_path)
file_name = os.path.splitext(file_name_with_extension)[0]  # Enlever l'extension '.xlsx'
name_parts = file_name.split('_')[2:]  # Ignorer les deux premières parties ('J0' et 'Grille')
enterprise_name = ' '.join(name_parts)  # Joindre les parties restantes avec un espace

print("Nom de l'entreprise:", enterprise_name)

# Insérer l'entreprise et obtenir son ID
cursor.execute("SELECT id FROM enterprise WHERE name = %s", (enterprise_name,))
enterprise_result = cursor.fetchone()
if enterprise_result:
    enterprise_id = enterprise_result[0]
else:
    cursor.execute("INSERT INTO enterprise (name) VALUES (%s)", (enterprise_name,))
    connection.commit()
    enterprise_id = cursor.lastrowid

print("ID de l'entreprise:", enterprise_id)

# Insérer l'évaluation et obtenir son ID
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("Date de l'évaluation:", now)
cursor.execute("SELECT id FROM evaluation WHERE enterprise_id = %s", (enterprise_id,))
existing_evaluation = cursor.fetchone()

if existing_evaluation:
    print("Une évaluation existe déjà pour cette entreprise à cette date.")
    evaluation_id = existing_evaluation[0]
else:
    cursor.execute("INSERT INTO evaluation (enterprise_id, created_at) VALUES (%s, %s)", (enterprise_id, now))
    evaluation_id = cursor.lastrowid
    print("Nouvelle évaluation créée pour l'entreprise.")
    
print("ID de l'évaluation:", evaluation_id)

# Liste des noms de feuilles à traiter
sheet_names = ["Axe Compétences", "Axe Réactivité", "Axe Numérique"]

# Parcourir chaque feuille
for sheet_name in sheet_names:
    sheet = workbook[sheet_name]
    print("Feuille:", sheet_name)

    # Recherche de l'ID de l'axe correspondant
    cursor.execute("SELECT id FROM axis WHERE name = %s", (sheet_name,))
    axis_result = cursor.fetchone()
    if axis_result:
        axis_id = axis_result[0]
        print("ID de l'axe:", axis_id)
    else:
        print(f"Aucun axe trouvé pour le nom '{sheet_name}'. Vérifiez les données dans la base de données.")
        continue
    
    merged_ranges = sheet.merged_cells.ranges

    # for row in sheet.iter_rows(min_row=4, values_only=True):
    #     # Vérifier si la cellule est fusionnée
    #     is_merged = False
    #     for merged_range in merged_ranges:
    #         if row[0] in merged_range:
    #             is_merged = True
    #             merged_cells = merged_range
    #             break

    #     if is_merged:
    #         # Extraire la valeur de la plage fusionnée
    #         merged_value = sheet[merged_cells[0].coord].value
    #         print(f"La cellule {merged_cells[0].coord} est fusionnée et contient la valeur {merged_value}.")
    #     else:
    #         print(f"La cellule {row[0].coordinate} n'est pas fusionnée.")
            
#         # Gérer les cellules fusionnées pour la colonne de catégorie
#         category_name = row[0].value
#         if row[0].is_merged:
#             for cell in row[0]:
#                 if cell.row == row[0].row:
#                     continue
#                 if cell.value is not None:
#                     category_name = cell.value
#                     break
        
#         question_content = row[1]
#         answer_choice = int(row[3]) if row[3] is not None else None
#         option_2 = row[5]
#         option_1 = row[6]
#         option_0 = row[7]
        
#         if sheet_name == "Axe Numérique":
#             ideas_content = row[9]
#             answer_comment = ""
#         else:
#             answer_comment = row[8]
#             ideas_content = row[10]

#         # Recherche de l'ID de la catégorie correspondante
#         cursor.execute("SELECT id FROM category WHERE name = %s AND axis_id = %s", (category_name, axis_id))
#         category_result = cursor.fetchone()
#         if category_result:
#             category_id = category_result[0]
#         else:
#             print(f"La catégorie '{category_name}' n'existe pas pour l'axe '{sheet_name}'. Veuillez vérifier les données dans la base de données.")
#             continue

#         # Recherche de l'ID de la question correspondante
#         cursor.execute("SELECT id FROM question WHERE content = %s AND category_id = %s", (question_content, category_id))
#         question_result = cursor.fetchone()
#         if question_result:
#             question_id = question_result[0]
#         else:
#             # Insertion de la nouvelle question et récupération de l'ID
#             cursor.execute("INSERT INTO question (content, category_id, option_2, option_1, option_0) VALUES (%s, %s, %s, %s, %s)",
#                            (question_content, category_id, option_2, option_1, option_0))
#             connection.commit()
#             question_id = cursor.lastrowid

#         # Insérer les données dans la table evaluation_question
#         cursor.execute("INSERT INTO evaluation_question (evaluation_id, question_id, choice, comment) VALUES (%s, %s, %s, %s)",
#                        (evaluation_id, question_id, answer_choice, answer_comment))

#         # Insérer les données dans la table evaluation_category
#         if ideas_content:
#             cursor.execute("INSERT INTO evaluation_category (evaluation_id, category_id, comment) VALUES (%s, %s, %s)",
#                            (evaluation_id, category_id, ideas_content))

# Valider les changements et fermer la connexion à la base de données
connection.commit()
connection.close()

print("Terminé.")
