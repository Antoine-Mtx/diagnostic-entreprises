import json
import mysql.connector
from datetime import datetime

# Charger le fichier JSON
with open("output/Bastien Seegmuller.json", "r", encoding="utf-8") as file:
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

try:
    # Insérer l'entreprise et récupérer l'ID
    entreprise_name = data["Entreprise"]
    cursor.execute("INSERT INTO enterprise (name) VALUES (%s)", (entreprise_name,))
    entreprise_id = cursor.lastrowid

    # Insérer l'évaluation et récupérer l'ID
    evaluation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO evaluation (created_at, enterprise_id) VALUES (%s, %s)", (evaluation_date, entreprise_id))
    evaluation_id = cursor.lastrowid

    # Parcourir les axes et insérer les données
    for axis_name, axis_data in data.items():
        if axis_name != "Entreprise":
            cursor.execute("SELECT id FROM axis WHERE name = %s", (axis_name,))
            result = cursor.fetchone()
            if result:
                axis_id = result[0]
            else:
                print(f"Erreur : L'axe '{axis_name}' n'a pas été trouvé dans la base de données.")
                continue

            for category_data in axis_data:
                category_name = category_data["Catégorie"]
                cursor.execute("SELECT id FROM category WHERE name = %s AND axis_id = %s", (category_name, axis_id))
                result = cursor.fetchone()
                if result:
                    category_id = result[0]
                else:
                    print(f"Erreur : La catégorie '{category_name}' n'a pas été trouvée dans la base de données.")
                    continue

                # Insérer l'évaluation_category et récupérer l'ID
                category_progress = category_data["Démarche pour progresser"]
                cursor.execute("""
                    INSERT INTO evaluation_category (comment, evaluation_id, category_id)
                    VALUES (%s, %s, %s)
                """, (category_progress, evaluation_id, category_id))
                evaluation_category_id = cursor.lastrowid

                for question_data in category_data["Questions"]:
                    question_content = question_data["Question"]
                    cursor.execute("SELECT id FROM question WHERE content = %s AND category_id = %s", (question_content, category_id))
                    result = cursor.fetchone()
                    if result:
                        question_id = result[0]
                    else:
                        print(f"Erreur : La question '{question_content}' n'a pas été trouvée dans la base de données.")
                        continue

                    choice = question_data["Réponse"]
                    comment = question_data.get("Commentaire", "")
                    cursor.execute("""
                        INSERT INTO evaluation_question (choice, comment, evaluation_id, question_id)
                        VALUES (%s, %s, %s, %s)
                    """, (choice, comment, evaluation_id, question_id))
except mysql.connector.Error as e:
    print(f"Erreur lors de l'exécution du script : {e}")
    connection.rollback()
else:
    # Valider les changements et fermer la connexion
    connection.commit()
finally:
    cursor.close()
    connection.close()
