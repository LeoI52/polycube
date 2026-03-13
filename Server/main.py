import threading
import pyxel
import sys
import os
import importlib.util
import server  # Ton serveur Socket.IO reste inchangé

# 1. LANCEMENT DU SERVEUR
server_thread = threading.Thread(target=server.start_server, daemon=True)
server_thread.start()

# 2. CONFIGURATION
GAMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Python playable"))
WIDTH, HEIGHT = 200, 150  # Pyxel utilise souvent des résolutions plus petites (Retro)

class PolycubeLauncher:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Polycube OS")
        
        self.selected_index = 0
        self.games = self.get_game_list()
        self.last_move_frame = 0
        self.status_msg = ""
        
        pyxel.run(self.update, self.draw)

    def get_game_list(self):
        if not os.path.exists(GAMES_DIR):
            return []
        return [f for f in os.listdir(GAMES_DIR) if f.endswith('.py') and f != "__init__.py"]

    def vibrate_controller(self, ctrl_id, duration=50):
        controller_data = server.controllers.get(ctrl_id)
        if controller_data and 'sid' in controller_data:
            server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

    def launch_game(self, filename):
        """Charge et exécute le module Pyxel externe"""
        path = os.path.join(GAMES_DIR, filename)
        spec = importlib.util.spec_from_file_location("game_module", path)
        game_module = importlib.util.module_from_spec(spec)
        
        try:
            # Note : Pyxel est restrictif sur le fait de relancer pyxel.init()
            # Le jeu chargé doit idéalement utiliser le pyxel.run existant ou être un script autonome.
            spec.loader.exec_module(game_module)
            if hasattr(game_module, 'run_game'):
                game_module.run_game(server.controllers)
        except Exception as e:
            self.status_msg = f"ERR: {str(e)[:20]}"
            print(f"CRASH : {e}")

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.games = self.get_game_list()
        active_controllers = server.controllers.copy()
        
        if active_controllers:
            # Récupération du premier joueur
            p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
            p1_data = active_controllers[p1_id]
            
            accel_x = p1_data['sensors']['accel']['x']
            btn_h = p1_data['buttons']['H']
            
            # Navigation (seuil de frames pour éviter le défilement trop rapide)
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
                self.launch_game(self.games[self.selected_index])

    def draw(self):
        pyxel.cls(1) # Bleu foncé (Slate)
        
        # Titre
        pyxel.text(WIDTH//2 - 30, 20, "POLYCUBE SYSTEM", 12) # 12 = Light Blue
        
        if not self.games:
            pyxel.text(WIDTH//2 - 35, HEIGHT//2, "AUCUN JEU TROUVE", 8) # 8 = Rouge
        else:
            for i, game_name in enumerate(self.games):
                color = 7 if i == self.selected_index else 13 # 7 = Blanc, 13 = Gris
                y_pos = 50 + (i * 10)
                prefix = "> " if i == self.selected_index else "  "
                pyxel.text(WIDTH//2 - 40, y_pos, f"{prefix}{game_name.replace('.py', '')}", color)

        # Status Barre
        p1_connected = any("JOUEUR-1" in id for id in server.controllers)
        status_color = 11 if p1_connected else 8 # 11 = Vert, 8 = Rouge
        status_text = "MANETTE OK" if p1_connected else "MANETTE DECONNECTEE"
        
        pyxel.rect(0, HEIGHT - 15, WIDTH, 15, 0)
        pyxel.text(5, HEIGHT - 10, status_text, status_color)
        if self.status_msg:
            pyxel.text(100, HEIGHT - 10, self.status_msg, 8)

if __name__ == '__main__':
    PolycubeLauncher()