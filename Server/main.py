"""
@author : Léo Imbert
@created : 13/03/2026
@updated : 13/03/2026
"""

#? ---------- IMPORTATIONS ---------- ?#

from utils import *
import threading
import server

#? ---------- CONSTANTS ---------- ?#

PALETTE = [0x000000, 0x2e222f, 0x353658, 0x83769C, 0x686b72, 0xc5cddb, 0xffffff, 0x5ee9e9, 
           0x2890dc, 0x1831a7, 0x053239, 0x005f41, 0x08b23b, 0x47f641, 0xe8ff75, 0xfbbe82, 
           0xde9751, 0xb66831, 0x8a4926, 0x461c14, 0x1e090d, 0x720d0d, 0x813704, 0xda2424, 
           0xef6e10, 0xecab11, 0xece910, 0xf78d8d, 0xf94e6d, 0xc12458, 0x841252, 0x3d083b, 0x000000]

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
            Scene(0, "PolyCube - Menu Principal", self.update_main_menu, self.draw_main_menu, "assets/assets.pyxres", PALETTE),
            Scene(1, "PolyCube - Séléction de jeu", self.update_level_selection, self.draw_level_selection, "assets/assets.pyxres", PALETTE),
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

        pyxel.text(pyxel.width // 2, 80, "POLYCUBE SYSTEM", 6)

    def update_level_selection(self):
        pass

    def draw_level_selection(self):
        pass

#? ---------- MAIN ---------- ?#
if __name__ == "__main__":
    Game()