import threading
import pygame
import sys
import os
import importlib.util
import server # Importe notre serveur Socket.IO

# 1. LANCEMENT DU SERVEUR DANS UN THREAD
server_thread = threading.Thread(target=server.start_server, daemon=True)
server_thread.start()

# 2. CONFIGURATION ET CHEMINS
GAMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Python playable"))

# Initialisation Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Polycube OS - Game Launcher")
clock = pygame.time.Clock()

# Couleurs
BG_COLOR = (15, 23, 42)
PRIMARY = (56, 189, 248)
WHITE = (241, 245, 249)
GRAY = (71, 85, 105)
ERROR_RED = (239, 68, 68)

def get_game_list():
    """Liste tous les fichiers .py dans le dossier Python playable"""
    if not os.path.exists(GAMES_DIR):
        return []
    return [f for f in os.listdir(GAMES_DIR) if f.endswith('.py') and f != "__init__.py"]

def draw_text(text, x, y, color=WHITE, size=30, center=False):
    font = pygame.font.SysFont("Consolas", size, bold=True)
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def vibrate_controller(ctrl_id, duration=50):
    """Envoie une commande de vibration à une manette spécifique."""
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

def launch_game(filename):
    """Charge et exécute dynamiquement un script Python avec gestion d'erreurs (Point 3)"""
    path = os.path.join(GAMES_DIR, filename)
    spec = importlib.util.spec_from_file_location("game_module", path)
    game_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(game_module)
        if hasattr(game_module, 'run_game'):
            print(f"Lancement de {filename}...")
            # On passe l'écran et le dictionnaire partagé des contrôleurs
            game_module.run_game(screen, server.controllers)
        else:
            print(f"Erreur : Pas de fonction 'run_game' dans {filename}")
    except Exception as e:
        print(f"CRASH DU JEU [{filename}] : {e}")
        # Affichage de l'erreur sur l'écran avant de revenir au menu
        screen.fill(BG_COLOR)
        draw_text("GAME CRASHED !", WIDTH//2, HEIGHT//2 - 20, ERROR_RED, 40, center=True)
        draw_text(str(e), WIDTH//2, HEIGHT//2 + 40, WHITE, 18, center=True)
        pygame.display.flip()
        pygame.time.wait(3000)
    finally:
        # On s'assure que le mode d'affichage est bien réinitialisé pour le launcher
        pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Polycube OS - Game Launcher")

def main_menu():
    selected_index = 0
    last_move_time = 0
    
    while True:
        games = get_game_list()
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        active_controllers = server.controllers.copy()
        p1_id = None
        
        if active_controllers:
            p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
            p1_data = active_controllers[p1_id]
            
            accel_x = p1_data['sensors']['accel']['x']
            btn_h = p1_data['buttons']['H']
            
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > 300:
                if accel_x > 4 or accel_x < -4:
                    vibrate_controller(p1_id, 30)
                    if accel_x > 4: selected_index = (selected_index + 1) % len(games) if games else 0
                    elif accel_x < -4: selected_index = (selected_index - 1) % len(games) if games else 0
                    last_move_time = current_time
            
            if btn_h and games:
                vibrate_controller(p1_id, 100)
                launch_game(games[selected_index])

        # Affichage UI
        draw_text("POLYCUBE SYSTEM", WIDTH//2, 80, PRIMARY, 50, center=True)
        if not games:
            draw_text("AUCUN JEU TROUVÉ", WIDTH//2, HEIGHT//2, ERROR_RED, 24, center=True)
        else:
            for i, game_name in enumerate(games):
                color = WHITE if i == selected_index else GRAY
                prefix = "> " if i == selected_index else "  "
                draw_text(f"{prefix}{game_name.replace('.py', '')}", WIDTH//2, 250 + (i * 50), color, 35, center=True)

        status_color = (74, 222, 128) if p1_id else ERROR_RED
        draw_text(f"MANETTE: {p1_id if p1_id else 'DÉCONNECTÉE'}", WIDTH//2, HEIGHT - 50, status_color, 18, center=True)

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main_menu()