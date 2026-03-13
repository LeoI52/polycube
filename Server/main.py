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

#? ---------- CLASSES ---------- ?#

class ButtonManager:

    def __init__(self, buttons:dict, links:dict):
        self.selected_button = 0
        self.buttons = buttons
        self.links = links

    def update(self, ctrl_data:dict):
        for id, button in self.buttons.items():
            button.update()
            if self.selected_button == id and ctrl_data['buttons']['H']:
                button.on_click()

        if ctrl_data['sensors']['accel']['y'] < -4 and self.links[self.selected_button][0] is not None:
            self.selected_button = self.links[self.selected_button][0]
        elif ctrl_data['sensors']['accel']['y'] > 4 and self.links[self.selected_button][1] is not None:
            self.selected_button = self.links[self.selected_button][1]
        elif ctrl_data['sensors']['accel']['x'] > 4 and self.links[self.selected_button][2] is not None:
            self.selected_button = self.links[self.selected_button][2]
        elif ctrl_data['sensors']['accel']['x'] < -4 and self.links[self.selected_button][3] is not None:
            self.selected_button = self.links[self.selected_button][3]

    def draw(self):
        for id, button in self.buttons.items():
            s = id == self.selected_button
            button.draw(s)

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
        self.pyxel_manager = PyxelManager(280, 176, scenes, 1, mouse=True)

        #? Main Menu Variables
        self.title = Text("PolyCube", 140, 20, 6, FONT_DEFAULT, 2, CENTER)

        #? Level Selection Variables
        self.button_manager = ButtonManager({
            0:Button("Jeu 1", 10, 10, 7, 8, 8, 7, FONT_DEFAULT, on_click=lambda : print("B 0")),
            1:Button("Jeu 2", 10, 40, 7, 8, 8, 7, FONT_DEFAULT, on_click=lambda : print("B 1"))
        }, {0:[None, None, None, 1], 1:[None, None, 0, None]})

        self.selected_index = 0
        self.last_move_time = 0

        #? Run
        self.pyxel_manager.run()

    def update_main_menu(self):
        self.title.update()

    def draw_main_menu(self):
        pyxel.cls(0)

        self.title.draw()

    def update_level_selection(self):
        active_controllers = server.controllers.copy()
        p1_id = None

        if active_controllers:
            p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
            p1_data = active_controllers[p1_id]
            self.button_manager.update(p1_data)

    def draw_level_selection(self):
        pyxel.cls(0)
        self.button_manager.draw()

#? ---------- MAIN ---------- ?#

if __name__ == "__main__":
    Game()