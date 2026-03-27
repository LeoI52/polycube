import threading
import pyxel
import server

server_thread = threading.Thread(target=server.start_server, daemon=True)
server_thread.start()

WIDTH, HEIGHT = 228, 128

class PolycubeLauncher:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Polycube OS")
        
        self.selected_index = 0
        self.last_move_frame = 0
        self.status_msg = ""
        self.games = ["main", "test"]
        
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        active_controllers = server.controllers.copy()
        
        if active_controllers:
            p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
            p1_data = active_controllers[p1_id]
            
            accel_x = p1_data['sensors']['accel']['x']
            btn_h = p1_data['buttons']['H']
            
            if pyxel.frame_count - self.last_move_frame > 10:
                if accel_x > 4:
                    self.vibrate_controller(p1_id, 30)
                    self.selected_index = (self.selected_index + 1) % len(self.games) if self.games else 0
                    self.last_move_frame = pyxel.frame_count
                elif accel_x < -4:
                    self.vibrate_controller(p1_id, 30)
                    self.selected_index = (self.selected_index - 1) % len(self.games) if self.games else 0
                    self.last_move_frame = pyxel.frame_count
            
            if btn_h and self.games:
                self.vibrate_controller(p1_id, 100)

    def draw(self):
        pyxel.cls(1)
        
        pyxel.text(WIDTH//2 - 30, 20, "POLYCUBE SYSTEM", 12)

        p1_connected = any("JOUEUR-1" in id for id in server.controllers)
        status_color = 11 if p1_connected else 8
        status_text = "MANETTE OK" if p1_connected else "MANETTE DECONNECTEE"
        
        pyxel.rect(0, HEIGHT - 15, WIDTH, 15, 0)
        pyxel.text(5, HEIGHT - 10, status_text, status_color)
        if self.status_msg:
            pyxel.text(100, HEIGHT - 10, self.status_msg, 8)

if __name__ == '__main__':
    PolycubeLauncher()