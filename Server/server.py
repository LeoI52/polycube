import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Configuration des chemins pour correspondre à ton arborescence
# On remonte d'un niveau depuis Server/ pour atteindre Web Page/
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
# On autorise toutes les origines pour faciliter les tests en local
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire global pour stocker l'état des manettes
controllers = {}

@app.route('/')
def index():
    # Page manette pour les smartphones
    return render_template('main.html')

@app.route('/dev')
def dev_dashboard():
    # Page de monitoring pour le développement
    return render_template('dev.html')

@socketio.on('connect')
def handle_connect():
    print("Nouvelle connexion d'un périphérique.")

@socketio.on('controller_data')
def handle_data(data):
    """
    Reçoit les données : ID, boutons (H, Pause), 
    orientation (alpha, beta, gamma) et accélération (x, y, z en g).
    """
    ctrl_id = data.get('id')
    if ctrl_id:
        controllers[ctrl_id] = data
        # On diffuse les données à tous les clients (notamment la page /dev)
        emit('update_dashboard', controllers, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # On pourrait ici nettoyer controllers, mais on le garde pour le debug
    pass

if __name__ == '__main__':
    # On écoute sur toutes les interfaces (0.0.0.0) sur le port 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)