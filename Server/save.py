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
    def __init__(self):
        self.buttons = []
        self.selected_index = 0
        self.last_move_time = 0
        self.move_delay = 300  # ms

    def add_button(self, button):
        self.buttons.append(button)

    def clear(self):
        self.buttons.clear()
        self.selected_index = 0

    def update(self, controller_data=None):
        current_time = pyxel.frame_count

        # --- CONTROLLER NAVIGATION ---
        if controller_data:
            accel_x = controller_data['sensors']['accel']['x']
            btn_h = controller_data['buttons']['H']

            if current_time - self.last_move_time > self.move_delay:
                if accel_x > 4:
                    self.selected_index = (self.selected_index + 1) % len(self.buttons)
                    self.last_move_time = current_time

                elif accel_x < -4:
                    self.selected_index = (self.selected_index - 1) % len(self.buttons)
                    self.last_move_time = current_time

            # --- CLICK / SELECT ---
            if btn_h and self.buttons:
                selected_button = self.buttons[self.selected_index]
                if selected_button.on_click:
                    selected_button.on_click()

        # --- MOUSE UPDATE (optional fallback) ---
        for btn in self.buttons:
            btn.update()

    def draw(self):
        for i, btn in enumerate(self.buttons):
            btn.draw(selected=(i == self.selected_index))

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
        self.button_manager = ButtonManager()
        self.button_manager.add_button(Button("Jeu 1", 10, 10, 7, 8, 8, 7, FONT_DEFAULT, on_click=lambda : print("B 0")))
        self.button_manager.add_button(Button("Jeu 2", 10, 40, 7, 8, 8, 7, FONT_DEFAULT, on_click=lambda : print("B 1")))
        
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
            p1_data = active_controllers[p1_id] if p1_id else None
            self.button_manager.update(p1_data)

    def draw_level_selection(self):
        pyxel.cls(1)

        self.button_manager.draw()
        
        pyxel.text(pyxel.width//2 - 30, 20, "POLYCUBE SYSTEM", 12)

        p1_connected = any("JOUEUR-1" in id for id in server.controllers)
        status_color = 11 if p1_connected else 8
        status_text = "MANETTE OK" if p1_connected else "MANETTE DECONNECTEE"
        
        pyxel.rect(0, pyxel.height - 15, pyxel.width, 15, 0)
        pyxel.text(5, pyxel.height - 10, status_text, status_color)

#? ---------- MAIN ---------- ?#

if __name__ == "__main__":
    Game()