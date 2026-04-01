import eventlet
eventlet.monkey_patch()

import os
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

# Configuration des chemins d'accès
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, 
            template_folder=base_dir, 
            static_folder=base_dir, 
            static_url_path='')

app.config['SECRET_KEY'] = 'polycube_2024_key'
# On diminue la taille du buffer car on va optimiser les payloads
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=1e6)

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
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})

@socketio.on('join_dev')
def handle_join_dev():
    join_room('dev_room')
    # Envoyer l'état complet au dashboard lors de sa connexion
    emit('update_dashboard', controllers)
    print("DEBUG: Dashboard monitoring connecté")

@socketio.on('select_slot')
def handle_select_slot(requested_slot):
    slot = int(requested_slot)
    if slot in occupied_slots and (occupied_slots[slot] is None or occupied_slots[slot] == request.sid):
        occupied_slots[slot] = request.sid
        
        ctrl_id = f"JOUEUR-{slot}"
        controllers[ctrl_id] = {
            'id': ctrl_id,
            'sid': request.sid,
            'buttons': {'Press': False, 'Back': False},
            'sensors': {'alpha': 0, 'beta': 0, 'gamma': 0, 'accel': {'x': 0, 'y': 0, 'z': 0}}
        }
        
        emit('slot_confirmed', {"slot": slot})
        socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})
        # Notifier le dashboard du nouveau joueur
        socketio.emit('update_dashboard', controllers, room='dev_room')
    else:
        emit('slot_denied', {"message": "Désolé, ce slot est déjà occupé."})

@socketio.on('controller_data')
def handle_data(data):
    # On identifie le joueur par son SID pour plus de sécurité et de légèreté (plus d'ID dans le payload)
    sid = request.sid
    slot = next((s for s, s_id in occupied_slots.items() if s_id == sid), None)
    
    if slot:
        ctrl_id = f"JOUEUR-{slot}"
        # On décompresse le format compact envoyé par le client
        # Format attendu: { b: [Press, Back], s: [alpha, beta, gamma, [ax, ay, az]] }
        if 'b' in data and 's' in data:
            controllers[ctrl_id]['buttons']['Press'] = data['b'][0]
            controllers[ctrl_id]['buttons']['Back'] = data['b'][1]
            
            s = data['s']
            controllers[ctrl_id]['sensors']['alpha'] = s[0]
            controllers[ctrl_id]['sensors']['beta'] = s[1]
            controllers[ctrl_id]['sensors']['gamma'] = s[2]
            
            if len(s) > 3:
                acc = s[3]
                controllers[ctrl_id]['sensors']['accel']['x'] = acc[0]
                controllers[ctrl_id]['sensors']['accel']['y'] = acc[1]
                controllers[ctrl_id]['sensors']['accel']['z'] = acc[2]

@socketio.on('vibrate_request')
def handle_vibrate_request(ctrl_id):
    if ctrl_id in controllers:
        target_sid = controllers[ctrl_id].get('sid')
        if target_sid:
            socketio.emit('vibrate', {'duration': 400}, room=target_sid)

@socketio.on('kick_all')
def handle_kick_all():
    global controllers, occupied_slots
    controllers.clear()
    for k in occupied_slots:
        occupied_slots[k] = None
    
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

# Tâche de fond pour mettre à jour le dashboard de monitoring à 10Hz
# Cela réduit énormément le trafic sortant si beaucoup de manettes bougent
def dashboard_update_loop():
    while True:
        socketio.emit('update_dashboard', controllers, room='dev_room')
        socketio.sleep(0.1) # 10 Hz

def start_server():
    # Lancement de la boucle de monitoring
    socketio.start_background_task(dashboard_update_loop)
    
    cert_file = os.path.join(os.path.dirname(__file__), "SSL/cert.pem")
    key_file = os.path.join(os.path.dirname(__file__), "SSL/key.pem")

    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            print("Démarrage avec Eventlet (Production)...")
            socketio.run(app, host='0.0.0.0', port=4000, 
                         certfile=cert_file, keyfile=key_file, 
                         debug=False, use_reloader=False)
        except Exception as e:
            print(f"Erreur Eventlet: {e}. Essai avec SSL context...")
            socketio.run(app, host='0.0.0.0', port=4000, 
                         ssl_context=(cert_file, key_file), 
                         debug=False, use_reloader=False)
    else:
        print("Mode HTTP simple...")
        socketio.run(app, host='0.0.0.0', port=4000, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()