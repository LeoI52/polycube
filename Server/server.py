import eventlet
eventlet.monkey_patch()

import os
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

# Configuration des chemins d'accès
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, template_folder=base_dir, static_folder=base_dir, static_url_path='')
app.config['SECRET_KEY'] = 'polycube_2024_key'
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=1e6)

controllers = {}
occupied_slots = {1: None, 2: None, 3: None, 4: None}

@app.route('/')
def index():
    return render_template('main.html')

@socketio.on('connect')
def handle_connect():
    emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})

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
    else:
        emit('slot_denied', {"message": "Occupé !"})

@socketio.on('controller_data')
def handle_data(data):
    sid = request.sid
    slot = next((s for s, s_id in occupied_slots.items() if s_id == sid), None)
    if slot:
        ctrl_id = f"JOUEUR-{slot}"
        if 'b' in data and 's' in data:
            controllers[ctrl_id]['buttons']['Press'] = data['b'][0]
            controllers[ctrl_id]['buttons']['Back'] = data['b'][1]
            s = data['s']
            controllers[ctrl_id]['sensors']['alpha'], controllers[ctrl_id]['sensors']['beta'], controllers[ctrl_id]['sensors']['gamma'] = s[0], s[1], s[2]
            if len(s) > 3:
                acc = s[3]
                controllers[ctrl_id]['sensors']['accel']['x'], controllers[ctrl_id]['sensors']['accel']['y'], controllers[ctrl_id]['sensors']['accel']['z'] = acc[0], acc[1], acc[2]

@socketio.on('disconnect')
def handle_disconnect():
    for slot, sid in occupied_slots.items():
        if sid == request.sid:
            occupied_slots[slot] = None
            if f"JOUEUR-{slot}" in controllers: del controllers[f"JOUEUR-1"]
            socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})
            break

def dashboard_update_loop():
    while True:
        socketio.emit('update_dashboard', controllers, room='dev_room')
        socketio.sleep(0.1)

def start_server():
    socketio.start_background_task(dashboard_update_loop)
    
    # Chemins absolus pour les certificats
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(current_dir, "SSL/cert.pem")
    key_file = os.path.join(current_dir, "SSL/key.pem")

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"--- SERVEUR HTTPS LANCÉ sur https://0.0.0.0:4000 ---")
        # Utilisation de eventlet directement pour plus de stabilité avec SSL
        socketio.run(app, host='0.0.0.0', port=4000, 
                     certfile=cert_file, keyfile=key_file,
                     debug=False, use_reloader=False, log_output=True)
    else:
        print("!!! ERREUR : Certificats SSL introuvables. Mode HTTP forcé.")
        socketio.run(app, host='0.0.0.0', port=4000, debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()
