import openpyxl
import mysql.connector

# Ouvrir le fichier Excel
workbook = openpyxl.load_workbook("data\J0_Grille_Acces_Editions_Test.xlsx")

# Liste des noms de feuilles à traiter
sheet_names = ["Axe Compétences", "Axe Réactivité", "Axe Numérique"]

# Connexion à la base de données
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="diagnostic",
    charset="utf8mb4",  # Ajoutez cette ligne pour définir explicitement l'encodage
    use_unicode=True  # Cette ligne garantit que les données sont traitées en Unicode
)
cursor = connection.cursor()

# Parcourir chaque feuille
for sheet_name in sheet_names:
    sheet = workbook[sheet_name]
    
    # Ignorer les 3 premières lignes et obtenir les données restantes
    rows_data = list(sheet.iter_rows(min_row=4, values_only=True))

    for row in rows_data:
        if row[0] == "Items":
          continue
        if len(row) >= 6:
            category_name = row[0]
            question_content = row[1]
            answer_choice = int(row[3])
            option_2 = row[5]
            option_1 = row[6]
            option_0 = row[7]
            
            if sheet_name == "Axe Numérique":
                ideas_content = row[9]
                answer_comment = ""
            else:
                answer_comment = row[8]
                ideas_content = row[10]

            # Recherche de l'ID de l'axe correspondant
            cursor.execute("SELECT id FROM axis WHERE name = %s", (sheet_name,))
            axis_result = cursor.fetchone()
            if axis_result:
                axis_id = axis_result[0]
            else:
                print(f"Aucun axe trouvé pour le nom '{sheet_name}'. Vérifiez les données dans la base de données.")
                continue


            # Recherche de l'ID de la catégorie correspondante
            cursor.execute("SELECT id FROM category WHERE name = %s AND axis_id = %s", (category_name, axis_id))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
            else:
                # Insertion de la nouvelle catégorie et récupération de l'ID
                cursor.execute("INSERT INTO category (name, axis_id) VALUES (%s, %s)", (category_name, axis_id))
                connection.commit()
                category_id = cursor.lastrowid

            # Recherche de l'ID de la question correspondante
            cursor.execute("SELECT id FROM question WHERE content = %s AND category_id = %s", (question_content, category_id))
            question_result = cursor.fetchone()
            if question_result:
                question_id = question_result[0]
            else:
                # Insertion de la nouvelle question et récupération de l'ID
                cursor.execute("INSERT INTO question (content, category_id, option_2, option_1, option_0) VALUES (%s, %s, %s, %s, %s)",
                               (question_content, category_id, option_2, option_1, option_0))
                connection.commit()
                question_id = cursor.lastrowid

            # Code pour insérer les données answer et ideas dans la base de données

        else:
            print(f"Ligne incomplète ou incorrecte: {row}")

# Fermer la connexion à la base de données
cursor.close()
connection.close()
