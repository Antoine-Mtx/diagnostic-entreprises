import json
import mysql.connector

# Charger le fichier JSON
with open("output.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Connecter à la base de données MySQL
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="diagnostic",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
    use_unicode=True
)

cursor = connection.cursor()

# Parcourir les axes et insérer les données
for axis_name, axis_data in data.items():
    if axis_name != "Entreprise":
        cursor.execute("INSERT INTO axis (name) VALUES (%s)", (axis_name,))
        axis_id = cursor.lastrowid

        for category_data in axis_data:
            category_name = category_data["Categorie"]
            cursor.execute("INSERT INTO category (name, axis_id) VALUES (%s, %s)", (category_name, axis_id))
            category_id = cursor.lastrowid

            for question_data in category_data["Questions"]:
                question_content = question_data["Question"]
                option_0 = question_data["0"]
                option_1 = question_data["1"]
                option_2 = question_data["2"]

                cursor.execute("""
                    INSERT INTO question (content, option_0, option_1, option_2, category_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (question_content, option_0, option_1, option_2, category_id))

# Valider les changements et fermer la connexion
connection.commit()
cursor.close()
connection.close()
