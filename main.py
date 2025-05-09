import pygame
import numpy as np
from interface import Interface
from game import Game
import multiprocessing
import threading
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Dimensions de la fenêtre
WIDTH, HEIGHT = 1000, 700

def afficher_barre_chargement(screen, progression, texte="Attente du tour adverse..."):
    """Affiche une barre de chargement animée"""
    largeur, hauteur = screen.get_size()
    barre_largeur = largeur * 0.6
    barre_hauteur = 30
    barre_x = (largeur - barre_largeur) // 2
    barre_y = hauteur * 0.7
    
    pygame.draw.rect(screen, (50, 50, 80), (barre_x, barre_y, barre_largeur, barre_hauteur))
    pygame.draw.rect(screen, (100, 200, 100), (barre_x, barre_y, int(barre_largeur * progression), barre_hauteur))
    pygame.draw.rect(screen, (200, 200, 200), (barre_x, barre_y, barre_largeur, barre_hauteur), 2)
    
    font = pygame.font.Font(None, 32)
    texte_surf = font.render(texte, True, (240, 240, 240))
    screen.blit(texte_surf, texte_surf.get_rect(center=(largeur//2, 505)))

def draw_menu(screen):
    """Affiche le menu principal avec sélection de difficulté"""
    screen.fill((211, 211, 211))
    font = pygame.font.Font(None, 74)
    
    # Titre
    title = font.render('Schotten Totten', True, (0, 0, 0))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    # Sous-titre
    subtitle_font = pygame.font.Font(None, 40)
    subtitle = subtitle_font.render('Choisissez la difficulté :', True, (0, 0, 0))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))
    
    # Boutons
    button_font = pygame.font.Font(None, 50)
    buttons = [
        {"rect": pygame.Rect(WIDTH//2-150, 220, 300, 80), "text": "Facile", "color": (50, 200, 50)},
        {"rect": pygame.Rect(WIDTH//2-150, 320, 300, 80), "text": "Moyen", "color": (200, 200, 50)},
        {"rect": pygame.Rect(WIDTH//2-150, 420, 300, 80), "text": "Difficile", "color": (200, 50, 50)},
        {"rect": pygame.Rect(WIDTH//2-150, 520, 300, 80), "text": "Aide", "color": (70, 70, 200)}
    ]
    
    for btn in buttons:
        pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=15)
        text = button_font.render(btn["text"], True, (255, 255, 255))
        screen.blit(text, (btn["rect"].x + (btn["rect"].width - text.get_width())//2,
                          btn["rect"].y + (btn["rect"].height - text.get_height())//2))
    
    return buttons

def jouer_coup_ia(game):
    """Fonction exécutée dans un thread pour le coup de l'IA"""
    try:
        if game.difficulty == "facile":
            return game.strat_k(game.ai, k=10)
        elif game.difficulty == "moyen":
            return game.strat_k(game.ai, k=1)
        else:
            coup_rais = game.k_coup_raisonnable(game.ai, k=3)
            if not coup_rais:
                return False

            with multiprocessing.Pool() as pool:
                results = pool.starmap(
                    game.simulation,
                    [(coup, 300, 1) for coup in coup_rais]
                )
            
            best_idx = np.argmax(results)
            borne_idx, carte_idx = coup_rais[best_idx]
            carte = game.ai.main[carte_idx]
            game.board.ajouter_carte(game.ai.num, borne_idx, (carte['num'], carte['couleur']))
            game.ai.retire_carte(carte)
            
            new_card = game.board.piocher_carte()
            if new_card:
                game.ai.ajoute_carte(new_card)
            return True
    except Exception as e:
        print(f"Erreur dans jouer_coup_ia: {e}")
        return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Schotten Totten")
    
    # Menu principal
    ai_difficulty = "difficile"
    in_menu = True
    while in_menu:
        buttons = draw_menu(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["text"] == "Facile":
                            ai_difficulty = "facile"
                            in_menu = False
                        elif btn["text"] == "Moyen":
                            ai_difficulty = "moyen"
                            in_menu = False
                        elif btn["text"] == "Difficile":
                            ai_difficulty = "difficile"
                            in_menu = False
                        elif btn["text"] == "Aide":
                            rules = [
                                "Règles du jeu :",
                                "- Placez des cartes sur les bornes (1-9)",
                                "- 3 cartes par borne pour la revendiquer",
                                "- 5 bornes ou 3 consécutives pour gagner!",
                                "- Combinaisons :",
                                "  Suite Couleur > Brelan > Couleur > Suite > Somme",
                                "- Cliquez-glissez pour jouer vos cartes"
                            ]
                            Interface(screen).show_text_popup('\n'.join(rules), (50, 100), (900, 300))
    
    # Initialisation du jeu
    game = Game(ai_difficulty)
    game.start()
    ui = Interface(screen)
    clock = pygame.time.Clock()
    running = True
    ai_played = True
    ai_thread = None
    chargement_start = 0
    moved = False

    # Boucle principale
    while running:
        ui.draw_board(game.player, game.ai, game.board)
        
        # Vérification fin de partie
        if game.player.a_gagner() or game.ai.a_gagner():
            player_won = game.player.a_gagner()
            action = ui.show_endgame_popup(screen, player_won)
            
            if action == "menu":
                # Retour au menu
                in_menu = True
                while in_menu:
                    buttons = draw_menu(screen)
                    pygame.display.flip()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            in_menu = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            for btn in buttons:
                                if btn["rect"].collidepoint(mouse_pos):
                                    if btn["text"] == "Facile":
                                        ai_difficulty = "facile"
                                        in_menu = False
                                    elif btn["text"] == "Moyen":
                                        ai_difficulty = "moyen"
                                        in_menu = False
                                    elif btn["text"] == "Difficile":
                                        ai_difficulty = "difficile"
                                        in_menu = False
                                    elif btn["text"] == "Aide":
                                        rules = [
                                            "Règles du jeu :",
                                            "- Placez des cartes sur les bornes (1-9)",
                                            "- 3 cartes par borne pour la revendiquer",
                                            "- 5 bornes ou 3 consécutives pour gagner!",
                                            "- Combinaisons :",
                                            "  Suite Couleur > Brelan > Couleur > Suite > Somme",
                                            "- Cliquez-glissez pour jouer vos cartes"
                                        ]
                                        ui.show_text_popup('\n'.join(rules), (50, 100), (900, 300))
                
                # Réinitialisation du jeu
                game = Game(ai_difficulty)
                game.start()
                
            elif action == "restart":
                # Nouvelle partie même difficulté
                game = Game(ai_difficulty)
                game.start()
                
            elif action == "quit":
                running = False
            
            continue  # Passe au tour suivant

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if ai_played:
                no_full0 = game.board.checkwin(game.player.num)
                for (num_b, num_j) in game.board.borne_won:
                    if num_j == 0:
                        if num_b not in game.player.won:
                            game.player.ajoute_flag(num_b)
                            for (num, val) in no_full0:
                                if num == num_b:
                                    ui.justif(num, val)

                moved, borne_idx, color = ui.drag_drop(event, game.player, game.board)

            if moved:
                ai_played = False
                moved = False
                chargement_start = time.time()

                new_card = game.board.piocher_carte()
                if new_card:
                    game.player.ajoute_carte(new_card)

                no_full1 = game.board.checkwin(game.ai.num)
                for (num_b, num_j) in game.board.borne_won:
                    if num_j == 1:
                        if num_b not in game.ai.won:
                            game.ai.ajoute_flag(num_b)
                            for (num, val) in no_full1:
                                if num == num_b:
                                    ui.justif(num, val)

                # Démarrer le thread de l'IA
                ai_thread = threading.Thread(target=jouer_coup_ia, args=(game,))
                ai_thread.start()
        
        # Gestion du thread IA
        if ai_thread is not None:
            if not ai_thread.is_alive():
                ai_played = True
                ai_thread.join()
                ai_thread = None   

        # Affichage chargement
        if not ai_played:
            progression = min((time.time() - chargement_start) / 10, 1.0)
            afficher_barre_chargement(screen, progression)
        
        pygame.display.flip()
        clock.tick(120)
    
    pygame.quit()

if __name__ == "__main__":
    main()