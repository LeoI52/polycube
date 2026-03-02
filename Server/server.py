from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

# Configuration du serveur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'polycube_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire pour stocker l'état des manettes connectées
controllers = {}

@app.route('/')
def index():
    # Sert la page de la manette aux téléphones
    return render_template('controller.html')

@socketio.on('connect')
def handle_connect():
    print("Une manette s'est connectée.")

@socketio.on('controller_data')
def handle_data(data):
    """
    Reçoit les données du téléphone :
    data = {
        'id': 'session_id',
        'buttons': {'A': True, 'B': False, ...},
        'sensors': {'alpha': 0, 'beta': 0, 'gamma': 0, 'accel': {...}}
    }
    """
    # Mise à jour de l'état global pour le moteur de jeu
    controllers[data.get('id')] = data
    
    # Ici, tu pourrais envoyer ces données à ton script de jeu Python
    # via un autre événement ou une file d'attente (Queue)
    # print(f"Data reçue : {data['sensors']['alpha']}") # Debug

if __name__ == '__main__':
    # Lance le serveur sur le port 5000, accessible sur le réseau local
    # Note : Le Raspberry Pi doit être sur le même Wi-Fi que les téléphones
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)