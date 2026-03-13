"""
@author : Léo Imbert
@created : 13/03/2026
@updated : 13/03/2026
"""

#? ---------- IMPORTATIONS ---------- ?#

from utils import *
import threading
import server

#? ---------- FUNCTIONS ---------- ?#

def vibrate_controller(ctrl_id, duration=50):
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

#? ---------- GAME ---------- ?#

class Game:

    def __init__(self):
        #? Server Init
        self.server = threading.Thread(target=server.start_server, daemon=True)
        self.server.start()

        #? Pyxel Init
        scenes = [
            Scene(0, "PolyCube - Main Menu", self.update_main_menu, self.draw_main_menu, "assets.pyxres")
        ]
        self.pyxel_manager = PyxelManager(228, 128, scenes)

        self.selected_index = 0
        self.last_move_time = 0

        #? Run
        self.pyxel_manager.run()

    def update_main_menu(self):
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

    def draw_main_menu(self):
        pyxel.cls(0)

        pyxel.text(pyxel.width // 2, 80, "POLYCUBE SYSTEM", 7)

#? ---------- MAIN ---------- ?#
if __name__ == "__main__":
    Game()