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
# On cible le dossier des jeux
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
    """
    Envoie une commande de vibration à une manette spécifique.
    Le serveur doit stocker le SID (session ID) pour cibler le bon appareil.
    """
    # On récupère les données de la manette pour trouver son SID
    controller_data = server.controllers.get(ctrl_id)
    if controller_data and 'sid' in controller_data:
        # On utilise socketio.emit vers la 'room' qui correspond au SID de l'appareil
        server.socketio.emit('vibrate', {'duration': duration}, room=controller_data['sid'])

def launch_game(filename):
    """Charge et exécute dynamiquement un script Python"""
    path = os.path.join(GAMES_DIR, filename)
    spec = importlib.util.spec_from_file_location("module.name", path)
    game_module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(game_module)
        # On suppose que chaque jeu a une fonction 'run_game(screen, controllers_dict)'
        # On peut aussi passer la fonction de vibration au jeu
        if hasattr(game_module, 'run_game'):
            print(f"Lancement de {filename}...")
            game_module.run_game(screen, server.controllers)
        else:
            print(f"Erreur : Le fichier {filename} n'a pas de fonction 'run_game'")
    except Exception as e:
        print(f"Erreur lors de l'exécution du jeu : {e}")

def main_menu():
    selected_index = 0
    games = get_game_list()
    last_move_time = 0
    
    print("Launcher démarré. En attente de manettes...")

    while True:
        screen.fill(BG_COLOR)
        
        # 1. Gestion des événements système
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 2. Récupération des données du Joueur 1 pour le menu
        active_controllers = server.controllers.copy()
        p1_id = None
        
        if active_controllers:
            # On cherche d'abord JOUEUR-1, sinon on prend le premier trouvé
            p1_id = next((id for id in active_controllers if "JOUEUR-1" in id), list(active_controllers.keys())[0])
            p1_data = active_controllers[p1_id]
            
            accel_x = p1_data['sensors']['accel']['x']
            btn_h = p1_data['buttons']['H']
            
            # Navigation avec l'inclinaison (Accel X)
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > 300: # Délai pour ne pas défiler trop vite
                if accel_x > 4 or accel_x < -4:
                    # Vibration courte lors du changement de sélection
                    vibrate_controller(p1_id, 30)
                    
                    if accel_x > 4: # Penché vers l'avant
                        selected_index = (selected_index + 1) % len(games) if games else 0
                    elif accel_x < -4: # Penché vers l'arrière
                        selected_index = (selected_index - 1) % len(games) if games else 0
                    last_move_time = current_time
            
            # Validation avec le bouton H
            if btn_h and games:
                # Vibration plus longue pour confirmer la sélection
                vibrate_controller(p1_id, 100)
                launch_game(games[selected_index])
                # Une fois le jeu terminé, on revient ici, donc on rafraîchit la liste
                games = get_game_list()

        # 3. Affichage du Menu
        draw_text("POLYCUBE SYSTEM", WIDTH//2, 80, PRIMARY, 50, center=True)
        draw_text("--- SELECT GAME ---", WIDTH//2, 150, GRAY, 20, center=True)

        if not games:
            draw_text("AUCUN JEU TROUVÉ DANS 'Python playable'", WIDTH//2, HEIGHT//2, (200, 50, 50), 24, center=True)
        else:
            for i, game_name in enumerate(games):
                color = WHITE if i == selected_index else GRAY
                prefix = "> " if i == selected_index else "  "
                draw_text(f"{prefix}{game_name.replace('.py', '')}", WIDTH//2, 250 + (i * 50), color, 35, center=True)

        # Footer status
        status_color = (74, 222, 128) if p1_id else (248, 113, 113)
        status_text = f"MANETTE: {p1_id if p1_id else 'DÉCONNECTÉE'}"
        draw_text(status_text, WIDTH//2, HEIGHT - 50, status_color, 18, center=True)

        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main_menu()