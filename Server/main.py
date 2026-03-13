"""
@author : Léo Imbert
@created : 13/03/2026
@updated : 13/03/2026
"""

#? ---------- IMPORTATIONS ---------- ?#

import importlib.util
import threading
import server
import pyxel
import sys
import os

#? ---------- INIT ---------- ?#

server_thread = threading.Thread(target=server.start_server, daemon=True)
server_thread.start()

GAMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Python playable"))

pyxel.init(228, 128)
pyxel.mouse(True)

selected_index = 0
last_move_time = 0

#? ---------- FUNCTIONS ---------- ?#

def get_game_list():
    if not os.path.exists(GAMES_DIR):
        return []
    return [f for f in os.listdir(GAMES_DIR) if f.endswith('.py') and f != "__init__.py"]

def vibrate_controller(ctrl_id, duration=50):
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

#? ---------- UPDATE / DRAW ---------- ?#

def update():
    active_controllers = server.controllers.copy()
    p1_id = None

    if active_controllers:
        p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
        p1_data = active_controllers[p1_id]
        
        accel_x = p1_data['sensors']['accel']['x']
        btn_h = p1_data['buttons']['H']
        
        current_time = pyxel.frame_count
        if current_time - last_move_time > 300:
            if accel_x > 4 or accel_x < -4:
                vibrate_controller(p1_id, 30)
                last_move_time = current_time

        if btn_h:
            vibrate_controller(p1_id, 100)
            print("goog")

def draw():
    pyxel.cls(0)

    pyxel.text(pyxel.width // 2, 80, "POLYCUBE SYSTEM", 7)

#? ---------- MAIN ---------- ?#
if __name__ == "__main__":
    pyxel.run(update, draw)