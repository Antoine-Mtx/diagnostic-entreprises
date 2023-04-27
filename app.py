from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, Response
from datetime import datetime
import pymysql
import os
import json
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Configurer vos informations de connexion à la base de données ici
db_config = {
    'host': os.environ['DB_HOST'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'db': os.environ['DB_NAME'],
    'charset': 'utf8mb4',
}

# ------------------
#       ROUTES
# ------------------

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

    # Insérer le nom de l'entreprise dans la table "enterprise" et récupérer l'ID de l'entreprise créée
    cursor.execute("INSERT INTO enterprise (name) VALUES (%s)", (enterprise_name,))
    enterprise_id = cursor.lastrowid

    # Insérer la date de soumission et l'entreprise dans la table "evaluation"
    cursor.execute("INSERT INTO evaluation (enterprise_id, created_at) VALUES (%s, %s)", (enterprise_id, evaluation_created_at))
    evaluation_id = cursor.lastrowid
    
    # Parcourer toutes les données soumises et identifier les champs "evaluation_category_comment"
    for field, value in form_data.items():
        if field.startswith('evaluation_category_comment'):
            category_id = int(field[len('evaluation_category_comment'):])
            comment = value
            
            # Insérer les données récupérées dans la table "evaluation_category"
            cursor.execute("INSERT INTO evaluation_category (evaluation_id, category_id, comment) VALUES (%s, %s, %s)", (evaluation_id, category_id, comment))

        # Traiter les champs "evaluation_question_choice" et "evaluation_question_comment"
        elif field.startswith('evaluation_question_choice'):
            question_id = int(field[len('evaluation_question_choice'):])
            choice = int(value)
            comment_field = f'evaluation_question_comment_{question_id}'
            comment = form_data.get(comment_field, '')

            # Insérer les données récupérées dans la table "evaluation_question" ou la table appropriée
            cursor.execute("INSERT INTO evaluation_question (evaluation_id, question_id, choice, comment) VALUES (%s, %s, %s, %s)", (evaluation_id, question_id, choice, comment))
    
    # Valider les changements et fermer le curseur
    connection.commit()
    cursor.close()
    connection.close()

    # Rediriger l'utilisateur vers la page de base
    return redirect(url_for('index'))

@app.route('/diagnostics')
def diagnostics():
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer les informations de l'entreprise et les dates de diagnostic
    cursor.execute("SELECT e.id AS enterprise_id, e.name AS enterprise_name, eval.id AS evaluation_id, eval.created_at FROM enterprise e JOIN evaluation eval ON e.id = eval.enterprise_id")
    evaluations = cursor.fetchall()

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    # Renvoyer la page HTML avec les données des entreprises et les dates de diagnostic
    return render_template('diagnostics.html', evaluations=evaluations)


@app.route('/diagnostic/<int:evaluation_id>', endpoint="diagnostic_view")
def diagnostic(evaluation_id):
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer les informations de l'évaluation et de l'entreprise
    cursor.execute("SELECT e.*, eval.id AS evaluation_id, eval.created_at FROM enterprise e JOIN evaluation eval ON e.id = eval.enterprise_id WHERE eval.id=%s", (evaluation_id,))
    evaluation = cursor.fetchone()

    cursor.execute("SELECT * FROM axis")
    axes = cursor.fetchall()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    cursor.execute("SELECT eq.* FROM evaluation_question eq WHERE eq.evaluation_id=%s", (evaluation_id,))
    evaluation_questions = cursor.fetchall()

    # Calculer les scores moyens pour chaque catégorie
    for category in categories:
        total_score = 0
        question_count = 0

        for question in questions:
            if question['category_id'] == category['id']:
                for evaluation_question in evaluation_questions:
                    if evaluation_question['question_id'] == question['id']:
                        total_score += evaluation_question['choice']
                        question_count += 1
                        break

        if question_count > 0:
            category['score'] = round(total_score / question_count, 2)*5/2
        else:
            category['score'] = 0

    # Imbriquer les catégories et les questions dans les axes appropriés
    for axis in axes:
        axis['categories'] = [cat for cat in categories if cat['axis_id'] == axis['id']]
        for category in axis['categories']:
            category['questions'] = [question for question in questions if question['category_id'] == category['id']]

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    # Renvoyer la page HTML avec les données de l'entreprise et les axes imbriqués
    return render_template('diagnostic.html', enterprise=evaluation, axes=axes, evaluation={"questions": evaluation_questions})

# Route pour afficher le diagnostic d'une entreprise
@app.route('/diagnostic_update/<int:enterprise_id>')
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
    return render_template('diagnostic_update.html', enterprise=enterprise, axes=axes)

# ---------------
#       API
# ---------------

@app.route('/api/diagnostics', methods=['GET'])
def api_diagnostics():
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer les informations de l'entreprise et les dates de diagnostic
    cursor.execute("SELECT e.id AS enterprise_id, e.name AS enterprise_name, eval.id AS evaluation_id, eval.created_at FROM enterprise e JOIN evaluation eval ON e.id = eval.enterprise_id")
    evaluations = cursor.fetchall()

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    response = Response(json.dumps(diagnostics, ensure_ascii=False), content_type='application/json; charset=utf-8')
    return response

@app.route('/api/diagnostic/<int:evaluation_id>', methods=['GET'])
def api_diagnostic(evaluation_id):
    # Établir la connexion avec la base de données
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Récupérer les informations de l'évaluation et de l'entreprise
    cursor.execute("SELECT e.*, eval.id AS evaluation_id, eval.created_at FROM enterprise e JOIN evaluation eval ON e.id = eval.enterprise_id WHERE eval.id=%s", (evaluation_id,))
    evaluation = cursor.fetchone()

    cursor.execute("SELECT * FROM axis")
    axes = cursor.fetchall()

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()

    cursor.execute("SELECT * FROM question")
    questions = cursor.fetchall()

    cursor.execute("SELECT eq.* FROM evaluation_question eq WHERE eq.evaluation_id=%s", (evaluation_id,))
    evaluation_questions = cursor.fetchall()

    # Imbriquer les catégories et les questions dans les axes appropriés
    for axis in axes:
        axis['categories'] = [cat for cat in categories if cat['axis_id'] == axis['id']]
        for category in axis['categories']:
            category['questions'] = [question for question in questions if question['category_id'] == category['id']]

    # Fermer la connexion à la base de données
    cursor.close()
    connection.close()

    diagnostic = {
        'enterprise': evaluation,
        'axes': axes,
        'evaluation_questions': evaluation_questions
    }

    if diagnostic:
        response = Response(json.dumps(diagnostic, ensure_ascii=False), content_type='application/json; charset=utf-8')
        return response
    else:
        return make_response(jsonify({"error": "Diagnostic not found"}), 404)


if __name__ == '__main__':
    app.run(debug=True)