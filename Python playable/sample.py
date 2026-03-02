import pygame

def run_game(screen, controllers):
    """Cette fonction est appelée par le launcher"""
    running = True
    clock = pygame.time.Clock()
    
    while running:
        screen.fill((0, 0, 0))
        # Quitter le jeu et revenir au menu avec le bouton PAUSE de n'importe quel joueur
        for ctrl_id, data in controllers.items():
            if data['buttons']['Pause']:
                running = False
        
        # Logique du jeu...
        # Utilise 'controllers' pour faire bouger tes objets
        
        pygame.display.flip()
        clock.tick(60)
        
        # Important : gérer les events Pygame pour ne pas freezer
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

