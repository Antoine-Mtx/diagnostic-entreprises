from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
import pymysql

app = Flask(__name__)

# Configurez vos informations de connexion à la base de données ici
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'db': 'diagnostic'
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

# Route pour soumettre le formulaire de diagnostic
@app.route('/submit_diagnostic', methods=['POST'])
def submit_diagnostic():
    form_data = request.form
    company_name = form_data.get('company_name')
    
    # Insérez le nom de l'entreprise dans la table "entreprise" et récupérez l'ID de l'entreprise créée
    cursor.execute("INSERT INTO entreprise (name) VALUES (%s)", (company_name,))
    entreprise_id = cursor.lastrowid
    
    # Parcourez toutes les données soumises et identifiez les champs "comment"
    for field, value in form_data.items():
        if field.startswith('comment_'):
            category_id = int(field[8:])
            comment = value
            
            # Insérez les données récupérées dans la table "evaluation_category"
            cursor.execute("INSERT INTO evaluation_category (entreprise_id, category_id, comment) VALUES (%s, %s, %s)", (entreprise_id, category_id, comment))
    
    # Validez les changements et fermez le curseur
    db.commit()
    cursor.close()

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