import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

# Configuration des chemins d'accès
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
# On augmente la taille du buffer pour éviter le "Too many packets in payload"
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=1e7)

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

@socketio.on('join_dev')
def handle_join_dev():
    """La page de monitoring rejoint une room spéciale pour ne pas polluer les téléphones."""
    join_room('dev_room')
    print("DEBUG: Dashboard de monitoring connecté à la room DEV")

@socketio.on('select_slot')
def handle_select_slot(requested_slot):
    slot = int(requested_slot)
    if slot in occupied_slots and (occupied_slots[slot] is None or occupied_slots[slot] == request.sid):
        occupied_slots[slot] = request.sid
        
        ctrl_id = f"JOUEUR-{slot}"
        controllers[ctrl_id] = {
            'id': ctrl_id,
            'sid': request.sid,
            'buttons': {'H': False, 'Pause': False},
            'sensors': {'alpha': 0, 'beta': 0, 'gamma': 0, 'accel': {'x': 0, 'y': 0, 'z': 0}}
        }
        
        emit('slot_confirmed', {"slot": slot})
        socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})
    else:
        emit('slot_denied', {"message": "Désolé, ce slot est déjà occupé."})

@socketio.on('controller_data')
def handle_data(data):
    ctrl_id = data.get('id')
    if ctrl_id:
        # Toujours mettre à jour le SID actuel
        data['sid'] = request.sid
        controllers[ctrl_id] = data
        # OPTIMISATION : On n'envoie les mises à jour qu'à la room 'dev_room'
        # Les téléphones n'ont pas besoin de recevoir les données des autres
        socketio.emit('update_dashboard', controllers, room='dev_room')

@socketio.on('vibrate_request')
def handle_vibrate_request(ctrl_id):
    """Relaye une demande de vibration vers une manette spécifique."""
    if ctrl_id in controllers:
        target_sid = controllers[ctrl_id].get('sid')
        if target_sid:
            socketio.emit('vibrate', {'duration': 400}, room=target_sid)

@socketio.on('kick_all')
def handle_kick_all():
    """Réinitialise tout et force le reload côté client."""
    global controllers, occupied_slots
    controllers.clear()
    for k in occupied_slots:
        occupied_slots[k] = None
    
    print("--- KICK ALL : Commande reçue ---")
    socketio.emit('force_reset') 
    socketio.emit('update_dashboard', controllers, room='dev_room')
    socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})

@socketio.on('disconnect')
def handle_disconnect():
    for slot, sid in occupied_slots.items():
        if sid == request.sid:
            occupied_slots[slot] = None
            ctrl_id = f"JOUEUR-{slot}"
            if ctrl_id in controllers:
                del controllers[ctrl_id]
            
            socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})
            socketio.emit('update_dashboard', controllers, room='dev_room')
            break

def start_server():
    cert_file = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "key.pem")

    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            print("Démarrage avec Eventlet (Production)...")
            socketio.run(app, host='0.0.0.0', port=5000, 
                         certfile=cert_file, keyfile=key_file, 
                         debug=False, use_reloader=False)
        except TypeError:
            print("Démarrage avec Werkzeug (Développement)...")
            socketio.run(app, host='0.0.0.0', port=5000, 
                         ssl_context=(cert_file, key_file), 
                         debug=False, use_reloader=False)
    else:
        print("Mode HTTP simple...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()