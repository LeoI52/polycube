"""
@author : Léo Imbert & Projet smartphonique
@created : 13/03/2026
@updated : 03/04/2026
"""

#? ---------- CHARGEMENT GPIO ---------- ?#
try:
    from rasp.gpios import gpio_manager
    gpio_manager.startup_sequence()
except ImportError:
    gpio_manager = None

#? ---------- CHARGEMENT DU SERVEUR ---------- ?#
import server
import threading
import random
import pyxel

def run_server():
    server.start_server()
threading.Thread(target=run_server, daemon=True).start()

#? ---------- IMPORTATIONS ---------- ?#
from utils import *

#? ---------- CONSTANTS ---------- ?#
PALETTE = [0x000000, 0xbe4a2f, 0xd77643, 0xead4aa, 0xe4a672, 0xb86f50, 0x733e39, 0x3e2731, 
           0xa22633, 0xe43b44, 0xf77622, 0xfeae34, 0xfee761, 0x63c74d, 0x3e8948, 0x265c42, 
           0x193c3e, 0x124e89, 0x0099db, 0x2ce8f5, 0xffffff, 0xc0cbdc, 0x8b9bb4, 0x5a6988, 
           0x3a4466, 0x262b44, 0xff0044, 0x68386c, 0xb55088, 0xf6757a, 0xe8b796, 0xc28569, 0x000000]

#? ---------- CLASSES PONG ---------- ?#

class PongPaddle:
    def __init__(self, side, player_num, color):
        self.side = side # 'left', 'right', 'top', 'bottom'
        self.player_num = player_num
        self.color = color
        self.active = False
        self.w = 4 if side in ['left', 'right'] else 40
        self.h = 40 if side in ['left', 'right'] else 4
        self.reset_position()

    def reset_position(self):
        if self.side == 'left':
            self.x, self.y = 10, 88 - self.h/2
        elif self.side == 'right':
            self.x, self.y = 266, 88 - self.h/2
        elif self.side == 'top':
            self.x, self.y = 140 - self.w/2, 10
        elif self.side == 'bottom':
            self.x, self.y = 140 - self.w/2, 162

    def update(self):
        p_id, p_data = get_player_data(f"PLAYER-{self.player_num}")
        self.active = p_data is not None
        
        if self.active:
            # Utilisation de l'accéléromètre pour bouger (inclinaison latérale)
            accel_y = p_data['sensors']['accel']['y']
            if self.side in ['left', 'right']:
                self.y += accel_y * 0.8
                self.y = clamp(self.y, 10, 166 - self.h)
            else:
                self.x += accel_y * 0.8
                self.x = clamp(self.x, 10, 270 - self.w)

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        else:
            # Si pas de joueur, on dessine un mur protecteur
            if self.side == 'left': pyxel.rect(0, 0, 5, 176, 7)
            if self.side == 'right': pyxel.rect(275, 0, 5, 176, 7)
            if self.side == 'top': pyxel.rect(0, 0, 280, 5, 7)
            if self.side == 'bottom': pyxel.rect(0, 171, 280, 5, 7)

class PongBall:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = 140, 88
        angle = random.choice([45, 135, 225, 315]) + random.uniform(-10, 10)
        rad = angle * (3.14159 / 180.0)
        self.vx = pyxel.cos(rad) * 2.5
        self.vy = pyxel.sin(rad) * 2.5
        self.radius = 3

    def update(self, paddles):
        self.x += self.vx
        self.y += self.vy

        # --- Collisions avec les murs (si joueurs absents) ---
        for p in paddles:
            if not p.active:
                if p.side == 'left' and self.x - self.radius < 5:
                    self.vx *= -1
                    self.x = 5 + self.radius
                elif p.side == 'right' and self.x + self.radius > 275:
                    self.vx *= -1
                    self.x = 275 - self.radius
                elif p.side == 'top' and self.y - self.radius < 5:
                    self.vy *= -1
                    self.y = 5 + self.radius
                elif p.side == 'bottom' and self.y + self.radius > 171:
                    self.vy *= -1
                    self.y = 171 - self.radius

        # --- Collisions avec les Raquettes ---
        for p in paddles:
            if p.active:
                if (self.x + self.radius > p.x and self.x - self.radius < p.x + p.w and
                    self.y + self.radius > p.y and self.y - self.radius < p.y + p.h):
                    if p.side in ['left', 'right']:
                        self.vx *= -1.05 # Accélération progressive
                        self.x = p.x + p.w + self.radius if p.side == 'left' else p.x - self.radius
                    else:
                        self.vy *= -1.05
                        self.y = p.y + p.h + self.radius if p.side == 'top' else p.y - self.radius
                    
                    p_id, _ = get_player_data(f"PLAYER-{p.player_num}")
                    if p_id: vibrate_controller(p_id, 30)

        # --- Sortie (Score) ---
        if self.x < 0 or self.x > 280 or self.y < 0 or self.y > 176:
            self.reset()

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, 12)

#? ---------- CLASSES EXISTANTES (SAKA) ---------- ?#

class ButtonManager:
    def __init__(self, buttons:list[Button]):
        self.buttons = buttons
        self.selected_index = 0
        self.last_move_time = 0
        self.move_cooldown = 15

    def update(self):
        p1_id, p1_data = get_player_data("PLAYER-1")
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
            self.buttons[self.selected_index].on_click()

    def draw(self, camera_x:int=0, camera_y:int=0):
        for i, button in enumerate(self.buttons):
            button.draw((i == self.selected_index), camera_x=camera_x, camera_y=camera_y)

class Player:
    def __init__(self, x:int, y:int, u:int, level:int, player_number:int, tagger:bool):
        self.x, self.y = x, y
        self.w, self.h = 8, 8
        self.player_number = player_number
        self.tagger = tagger
        self.tagged_timer = 0
        self.u = u
        self.controls = None
        self.level = level
        self.velocity_x = 0
        self.vx_r = 0
        self.velocity_y = 0
        self.max_velocity_y = 6
        self.gravity = 0.4
        self.friction = 0.8
        self.speed = 1.4
        self.coyote_timer = 0
        self.coyote_time = 6
        self.jump_buffer_timer = 0
        self.jump_buffer_time = 12
        self.jump_power = 5.5
        self.jumping = False
        self.facing_right = True if player_number == 1 else False
        self.on_ground = False

    def _handle_timers(self):
        self.coyote_timer = max(0, self.coyote_timer - 1)
        self.tagged_timer = max(0, self.tagged_timer - 1)
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - 1)

    def _handle_physics(self):
        self.velocity_y = min(self.velocity_y + self.gravity, self.max_velocity_y)
        self.velocity_x *= self.friction
        self.on_ground = collision_rect_tiles(self.x, self.y + 1, self.w, self.h, COLLISION_TILES, self.level)
        if self.on_ground:
            if not self.jumping: self.velocity_y = 0
            self.jumping = False
            self.coyote_timer = self.coyote_time

    def _handle_movement(self):
        if left(self.controls):
            self.velocity_x = -self.speed
            self.facing_right = False
        if right(self.controls):
            self.velocity_x = self.speed
            self.facing_right = True
        if jump(self.controls) and ((self.on_ground or self.coyote_timer > 0) and not self.jumping):
            self.velocity_y = -self.jump_power
            self.jumping = True
            pyxel.play(0, 0)
        elif jump(self.controls):
            self.jump_buffer_timer = self.jump_buffer_time
        if self.on_ground and self.jump_buffer_timer > 0:
            self.velocity_y = -self.jump_power
            self.jumping = True
            self.jump_buffer_timer = 0

    def _handle_levers(self):
        tiles = tiles_in_rect(self.x- 4, self.y, self.w + 8, self.h, LEVER_TILES, self.level)
        if tiles:
            timer, door_tile, hollow_tile, door_tiles, timer_duration = LEVERS_DICT[self.level][tiles[0]]
            u, v = pyxel.tilemaps[self.level].pget(*tiles[0])
            if timer == 0:
                pyxel.tilemaps[self.level].pset(*tiles[0], (u + 1, v))
                LEVERS_DICT[self.level][tiles[0]][0] = timer_duration
                for tx, ty in door_tiles:
                    if pyxel.tilemaps[self.level].pget(tx, ty) == door_tile:
                        pyxel.tilemaps[self.level].pset(tx, ty, hollow_tile)
                    else:
                        pyxel.tilemaps[self.level].pset(tx, ty, door_tile)

    def _update_velocity_x(self):
        if self.velocity_x != 0:
            self.velocity_x += self.vx_r
            self.vx_r = self.velocity_x - int(self.velocity_x)
            self.velocity_x -= self.vx_r
            step_x = 1 if self.velocity_x > 0 else -1
            for _ in range(int(abs(self.velocity_x))):
                if not collision_rect_tiles(self.x + step_x, self.y, self.w, self.h, COLLISION_TILES, self.level) and 0 <= self.x + step_x and self.x + self.w + step_x <= pyxel.width:
                    self.x += step_x
                else:
                    self.velocity_x = 0
                    break

    def _update_velocity_y(self):
        if self.velocity_y != 0:
            step_y = 1 if self.velocity_y > 0 else -1
            for _ in range(int(abs(self.velocity_y))):
                if not collision_rect_tiles(self.x, self.y + step_y, self.w, self.h, COLLISION_TILES, self.level) and 0 <= self.y + step_y and self.y + self.h +step_y <= pyxel.height:
                    self.y += step_y
                else:
                    self.velocity_y = 0
                    break
    
    def update(self, other):
        _, self.controls = get_player_data(f"PLAYER-{self.player_number}")
        self._handle_timers()
        self._handle_physics()
        if collision_rect_rect(self.x, self.y, self.w, self.h, other.x, other.y, other.w, other.h) and self.tagger and other.tagged_timer == 0:
            self.tagged_timer = 60
            self.tagger = False
            other.tagger = True
            if gpio_manager: gpio_manager.tag()
        if self.controls:
            self._handle_movement()
        self._handle_levers()
        self._update_velocity_x()
        self._update_velocity_y()

    def draw(self):
        w = self.w if self.facing_right else -self.w
        v = 8 if self.controls and crouch(self.controls) else 0
        pyxel.blt(self.x, self.y, 0, self.u, 0 + v, w, self.h, 0)
        if self.tagger and not pyxel.frame_count // 6 % 6 == 0:
            blt_outline(self.x, self.y, 0, self.u, v, 8, 8, col=8, flip_x=not self.facing_right)

class Teleporter:
    def __init__(self, x:int, y:int, w:int, h:int, x_spawn:int, y_spawn:int, teleporter_id:int, particle_spawn_off:int=0):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.particle_spawn_off = particle_spawn_off
        self.x_spawn, self.y_spawn = x_spawn, y_spawn
        self.teleporter_id = teleporter_id
    def update(self, players:list, level:int):
        for player in players:
            if collision_rect_rect(player.x, player.y, player.w, player.h, self.x, self.y, self.w, self.h):
                nx, ny = TELEPORTERS[level][self.teleporter_id].x_spawn, TELEPORTERS[level][self.teleporter_id].y_spawn
                player.x, player.y = nx, ny

#? ---------- FUNCTIONS ---------- ?#

def vibrate_controller(ctrl_id, duration=50):
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

def get_player_data(player_name:str):
    controllers = server.controllers.copy()
    p_id = next((cid for cid in controllers if player_name in cid), None)
    if p_id: return p_id, controllers[p_id]
    return None, None

def collision_rect_tiles(x:int, y:int, w:int, h:int, tiles:list, tilemaps:int|list=0)-> bool:
    start_tile_x, start_tile_y = int(x // 8), int(y // 8)
    end_tile_x, end_tile_y = int((x + w - 1) // 8), int((y + h - 1) // 8)
    tilemaps = [tilemaps] if isinstance(tilemaps, int) else tilemaps
    for tile_y in range(start_tile_y, end_tile_y + 1):
        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tm in tilemaps:
                if 0 <= tile_x < pyxel.tilemaps[tm].width and 0 <= tile_y < pyxel.tilemaps[tm].height:
                    if pyxel.tilemaps[tm].pget(tile_x, tile_y) in tiles: return True
    return False

def tiles_in_rect(x:int, y:int, w:int, h:int, tiles:list, tilemaps:int|list=0)-> list:
    res = []
    start_tile_x, start_tile_y = int(x // 8), int(y // 8)
    end_tile_x, end_tile_y = int((x + w - 1) // 8), int((y + h - 1) // 8)
    tilemaps = [tilemaps] if isinstance(tilemaps, int) else tilemaps
    for tile_y in range(start_tile_y, end_tile_y + 1):
        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tm in tilemaps:
                if 0 <= tile_x < pyxel.tilemaps[tm].width and 0 <= tile_y < pyxel.tilemaps[tm].height:
                    if pyxel.tilemaps[tm].pget(tile_x, tile_y) in tiles: res.append((tile_x, tile_y))
    return res

def blt_outline(x:int, y:int, img:int, u:int, v:int, w:int, h:int, col:int, flip_x:bool=False, colkey:int=0):
    for py in range(h):
        for px in range(w):
            sx = u + (w - 1 - px if flip_x else px)
            sy = v + py
            if pyxel.images[img].pget(sx, sy) == colkey: continue
            for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = px + ox, py + oy
                if nx < 0 or ny < 0 or nx >= w or ny >= h: pyxel.pset(x + px + ox, y + py + oy, col)
                else:
                    nsx = u + (w - 1 - nx if flip_x else nx)
                    nsy = v + ny
                    if pyxel.images[img].pget(nsx, nsy) == colkey: pyxel.pset(x + px + ox, y + py + oy, col)

def left(c): return c['sensors']['accel']['y'] < -2 if c else False
def right(c): return c['sensors']['accel']['y'] > 2 if c else False
def jump(c): return c['buttons']['Press'] if c else False
def crouch(c): return c['sensors']['accel']['x'] < -4 if c else False

#? ---------- SAKA CONSTANTS ---------- ?#

COLLISION_TILES = [(0,1),(3,2)]
LEVER_TILES = [(3,1),(4,1)]
PLAYER_POS = [[[16, 24], [264, 160]], [[16, 24], [264, 160]]]
LEVERS_DICT = [
    {(11, 4):[0, (3,2), (4,2), [(8,18),(8,19),(8,20),(27,6),(28,5),(29,5),(16,8),(17,9),(18,10)], 480]},
    {(33, 1):[0, (3,2), (4,2), [(24,8),(24,9),(24,10),(24,11),(24,12),(24,13),(24,14),(24,17),(24,18),(24,19),(24,20),(11,7),(11,8),(11,9),(11,10),(11,11),(11,12),(11,13),(11,14)], 480]}
]
TELEPORTERS = [
    {1:Teleporter(0, 18*8, 8, 24, 16, 20*8, 2, 8), 2:Teleporter(34*8, 8, 8, 24, 32*8, 24, 1)},
    {1:Teleporter(0, 18*8, 8, 24, 16, 20*8, 2, 8), 2:Teleporter(34*8, 9*8, 8, 24, 32*8, 11*8, 1)},
]

#? ---------- GAME MAIN CLASS ---------- ?#

class Game:
    def __init__(self):
        scenes = [
            Scene(0, "Main Menu", self.update_main_menu, self.draw_main_menu, "assets/assets.pyxres", PALETTE),
            Scene(1, "Saka", self.update_saka, self.draw_saka, "assets/assets.pyxres", PALETTE),
            Scene(2, "Pong", self.update_pong, self.draw_pong, "assets/assets.pyxres", PALETTE)
        ]
        self.pyxel_manager = PyxelManager(280, 176, scenes, 0, fullscreen=True)

        # Menu
        self.title = Text("PolyCube", 140, 30, [10, 11, 18, 17], FONT_DEFAULT, 3, CENTER, (VERTICAL, NORMAL_COLOR_MODE, 20), (10, 10, 0.3), outline_color=7)
        self.main_menu_buttons = [
            Button("Saka", 40, 80, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=TOP_LEFT, on_click=self.saka_act),
            Button("Pong", 40, 156, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=BOTTOM_LEFT, on_click=self.pong_act),
            Button("Far West", 240, 80, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=TOP_RIGHT, on_click=lambda:None),
        ]
        self.main_menu_button_manager = ButtonManager(self.main_menu_buttons)

        # Saka
        self.background = MatrixRainBackground(16, 0.5, [21, 22, 23])
        self.particle_manager = ParticleManager()
        self.init_saka()

        # Pong
        self.pong_paddles = [
            PongPaddle('left', 1, 9),   # Rouge
            PongPaddle('right', 2, 11),  # Orange
            PongPaddle('top', 3, 13),    # Vert
            PongPaddle('bottom', 4, 19)  # Bleu
        ]
        self.pong_ball = PongBall()

        self.pyxel_manager.run()

    # --- Actions ---
    def saka_act(self):
        if gpio_manager: gpio_manager.blink_start_sequence()
        self.init_saka()
        self.pyxel_manager.change_scene_transition(TransitonPixelate(1, 2, 8, 6))

    def pong_act(self):
        self.pong_ball.reset()
        for p in self.pong_paddles: p.reset_position()
        self.pyxel_manager.change_scene_transition(TransitonPixelate(2, 2, 8, 6))

    def init_saka(self):
        self.level = random.randint(0, 1)
        t = random.choice([False, True])
        p1_u, p2_u = random.randint(0, 12) * 8, random.randint(0, 12) * 8
        while p2_u == p1_u: p2_u = random.randint(0, 12) * 8
        self.player_1 = Player(*PLAYER_POS[self.level][0], p1_u, self.level, 1, t)
        self.player_2 = Player(*PLAYER_POS[self.level][1], p2_u, self.level, 2, not t)

    # --- Updates & Draws ---
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
        self.particle_manager.update()
        self.background.update()
        if gpio_manager:
            if self.player_1.tagger: gpio_manager.update_controllers({1:True, 2:True})
            else: gpio_manager.update_controllers({3:True, 4:True})
            if gpio_manager.bouton.is_pressed:
                self.pyxel_manager.change_scene_transition(TransitonPixelate(0, 2, 8, 6))

        for tele in TELEPORTERS[self.level].values():
            tele.update([self.player_1, self.player_2], self.level)
            if pyxel.frame_count % 20 == 0:
                for _ in range(3):
                    x, y = tele.x + tele.particle_spawn_off, tele.y + random.randint(2, tele.h - 4)
                    self.particle_manager.add_particle(LineParticle(x, y, random.randint(2,6), [27,28], 60, 0.3, (tele.x_spawn, y)))

        for lever, info in LEVERS_DICT[self.level].items():
            info[0] = max(0, info[0] - 1)
            if info[0] == 1:
                u, v = pyxel.tilemaps[self.level].pget(*lever)
                pyxel.tilemaps[self.level].pset(*lever, (u-1, v))
                for tx, ty in info[3]:
                    curr = pyxel.tilemaps[self.level].pget(tx, ty)
                    pyxel.tilemaps[self.level].pset(tx, ty, info[2] if curr == info[1] else info[1])

    def draw_saka(self):
        pyxel.cls(0)
        self.background.draw()
        self.player_1.draw()
        self.player_2.draw()
        pyxel.bltm(0, 0, self.level, 0, 0, 280, 176, 0)
        self.particle_manager.draw()

    def update_pong(self):
        for p in self.pong_paddles: p.update()
        self.pong_ball.update(self.pong_paddles)
        if gpio_manager and gpio_manager.bouton.is_pressed:
            self.pyxel_manager.change_scene_transition(TransitonPixelate(0, 2, 8, 6))

    def draw_pong(self):
        pyxel.cls(0)
        # Décoration terrain
        for i in range(0, 176, 12): pyxel.line(140, i, 140, i+6, 24)
        for i in range(0, 280, 12): pyxel.line(i, 88, i+6, 88, 24)
        for p in self.pong_paddles: p.draw()
        self.pong_ball.draw()

if __name__ == "__main__":
    Game()