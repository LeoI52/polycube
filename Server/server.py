import eventlet
eventlet.monkey_patch()

import os
import socket
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Web Page"))

app = Flask(__name__, template_folder=base_dir, static_folder=base_dir, static_url_path='')
app.config['SECRET_KEY'] = 'polycube_2024_key'
# On autorise explicitement toutes les origines pour éviter les blocages CORS en HTTPS
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

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
            if f"JOUEUR-{slot}" in controllers: del controllers[f"JOUEUR-{slot}"]
            socketio.emit('slots_update', {str(k): (v is not None) for k, v in occupied_slots.items()})
            break

def start_server():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(current_dir, "SSL/cert.pem")
    key_file = os.path.join(current_dir, "SSL/key.pem")

    lan_ip = get_lan_ip()
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"\n" + "="*50)
        print(f"SERVEUR HTTPS PRÊT !")
        print(f"URL: https://{lan_ip}:4000")
        print("="*50 + "\n")
        
        # Configuration SSL explicite pour eventlet
        socketio.run(app, host='0.0.0.0', port=4000, 
                     certfile=cert_file, keyfile=key_file,
                     debug=False, use_reloader=False)
    else:
        print("!!! ERREUR : Certificats SSL introuvables. Mode HTTP.")
        socketio.run(app, host='0.0.0.0', port=4000)

if __name__ == '__main__':
    start_server()
