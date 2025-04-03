import pygame
import numpy as np
from interface import Interface
from game import Game
from board import Board
from player import Player
import multiprocessing
import threading
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

def afficher_barre_chargement(screen, progression, texte="Attente du tour adverse..."):
    """Affiche une barre de chargement animée"""
    largeur, hauteur = screen.get_size()
    
    # Paramètres visuels
    barre_largeur = largeur * 0.6
    barre_hauteur = 30
    barre_x = (largeur - barre_largeur) // 2
    barre_y = hauteur * 0.7
    
    # Dessin
    pygame.draw.rect(screen, (50, 50, 80), (barre_x, barre_y, barre_largeur, barre_hauteur))  # Fond
    pygame.draw.rect(screen, (100, 200, 100), (barre_x, barre_y, int(barre_largeur * progression), barre_hauteur))  # Remplissage
    pygame.draw.rect(screen, (200, 200, 200), (barre_x, barre_y, barre_largeur, barre_hauteur), 2)  # Bordure
    
    # Texte
    font = pygame.font.Font(None, 32)
    texte_surf = font.render(texte, True, (240, 240, 240))
    screen.blit(texte_surf, texte_surf.get_rect(center=(largeur//2, 505)))

if __name__ == "__main__":
    # Initialisation Pygame et du jeu
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, depth=32)
    
    pygame.display.set_caption("Schotten Totten")
    
    game = Game()
    game.start()
    ui = Interface(screen)
    
    # Créer un pool de processus une seule fois
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_cores)
    
    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    ai_played = True
    ai_thread = None
    chargement_start = 0

    def jouer_coup_ia(game):
        """Fonction exécutée dans un thread, qui utilise multiprocessing pour les simulations."""
        # 1. Calculer les coups possibles (séquentiel)
        coup_rais = game.k_coup_raisonnable(game.ai, k=3)
        if not coup_rais:
            return

        # 2. Lancer les simulations en parallèle avec multiprocessing
        with multiprocessing.Pool() as pool:
            results = pool.starmap(
                game.simulation,
                [(coup, 100, 5) for coup in coup_rais]
            )
        
        # 3. Choisir et appliquer le meilleur coup (séquentiel)
        best_idx = np.argmax(results)
        borne_idx, carte_idx = coup_rais[best_idx]
        
        carte = game.ai.main[carte_idx]
        game.board.ajouter_carte(game.ai.num, borne_idx, (carte['num'], carte['couleur']))
        game.ai.retire_carte(carte)
        
        # Piocher une nouvelle carte pour l'IA
        new_card = game.board.piocher_carte()
        if new_card:
            game.ai.ajoute_carte(new_card)


    while running:
        ui.draw_board(game.player, game.ai, game.board)
        
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
    
        # Afficher le chargement si actif
        if ai_thread is not None and not ai_thread.is_alive():
            ai_played = True
            ai_thread.join()   

        if not ai_played:
            progression = min((time.time() - chargement_start) / 10, 1.0)  # 10 secondes max
            afficher_barre_chargement(screen, progression)
        
        pygame.display.flip()
        clock.tick(120)
    
    pool.close()
    pool.join()
    pygame.quit()