"""
@author : Léo Imbert
@created : 13/03/2026
@updated : 10/04/2026
"""

#? ---------- CHARGEMENT GPIO ---------- ?#

from rasp.gpios import gpio_manager
gpio_manager.startup_sequence()

#? ---------- CHARGEMENT DU SERVEUR ---------- ?#

import server
import threading

def run_server():
    server.start_server()
threading.Thread(target=run_server, daemon=True).start()

#? ---------- IMPORTATIONS ---------- ?#

from utils import *
import threading
import server

#? ---------- CONSTANTS ---------- ?#

PALETTE = [0x000000, 0xbe4a2f, 0xd77643, 0xead4aa, 0xe4a672, 0xb86f50, 0x733e39, 0x3e2731, 
           0xa22633, 0xe43b44, 0xf77622, 0xfeae34, 0xfee761, 0x63c74d, 0x3e8948, 0x265c42, 
           0x193c3e, 0x124e89, 0x0099db, 0x2ce8f5, 0xffffff, 0xc0cbdc, 0x8b9bb4, 0x5a6988, 
           0x3a4466, 0x262b44, 0xff0044, 0x68386c, 0xb55088, 0xf6757a, 0xe8b796, 0xc28569, 0x000000]

#? ---------- CLASSES ---------- ?#

class ButtonManager:

    def __init__(self, buttons:list[Button]):
        self.buttons = buttons
        self.selected_index = 0
        self.last_move_time = 0
        self.move_cooldown = 45

    def update(self):
        p1_id, p1_data = get_player_data("PLAYER-1")

        if not p1_data or not self.buttons:
            return

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
            if button.on_click:
                button.on_click()

    def draw(self, camera_x:int=0, camera_y:int=0):
        for i, button in enumerate(self.buttons):
            button.draw((i == self.selected_index), camera_x=camera_x, camera_y=camera_y)

class Player:

    def __init__(self, x:int, y:int, u:int, level:int, player_number:int, tagger:bool):
        self.x, self.y = x, y
        self.w, self.h = 8, 8

        #? Others
        self.player_number = player_number
        self.tagger = tagger
        self.tagged_timer = 0

        self.u = u
        self.controls = None
        self.level = level

        #? Velocity
        self.velocity_x = 0
        self.vx_r = 0
        self.velocity_y = 0
        self.max_velocity_y = 6
        self.gravity = 0.4
        self.friction = 0.8

        #? Movement
        self.speed = 1.4

        #? Jump
        self.coyote_timer = 0
        self.coyote_time = 6
        self.jump_buffer_timer = 0
        self.jump_buffer_time = 12
        self.jump_power = 5.5
        self.jumping = False

        #? Flares
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
            if not self.jumping:
                self.velocity_y = 0
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
        id, self.controls = get_player_data(f"PLAYER-{self.player_number}")
        self._handle_timers()
        self._handle_physics()

        if collision_rect_rect(self.x, self.y, self.w, self.h, other.x, other.y, other.w, other.h) and self.tagger and other.tagged_timer == 0:
            self.tagged_timer = 60
            self.tagger = False
            other.tagger = True
            vibrate_controller(id)
            gpio_manager.red_start_sequence()

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
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.particle_spawn_off = particle_spawn_off
        self.x_spawn, self.y_spawn = x_spawn, y_spawn
        self.teleporter_id = teleporter_id

    def update(self, players:list, level:int):
        for player in players:
            if collision_rect_rect(player.x, player.y, player.w, player.h, self.x, self.y, self.w, self.h):
                nx, ny = TELEPORTERS[level][self.teleporter_id].x_spawn, TELEPORTERS[level][self.teleporter_id].y_spawn
                player.x = nx
                player.y = ny

#? ---------- FUNCTIONS ---------- ?#

def vibrate_controller(ctrl_id, duration=50):
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

def get_player_data(player_name:str):
    controllers = server.controllers.copy()
    if not controllers:
        return None, None
        
    p_id = next((cid for cid in controllers if player_name in cid), None)
    if p_id:
        return p_id, controllers[p_id]
    return None, None

def collision_rect_tiles(x:int, y:int, w:int, h:int, tiles:list, tilemaps:int|list=0)-> bool:
    start_tile_x = x // 8
    start_tile_y = y // 8
    end_tile_x = (x + w - 1) // 8
    end_tile_y = (y + h - 1) // 8

    tilemaps = [tilemaps] if isinstance(tilemaps, int) else tilemaps
    tilemap_w, tilemap_h = pyxel.tilemaps[tilemaps[0]].width, pyxel.tilemaps[tilemaps[0]].height

    start_tile_x = int(clamp(start_tile_x, 0, tilemap_w - 1))
    start_tile_y = int(clamp(start_tile_y, 0, tilemap_h - 1))
    end_tile_x = int(clamp(end_tile_x, 0, tilemap_w - 1))
    end_tile_y = int(clamp(end_tile_y, 0, tilemap_h - 1))


    for tile_y in range(start_tile_y, end_tile_y + 1):
        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tilemap_id in tilemaps:
                tile_id = pyxel.tilemaps[tilemap_id].pget(tile_x, tile_y)

                if tile_id in tiles:
                    return True
    
    return False
    
def tiles_in_rect(x:int, y:int, w:int, h:int, tiles:list, tilemaps:int|list=0)-> list:
    result = []

    start_tile_x = x // 8
    start_tile_y = y // 8
    end_tile_x = (x + w - 1) // 8
    end_tile_y = (y + h - 1) // 8

    tilemaps = [tilemaps] if isinstance(tilemaps, int) else tilemaps
    tilemap_w, tilemap_h = pyxel.tilemaps[tilemaps[0]].width, pyxel.tilemaps[tilemaps[0]].height

    start_tile_x = int(clamp(start_tile_x, 0, tilemap_w - 1))
    start_tile_y = int(clamp(start_tile_y, 0, tilemap_h - 1))
    end_tile_x = int(clamp(end_tile_x, 0, tilemap_w - 1))
    end_tile_y = int(clamp(end_tile_y, 0, tilemap_h - 1))


    for tile_y in range(start_tile_y, end_tile_y + 1):
        for tile_x in range(start_tile_x, end_tile_x + 1):
            for tilemap_id in tilemaps:
                tile_id = pyxel.tilemaps[tilemap_id].pget(tile_x, tile_y)

                if tile_id in tiles:
                    result.append((tile_x, tile_y))

    return result

def blt_outline(x:int, y:int, img:int, u:int, v:int, w:int, h:int, col:int, flip_x:bool=False, colkey:int=0):
    for py in range(h):
        for px in range(w):
            sx = u + (w - 1 - px if flip_x else px)
            sy = v + py

            c = pyxel.images[img].pget(sx, sy)
            if c == colkey:
                continue

            for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = px + ox, py + oy

                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    pyxel.pset(x + px + ox, y + py + oy, col)
                else:
                    nsx = u + (w - 1 - nx if flip_x else nx)
                    nsy = v + ny
                    nc = pyxel.images[img].pget(nsx, nsy)
                    if nc == colkey:
                        pyxel.pset(x + px + ox, y + py + oy, col)

def left(controls:int)-> bool:
    return controls['sensors']['accel']['y'] < -2

def right(controls:int)-> bool:
    return controls['sensors']['accel']['y'] > 2

def jump(controls:int)-> bool:
    return controls['buttons']['Press']

def crouch(controls:int)-> bool:
    return controls['sensors']['accel']['x'] < -4

def get_terrain(x:int, t1:float, h1:float, t2:float, h2:float)-> float:
    return math.cos(x * t1) * h1 + math.sin(x * t2) * h2

#? ---------- SAKA CONSTANTS ---------- ?#

COLLISION_TILES = [(0,1),(3,2)]
LEVER_TILES = [(3,1),(4,1)]

PLAYER_POS = [
    [[16, 24], [264, 160]],
    [[16, 24], [264, 160]],
]

LEVERS_DICT = [
    #? Tile Coord : Timer, Block tile, Hollow tile, Block coords, Timer duration
    {(11, 4):[0, (3,2), (4,2), [(8,18),(8,19),(8,20),(27,6),(28,5),(29,5),(16,8),(17,9),(18,10)], 300]},
    {(33, 1):[0, (3,2), (4,2), [(24,8),(24,9),(24,10),(24,11),(24,12),(24,13),(24,14),(24,17),(24,18),(24,19),(24,20),(11,7),(11,8),(11,9),(11,10),(11,11),(11,12),(11,13),(11,14)], 300]}
]

TELEPORTERS = [
    {1:Teleporter(0, 18*8, 8, 24, 16, 20*8, 2, 8), 2:Teleporter(34*8, 8, 8, 24, 32*8, 24, 1)},
    {1:Teleporter(0, 18*8, 8, 24, 16, 20*8, 2, 8), 2:Teleporter(34*8, 9*8, 8, 24, 32*8, 11*8, 1)},
]

#? ---------- GAME ---------- ?#

class Game:

    def __init__(self):
        #? Pyxel Init
        scenes = [
            Scene(0, "PolyCube - Main Menu", self.update_main_menu, self.draw_main_menu, "assets/assets.pyxres", PALETTE),
            Scene(1, "Polycube - Saka", self.update_saka, self.draw_saka, "assets/assets.pyxres", PALETTE),
            Scene(2, "Polycube - Far west", self.update_west, self.draw_west, "assets/assets.pyxres", PALETTE)
        ]
        self.pyxel_manager = PyxelManager(280, 176, scenes, 0, fullscreen=True)

        #? Main Menu Variables
        self.title = Text("PolyCube", 140, 30, [10, 11, 18, 17], FONT_DEFAULT, 3, CENTER, (VERTICAL, NORMAL_COLOR_MODE, 20), (10, 10, 0.3), outline_color=7)
        self.main_background = StarBackground(200, stars_color=20)
        self.main_menu_buttons = [
            Button("Saka", 40, 80, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=TOP_LEFT, on_click=self.saka_act),
            Button("Pong", 40, 156, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=BOTTOM_LEFT),
            Button("Far West", 240, 80, 18, 10, 17, 11, FONT_DEFAULT, 2, anchor=TOP_RIGHT, on_click=self.west_act),
        ]
        self.main_menu_button_manager = ButtonManager(self.main_menu_buttons)

        #? Saka Variables
        self.saka_background = MatrixRainBackground(16, 0.5, [21, 22, 23])
        self.particle_manager = ParticleManager()
        self.saka_play_timer = CountdownTimer(60)

        #? West Variables
        self.plant = [-10, random.randint(140, 170)]

        #? Run
        self.pyxel_manager.run()

    def saka_act(self):
        if server.occupied_slots[1] and server.occupied_slots[2]:
            if gpio_manager: gpio_manager.blink_start_sequence()
            self.init_saka()
            self.pyxel_manager.change_scene_transition(TransitonPixelate(1, 2, 8, 18, action=lambda : self.saka_play_timer.restart()))
        elif gpio_manager:
            gpio_manager.red_start_sequence()

    def init_saka(self):
        self.level = random.randint(0, 1)
        t = random.choice([False, True])
        p1_u = random.randint(0, 12) * 8
        p2_u = random.randint(0, 12) * 8
        while p2_u == p1_u:
            p2_u = random.randint(0, 12) * 8
        self.player_1 = Player(*PLAYER_POS[self.level][0], p1_u, self.level, 1, t)
        self.player_2 = Player(*PLAYER_POS[self.level][1], p2_u, self.level, 2, not t)

    def west_act(self):
        if gpio_manager: gpio_manager.blink_start_sequence()
        self.init_west()
        self.pyxel_manager.change_scene_transition(TransitonPixelate(2, 2, 8, 18))

    def init_west(self):
        pass

    def update_main_menu(self):
        self.title.update()
        self.main_background.update()
        self.main_menu_button_manager.update()
        if gpio_manager and pyxel.frame_count % 30 == 0:
            gpio_manager.update_controllers(server.occupied_slots)

        try:
            gpio_manager.bouton.when_pressed = None
        except:
            pass

    def draw_main_menu(self):
        pyxel.cls(0)
        self.main_background.draw()

        self.title.draw()
        self.main_menu_button_manager.draw()

    def update_saka(self):
        if self.saka_play_timer.get_timer() > 0:
            self.player_1.update(self.player_2)
            self.player_2.update(self.player_1)
        self.particle_manager.update()
        self.saka_background.update()

        #? Polycube LEDS
        if self.player_1.tagger:
            gpio_manager.update_controllers({1:True, 2:True})
        else:
            gpio_manager.update_controllers({3:True, 4:True})

        #? Polycube Button
        try:
            gpio_manager.bouton.when_pressed = lambda : self.pyxel_manager.change_scene_transition(TransitonPixelate(0, 2, 8, 6))
        except:
            pass

        #? Teleporters
        for teleporter in TELEPORTERS[self.level].values():
            teleporter.update([self.player_1, self.player_2], self.level)
            if pyxel.frame_count % 20 ==0:
                for _ in range(5):
                    x = teleporter.x + teleporter.particle_spawn_off
                    y = teleporter.y + random.randint(2, teleporter.h - 4)
                    l = random.randint(2, 6)
                    c = [random.choice([27, 28]) for _ in range(5)]
                    s = random.uniform(0.2, 0.4)
                    tx, ty = teleporter.x_spawn, y + random.randint(-5, 5)
                    self.particle_manager.add_particle(LineParticle(x, y, l, c, 60, s, (tx, ty), dither_duration=10))

        #? Levers
        for lever, lever_info in LEVERS_DICT[self.level].items():
            t = max(0, lever_info[0] - 1)
            LEVERS_DICT[self.level][lever][0] = t

            if t == 1:
                u, v = pyxel.tilemaps[self.level].pget(*lever)
                pyxel.tilemaps[self.level].pset(*lever, (u - 1, v))
                for tx, ty in lever_info[3]:
                    if pyxel.tilemaps[self.level].pget(tx, ty) == lever_info[1]:
                        pyxel.tilemaps[self.level].pset(tx, ty, lever_info[2])
                    else:
                        pyxel.tilemaps[self.level].pset(tx, ty, lever_info[1])

        #? End Timer
        if self.saka_play_timer.get_timer() == 0:
            self.pyxel_manager.shake_camera(4, 0.1)
            for _ in range(20):
                x = self.player_1.x + 4 if self.player_1.tagger else self.player_2.x + 4
                y = self.player_1.y + 4 if self.player_1.tagger else self.player_2.y + 4
                w = random.randint(1, 10)
                s = random.uniform(0.2, 0.5)
                tx, ty = x + random.randint(-4, 4), y + random.randint(-4, 4)
                self.particle_manager.add_particle(OvalParticle(x, y, w, w, [25, 9, 10, 11, 12], 100, s, (tx, ty), dither_duration=10))
        elif self.saka_play_timer.get_timer() < -120:
            _, p1_data = get_player_data("PLAYER-1")
            if p1_data and p1_data['buttons']['Press']:
                self.saka_act()

    def draw_saka(self):
        pyxel.cls(0)
        self.saka_background.draw()

        self.player_1.draw()
        self.player_2.draw()
        pyxel.bltm(0, 0, self.level, 0, 0, 280, 176, 0)
        self.particle_manager.draw()
        if self.saka_play_timer.get_timer() >= 0:
            self.saka_play_timer.draw(140, 5, 20, 1, TOP)

    def update_west(self):
        #? Polycube Button
        try:
            gpio_manager.bouton.when_pressed = lambda : self.pyxel_manager.change_scene_transition(TransitonPixelate(0, 2, 8, 6))
        except:
            pass

        #? Tumble
        self.plant = self.plant[0] + random.uniform(0.5, 2), wave_motion(self.plant[1], 1, 1, pyxel.frame_count)
        if self.plant[0] > pyxel.width + 10 and random.random() < 0.02:
            self.plant = [-10, random.randint(140, 170)]

    def draw_west(self):
        pyxel.cls(0)

        #? Terrain
        for x in range(0, pyxel.width + 1):
            pyxel.pset(x, 80 + get_terrain(x, 0.04, 2, 0.08, 4), 1)
            pyxel.pset(x, 150 + get_terrain(x, 0.02, 4, 0.05, 3), 2)
            if x % 30 < 10:
                pyxel.pset(x, 160 + get_terrain(x, 0.01, 4, 0.03, 5), 1)
        pyxel.fill(0, 105, 1)
        pyxel.fill(0, 155, 2)
        pyxel.fill(0, 0, 18)

        #? Sun
        draw_moving_spiral(20, 20, 20, 11, pyxel.frame_count, 4, 25, 0.005)
        pyxel.circ(20, 20, 8, 11)

        #? Tumble
        draw_moving_spiral(*self.plant, 10, 6, pyxel.frame_count, 4, 100, 0.1)

#? ---------- MAIN ---------- ?#

if __name__ == "__main__":
    Game()