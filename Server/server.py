import os
import ssl
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Configuration des chemins
# On remonte d'un niveau depuis Server/ pour atteindre Web Page/
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
# On autorise toutes les origines pour les tests en réseau local
socketio = SocketIO(app, cors_allowed_origins="*")

controllers = {}

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/dev')
def dev_dashboard():
    return render_template('dev.html')

@socketio.on('controller_data')
def handle_data(data):
    ctrl_id = data.get('id')
    if ctrl_id:
        controllers[ctrl_id] = data
        emit('update_dashboard', controllers, broadcast=True)

if __name__ == '__main__':
    # Chemins vers les fichiers de certificat
    cert_file = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "key.pem")

    # Vérification si les certificats existent pour lancer en HTTPS
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("\n" + "="*50)
        print("SÉCURITÉ : MODE HTTPS ACTIVÉ")
        print("ATTENTION : Vous DEVEZ utiliser l'URL suivante dans votre navigateur :")
        print("--> https://polycube.local:5000  (ou https://[VOTRE_IP]:5000)")
        print("Si vous oubliez le 'https://', le serveur générera une erreur SSL.")
        print("="*50 + "\n")
        
        # Lancement sécurisé
        socketio.run(app, 
                     host='0.0.0.0', 
                     port=5000, 
                     certfile=cert_file, 
                     keyfile=key_file,
                     debug=True)
    else:
        print("\n" + "!"*50)
        print("SÉCURITÉ : MODE HTTP SIMPLE (Non sécurisé)")
        print("Note : Les capteurs smartphone seront bloqués par le navigateur.")
        print("Générez cert.pem et key.pem pour activer l'HTTPS.")
        print("!"*50 + "\n")
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)