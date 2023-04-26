from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from datetime import datetime
import pymysql

app = Flask(__name__)

# Configurez vos informations de connexion à la base de données ici
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'db': 'test'
}

# Page par défaut
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_diagnostic')
def new_diagnostic():
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer les axes, catégories et questions
    cursor.execute("SELECT * FROM axis")
    axes = cursor.fetchall()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    # Imbriquer les catégories et les questions dans les axes appropriés
    for axis in axes:
        axis['categories'] = [cat for cat in categories if cat['axis_id'] == axis['id']]
        for category in axis['categories']:
            category['questions'] = [question for question in questions if question['category_id'] == category['id']]

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    # Renvoyer la page HTML avec les données de l'entreprise et les axes imbriqués
    return render_template('diagnostic_form.html', axes=axes)

@app.route('/submit_diagnostic', methods=['POST'])
def submit_diagnostic():
    form_data = request.form
    enterprise_name = form_data.get('enterprise_name')
    evaluation_created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Insérez le nom de l'entreprise dans la table "enterprise" et récupérez l'ID de l'entreprise créée
    cursor.execute("INSERT INTO enterprise (name) VALUES (%s)", (enterprise_name,))
    enterprise_id = cursor.lastrowid

    # Insérez la date de soumission et l'entreprise dans la table "evaluation"
    cursor.execute("INSERT INTO evaluation (enterprise_id, created_at) VALUES (%s, %s)", (enterprise_id, evaluation_created_at))
    evaluation_id = cursor.lastrowid
    
    # Parcourez toutes les données soumises et identifiez les champs "evaluation_category_comment"
    for field, value in form_data.items():
        if field.startswith('evaluation_category_comment'):
            category_id = int(field[len('evaluation_category_comment'):])
            comment = value
            
            # Insérez les données récupérées dans la table "evaluation_category"
            cursor.execute("INSERT INTO evaluation_category (evaluation_id, category_id, comment) VALUES (%s, %s, %s)", (evaluation_id, category_id, comment))

        # Traitez les champs "evaluation_question_choice" et "evaluation_question_comment"
        elif field.startswith('evaluation_question_choice'):
            question_id = int(field[len('evaluation_question_choice'):])
            choice = int(value)
            comment_field = f'evaluation_question_comment_{question_id}'
            comment = form_data.get(comment_field, '')

            # Insérez les données récupérées dans la table "evaluation_question" ou la table appropriée
            cursor.execute("INSERT INTO evaluation_question (evaluation_id, question_id, choice, comment) VALUES (%s, %s, %s, %s)", (evaluation_id, question_id, choice, comment))
    
    # Validez les changements et fermez le curseur
    connection.commit()
    cursor.close()
    connection.close()

    # Redirigez l'utilisateur vers la page de base
    return redirect(url_for('index'))

# Route pour afficher le diagnostic d'une entreprise
@app.route('/diagnostic/<int:enterprise_id>')
def diagnostic(enterprise_id):
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    # Récupérer les informations de l'entreprise et les données du diagnostic
    cursor.execute("SELECT * FROM enterprise WHERE id=%s", (enterprise_id,))
    enterprise = cursor.fetchone()

    cursor.execute("SELECT * FROM axis")
    axes = cursor.fetchall()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    # Imbriquer les catégories et les questions dans les axes appropriés
    for axis in axes:
        axis['categories'] = [cat for cat in categories if cat['axis_id'] == axis['id']]
        for category in axis['categories']:
            category['questions'] = [question for question in questions if question['category_id'] == category['id']]

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    # Renvoyer la page HTML avec les données de l'entreprise et les axes imbriqués
    return render_template('diagnostic.html', enterprise=enterprise, axes=axes)

if __name__ == '__main__':
    app.run(debug=True)