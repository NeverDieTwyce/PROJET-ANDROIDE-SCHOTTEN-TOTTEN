import pygame
from interface import Interface
from card import Cartes
from player import Joueur  
from game import Game

# Initialiser Pygame
pygame.init()

# Dimensions de la fenêtre de jeu
WIDTH, HEIGHT = 1000, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Schotten Totten")


# Créer une instance de l'interface utilisateur
ui = Interface(screen)
game = Game()
game.restart()
nb_tour = 0
cpt = 0

# Boucle principale du jeu
clock = pygame.time.Clock()

running = True
paused = False

while running:

    if paused and cpt>2:
        continue

    ui.draw_board(game.player0, game.player1, game.board)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Dessiner l'interface avec les cartes et l'état du jeu
        if ui.nb_tour%2 == 0:
            list_win = game.board.check_win_borne()
            if list_win:
                for num_joueur, num_borne in list_win:
                    if num_joueur == 0 and num_borne not in game.player0.flag:
                        game.player0.remporte_flag(num_borne)
            ajouer, surbr, couleur = ui.deplace_carte(event, game.player0, game.player1, game.board)
            if game.player0.main == []:
                ajouer = True
            if ajouer:
                carte = game.board.piocher()
                if carte is not None:
                    game.player0.ajoute_carte(carte)
                ui.nb_tour+=1

    ui.draw_board(game.player0, game.player1, game.board)   

    if ui.nb_tour%2 == 1:
        list_win = game.board.check_win_borne()
        if list_win:
            for num_joueur, num_borne in list_win:
                if num_joueur == 1 and num_borne not in game.player1.flag:
                    game.player1.remporte_flag(num_borne)
        ajouer = game.random_strat_IA()
        if ajouer:
            carte = game.board.piocher()
            if carte is not None:
                game.player1.ajoute_carte(carte)
            ui.nb_tour+=1

    # Rafraîchir l'écran
    ui.draw_board(game.player0, game.player1, game.board)

    if surbr is not None and couleur is not None:
        ui.surbrillance(surbr,couleur)

    pygame.display.flip()

    # Limiter le nombre de frames par seconde
    clock.tick(144)

    # vérification qu'un des joueurs à gagné
    if game.player0.a_gagner() or game.player1.a_gagner():
        paused = True
        cpt  += 1
        #running = False
# Quitter Pygame proprement
pygame.quit()