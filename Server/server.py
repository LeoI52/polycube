import os
import ssl
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# Configuration des chemins d'accès
# On remonte d'un niveau (..) depuis le dossier Server/ pour atteindre le dossier Web Page/
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
# On autorise toutes les origines pour les tests en réseau local (CORS)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire global pour stocker l'état des manettes en temps réel
# { 'JOUEUR-1': { 'id': ..., 'buttons': ..., 'sensors': ..., 'sid': ... }, ... }
controllers = {}

# Suivi des slots (1 à 4) : { slot_id: sid_du_socket }
occupied_slots = {1: None, 2: None, 3: None, 4: None}

@app.route('/')
def index():
    """Sert la page de la manette aux smartphones."""
    return render_template('main.html')

@app.route('/dev')
def dev_dashboard():
    """Sert la page de monitoring pour le développement."""
    return render_template('dev.html')

@socketio.on('connect')
def handle_connect():
    """Envoyer l'état actuel des slots au nouvel utilisateur dès la connexion."""
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})

@socketio.on('select_slot')
def handle_select_slot(requested_slot):
    """Gère la sélection d'un numéro de joueur (1-4)."""
    slot = int(requested_slot)
    if slot in occupied_slots and occupied_slots[slot] is None:
        # On assigne le SID (Session ID) au slot
        occupied_slots[slot] = request.sid
        
        # On pré-remplit l'entrée dans le dictionnaire controllers avec le SID
        ctrl_id = f"JOUEUR-{slot}"
        controllers[ctrl_id] = {
            'id': ctrl_id,
            'sid': request.sid,
            'buttons': {'H': False, 'Pause': False},
            'sensors': {'alpha': 0, 'beta': 0, 'gamma': 0, 'accel': {'x': 0, 'y': 0, 'z': 0}}
        }
        
        emit('slot_confirmed', {"slot": slot})
        # Informer tout le monde que ce slot est maintenant pris
        emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)
    else:
        emit('slot_denied', {"message": "Désolé, ce slot est déjà occupé."})

@socketio.on('controller_data')
def handle_data(data):
    """Mise à jour des capteurs et boutons envoyés par le téléphone."""
    ctrl_id = data.get('id')
    if ctrl_id:
        # On conserve le SID existant pour ne pas perdre la cible des vibrations
        sid = controllers.get(ctrl_id, {}).get('sid', request.sid)
        controllers[ctrl_id] = data
        controllers[ctrl_id]['sid'] = sid
        
        # Mise à jour du dashboard de dev
        emit('update_dashboard', controllers, broadcast=True)

@socketio.on('kick_all')
def handle_kick_all():
    """Réinitialise tous les slots et force le rechargement des manettes."""
    global controllers, occupied_slots
    controllers.clear()
    for k in occupied_slots:
        occupied_slots[k] = None
    
    print("--- RÉINITIALISATION GLOBALE ---")
    emit('force_reset', broadcast=True)
    emit('update_dashboard', controllers, broadcast=True)
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Libère le slot et nettoie les données si un utilisateur se déconnecte."""
    for slot, sid in occupied_slots.items():
        if sid == request.sid:
            occupied_slots[slot] = None
            ctrl_id = f"JOUEUR-{slot}"
            if ctrl_id in controllers:
                del controllers[ctrl_id]
            
            emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)
            emit('update_dashboard', controllers, broadcast=True)
            break

def start_server():
    """Lance le serveur avec support SSL si les certificats sont présents."""
    cert_file = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "key.pem")
import os
import ssl
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# Configuration des chemins d'accès
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire global pour stocker l'état des manettes
controllers = {}
# Suivi des slots (1 à 4) : { slot_id: sid_du_socket }
occupied_slots = {1: None, 2: None, 3: None, 4: None}

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/dev')
def dev_dashboard():
    return render_template('dev.html')

@socketio.on('connect')
def handle_connect():
    # Envoyer l'état actuel des slots au nouvel utilisateur
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})

@socketio.on('select_slot')
def handle_select_slot(requested_slot):
    slot = int(requested_slot)
    if slot in occupied_slots and occupied_slots[slot] is None:
        occupied_slots[slot] = request.sid
        emit('slot_confirmed', {"slot": slot})
        # Informer les autres que ce slot est pris
        emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)
    else:
        emit('slot_denied', {"message": "Slot déjà occupé"})

@socketio.on('controller_data')
def handle_data(data):
    ctrl_id = data.get('id')
    if ctrl_id:
        controllers[ctrl_id] = data
        emit('update_dashboard', controllers, broadcast=True)

@socketio.on('kick_all')
def handle_kick_all():
    """Réinitialise tous les slots et déconnecte les manettes côté client"""
    global controllers, occupied_slots
    controllers = {}
    for k in occupied_slots:
        occupied_slots[k] = None
    
    print("--- KICK ALL : Réinitialisation de la session ---")
    emit('force_reset', broadcast=True)
    emit('update_dashboard', controllers, broadcast=True)
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # Libérer le slot si l'utilisateur part
    for slot, sid in occupied_slots.items():
        if sid == request.sid:
            occupied_slots[slot] = None
            emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()}, broadcast=True)
            break

def start_server():
    cert_file = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "key.pem")

    if os.path.exists(cert_file) and os.path.exists(key_file):
        socketio.run(app, host='0.0.0.0', port=5000, 
                     certfile=cert_file, keyfile=key_file, 
                     debug=False, use_reloader=False)
    else:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("\n--- MODE HTTPS ACTIVÉ ---")
        socketio.run(app, host='0.0.0.0', port=5000, 
                     certfile=cert_file, keyfile=key_file, 
                     debug=False, use_reloader=False)
    else:
        print("\n--- MODE HTTP SIMPLE (Capteurs risquent d'être bloqués) ---")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()