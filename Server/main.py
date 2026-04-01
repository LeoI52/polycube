#? ---------- SERVEUR EN PRIORITÉ ---------- ?#
import server # Charge eventlet et fait le monkey_patch immédiatement
import threading

# On lance le serveur dans un thread séparé tout de suite
# pour être sûr d'avoir accès à la page web même si le reste bug
print("Démarrage du serveur web (port 4000)...")
server_thread = threading.Thread(target=server.start_server, daemon=True)
server_thread.start()

#? ---------- AUTRES IMPORTS ---------- ?#
from utils import *
import random
import time

print("Chargement des GPIO (en tâche de fond)...")
gpio_manager = None
def load_gpio():
    global gpio_manager
    try:
        from rasp.gpios import gpio_manager as gm
        gpio_manager = gm
        print("GPIO opérationnels.")
    except Exception as e:
        print(f"GPIO non disponibles: {e}")

# On charge les GPIO dans un thread pour ne pas bloquer le lancement de Pyxel
threading.Thread(target=load_gpio, daemon=True).start()

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
        self.move_cooldown = 45

    def get_player1(self):
        local_controllers = server.controllers.copy()
        if not local_controllers: return None, None
        p1_id = next((cid for cid in local_controllers if "JOUEUR-1" in cid), next(iter(local_controllers)))
        return p1_id, local_controllers[p1_id]

    def update(self):
        p1_id, p1_data = self.get_player1()
        self.buttons[self.selected_index].update()
        if not p1_data or not self.buttons: return

        accel_x = p1_data['sensors']['accel']['x']
        btn_h = p1_data['buttons']['Press']

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
            if button.on_click: button.on_click()

    def draw(self, camera_x:int=0, camera_y:int=0):
        for i, button in enumerate(self.buttons):
            button.draw((i == self.selected_index), camera_x=camera_x, camera_y=camera_y)

class Player:
    def __init__(self, x:int, y:int, player_number:int, tagger:bool):
        self.x, self.y = x, y
        self.w, self.h = 8, 8
        self.player_number = player_number
        self.tagger = tagger
        self.tagged_timer = 0
        self.u = random.randint(0, 12) * 8
        self.velocity_x = 0
        self.vx_r = 0
        self.velocity_y = 0
        self.max_velocity_y = 6
        self.gravity = 0.4
        self.friction = 0.8
        self.speed = 1.6
        self.coyote_timer = 0
        self.coyote_time = 6
        self.jump_buffer_timer = 0
        self.jump_buffer_time = 12
        self.jump_power = 5.5
        self.jumping = False
        self.facing_right = True if player_number == 1 else False
        self.on_ground = False

    def update(self, other):
        self.coyote_timer = max(0, self.coyote_timer - 1)
        self.tagged_timer = max(0, self.tagged_timer - 1)
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - 1)

        self.velocity_y = min(self.velocity_y + self.gravity, self.max_velocity_y)
        self.velocity_x *= self.friction
        self.on_ground = collision_rect_tiles(self.x, self.y + 1, self.w, self.h, COLLISION_TILES)
        if self.on_ground:
            if not self.jumping: self.velocity_y = 0
            self.jumping = False
            self.coyote_timer = self.coyote_time

        if collision_rect_rect(self.x, self.y, self.w, self.h, other.x, other.y, other.w, other.h) and self.tagger and other.tagged_timer == 0:
            self.tagged_timer = 60
            self.tagger, other.tagger = False, True

        if left(self.player_number): self.velocity_x = -self.speed; self.facing_right = False
        if right(self.player_number): self.velocity_x = self.speed; self.facing_right = True
        
        if jump(self.player_number):
            if (self.on_ground or self.coyote_timer > 0) and not self.jumping:
                self.velocity_y = -self.jump_power
                self.jumping = True
            else: self.jump_buffer_timer = self.jump_buffer_time
            
        if self.on_ground and self.jump_buffer_timer > 0:
            self.velocity_y = -self.jump_power
            self.jumping, self.jump_buffer_timer = True, 0

        # Mouvement X
        step_x = 1 if self.velocity_x > 0 else -1
        for _ in range(int(abs(self.velocity_x))):
            if not collision_rect_tiles(self.x + step_x, self.y, self.w, self.h, COLLISION_TILES): self.x += step_x
        # Mouvement Y
        step_y = 1 if self.velocity_y > 0 else -1
        for _ in range(int(abs(self.velocity_y))):
            if not collision_rect_tiles(self.x, self.y + step_y, self.w, self.h, COLLISION_TILES): self.y += step_y

    def draw(self):
        w = self.w if self.facing_right else -self.w
        v = 8 if crouch(self.player_number) else 0
        pyxel.blt(self.x, self.y, 0, self.u, 0 + v, w, self.h, 0)
        if self.tagger and not pyxel.frame_count // 6 % 6 == 0:
            blt_outline(self.x,self.y,0,self.u,v,8,8,col=8,flip_x=not self.facing_right)

#? ---------- FUNCTIONS ---------- ?#

def vibrate_controller(ctrl_id, duration=50):
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

def collision_rect_tiles(x, y, w, h, tiles, tilemap=0):
    for ty in range(int(y // 8), int((y + h - 1) // 8) + 1):
        for tx in range(int(x // 8), int((x + w - 1) // 8) + 1):
            if pyxel.tilemaps[tilemap].pget(tx, ty) in tiles: return True
    return False

def blt_outline(x, y, img, u, v, w, h, col, flip_x=False, colkey=0):
    for py in range(h):
        for px in range(w):
            sx = u + (w - 1 - px if flip_x else px)
            sy = v + py
            if pyxel.images[img].pget(sx, sy) == colkey: continue
            for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]: pyxel.pset(x + px + ox, y + py + oy, col)

def left(p): return pyxel.btn(pyxel.KEY_A if p==1 else pyxel.KEY_LEFT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX if p==1 else pyxel.GAMEPAD3_AXIS_LEFTX) < -8000
def right(p): return pyxel.btn(pyxel.KEY_D if p==1 else pyxel.KEY_RIGHT) or pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX if p==1 else pyxel.GAMEPAD3_AXIS_LEFTX) > 8000
def jump(p): return pyxel.btnp(pyxel.KEY_Z if p==1 else pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A if p==1 else pyxel.GAMEPAD3_BUTTON_A)
def interact(p): return pyxel.btnp(pyxel.KEY_S if p==1 else pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X if p==1 else pyxel.GAMEPAD3_BUTTON_X)
def crouch(p): return pyxel.btn(pyxel.KEY_S if p==1 else pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_X if p==1 else pyxel.GAMEPAD3_BUTTON_X)

COLLISION_TILES = [(0,1),(3,2)]

#? ---------- GAME ---------- ?#

class Game:
    def __init__(self):
        print("Initialisation Pyxel...")
        scenes = [
            Scene(0, "PolyCube - Main Menu", self.update_main_menu, self.draw_main_menu, "assets/assets.pyxres", PALETTE),
            Scene(1, "Polycube - Saka", self.update_saka, self.draw_saka, "assets/assets.pyxres", PALETTE)
        ]
        self.pyxel_manager = PyxelManager(280, 176, scenes, 0, mouse=True, fullscreen=>False)

        self.title = Text("PolyCube", 140, 30, [24, 25, 8, 9], FONT_DEFAULT, 3, CENTER, (VERTICAL, NORMAL_COLOR_MODE, 20), (10, 10, 0.3), outline_color=1)
        self.main_menu_buttons = [
            Button("Saka", 40, 80, 8, 25, 9, 24, FONT_DEFAULT, 2, anchor=TOP_LEFT, on_click=self.saka_act),
            Button("Pong", 40, 156, 8, 25, 9, 24, FONT_DEFAULT, 2, anchor=BOTTOM_LEFT, on_click=lambda : print("go to pong")),
            Button("Far West", 240, 80, 8, 25, 9, 24, FONT_DEFAULT, 2, anchor=TOP_RIGHT, on_click=lambda : print("go to far west")),
        ]
        self.main_menu_button_manager = ButtonManager(self.main_menu_buttons)

        self.background = MatrixRainBackground(16, 0.5, [21, 22, 23])
        t = random.choice([False, True])
        self.player_1 = Player(10, 10, 1, t)
        self.player_2 = Player(262, 160, 2, not t)

        print("Lancement de la boucle Pyxel !")
        self.pyxel_manager.run()

    def saka_act(self):
        if gpio_manager: gpio_manager.blink_start_sequence()
        self.pyxel_manager.change_scene_transition(TransitonPixelate(1, 2, 8, 6))

    def update_main_menu(self):
        self.title.update()
        self.main_menu_button_manager.update()
        if gpio_manager and pyxel.frame_count % 30 == 0:
            gpio_manager.update_controllers(server.occupied_slots)

    def draw_main_menu(self):
        pyxel.cls(0)
        self.title.draw()
        self.main_menu_button_manager.draw()

    def update_saka(self):
        self.player_1.update(self.player_2)
        self.player_2.update(self.player_1)
        self.background.update()
        if pyxel.btnp(pyxel.KEY_R):
            t = random.choice([False, True])
            self.player_1, self.player_2 = Player(10, 10, 1, t), Player(262, 160, 2, not t)

    def draw_saka(self):
        pyxel.cls(0)
        self.background.draw()
        self.player_1.draw()
        self.player_2.draw()
        pyxel.bltm(0, 0, 0, 0, 0, 280, 176, 0)

if __name__ == "__main__":
    Game()
