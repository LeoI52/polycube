"""
@author : Léo Imbert
@created : 13/03/2026
@updated : 27/03/2026
"""

#? ---------- IMPORTATIONS ---------- ?#

from utils import *
import threading
import server
from rasp.gpios import GameHardware

#? ---------- CONSTANTS ---------- ?#

PALETTE = [0x000000, 0x2e222f, 0x353658, 0x83769C, 0x686b72, 0xc5cddb, 0xffffff, 0x5ee9e9, 
           0x2890dc, 0x1831a7, 0x053239, 0x005f41, 0x08b23b, 0x47f641, 0xe8ff75, 0xfbbe82, 
           0xde9751, 0xb66831, 0x8a4926, 0x461c14, 0x1e090d, 0x720d0d, 0x813704, 0xda2424, 
           0xef6e10, 0xecab11, 0xece910, 0xf78d8d, 0xf94e6d, 0xc12458, 0x841252, 0x3d083b, 0x000000]

#? ---------- CLASSES ---------- ?#

class ButtonManager:

    def __init__(self, buttons:list[Button]):
        self.buttons = buttons
        self.selected_index = 0
        self.last_move_time = 0
        self.move_cooldown = 60

    def get_player1(self):
        if not server.controllers:
            return None, None
        
        p1_id = next((id for id in server.controllers if "JOUEUR-1" in id), list(server.controllers.keys())[0])
        return p1_id, server.controllers[p1_id]

    def update(self):
        p1_id, p1_data = self.get_player1()
        if not p1_data or not self.buttons:
            return

        accel_x = p1_data['sensors']['accel']['x']
        btn_h = p1_data['buttons']['H']

        if pyxel.frame_count - self.last_move_time > self.move_cooldown:
            if accel_x > 4:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                vibrate_controller(p1_id, 30)
                self.last_move_time = pyxel.frame_count

            elif accel_x < -4:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                vibrate_controller(p1_id, 30)
                self.last_move_time = pyxel.frame_count

        if btn_h:
            vibrate_controller(p1_id, 100)
            button = self.buttons[self.selected_index]
            if button.on_click:
                button.on_click()

    def draw(self, camera_x:int=0, camera_y:int=0):
        for i, button in enumerate(self.buttons):
            button.draw((i == self.selected_index), camera_x=camera_x, camera_y=camera_y)

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
        ]
        self.pyxel_manager = PyxelManager(280, 176, scenes, 0, mouse=True, fullscreen=True)

        #? Main Menu Variables
        self.title = Text("PolyCube", 140, 30, [24, 25, 8, 9], FONT_DEFAULT, 3, CENTER, (VERTICAL, NORMAL_COLOR_MODE, 20), (10, 10, 0.3), outline_color=1)

        self.main_menu_buttons = [
            Button("Saka", 140, 80, 8, 25, 9, 24, FONT_DEFAULT, 2, anchor=CENTER, on_click=lambda : print("go to saka")),
            Button("Pong", 140, 110, 8, 25, 9, 24, FONT_DEFAULT, 2, anchor=CENTER, on_click=lambda : print("go to pong")),
        ]
        self.main_menu_button_manager = ButtonManager(self.main_menu_buttons)

        self.gh = GameHardware()

        #? Run
        self.pyxel_manager.run()

    def update_main_menu(self):
        self.title.update()
        self.main_menu_button_manager.update()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.gh.flash_all(1)

    def draw_main_menu(self):
        pyxel.cls(0)

        self.title.draw()
        self.main_menu_button_manager.draw()

#? ---------- MAIN ---------- ?#

if __name__ == "__main__":
    Game()