from game import *
from player import *
from board import *


# Le joueur joue en premier, renvoie 1 si l'ia gagne 0 sinon
# k1 pour le joueur
# k2 pour l'ia
def test_param_k_player_first(k1, k2):
    game = Game()
    game.start()
    while not game.game_over():
        game.board.checkwin(game.player.num)
        for (num_b, num_j) in game.board.borne_won:
            if num_j == 0:
                if num_b not in game.player.won:
                    game.player.ajoute_flag(num_b)
        game.strat_k(game.player, k1)


        game.board.checkwin(game.ai.num)
        for (num_b, num_j) in game.board.borne_won:
            if num_j == 1:
                if num_b not in game.ai.won:
                    game.ai.ajoute_flag(num_b)
        game.strat_k(game.ai, k2)

    return 1 if game.ai.a_gagner() else 0


# L'ia joue en premier, renvoie 1 si l'ia gagne 0 sinon
# k1 pour le joueur
# k2 pour l'ia
def test_param_k_ia_first(k1, k2):
    game = Game()
    game.start()
    while not game.game_over():
        game.board.checkwin(game.ai.num)
        for (num_b, num_j) in game.board.borne_won:
            if num_j == 1:
                if num_b not in game.ai.won:
                    game.ai.ajoute_flag(num_b)
        game.strat_k(game.ai, k2)

        game.board.checkwin(game.player.num)
        for (num_b, num_j) in game.board.borne_won:
            if num_j == 0:
                if num_b not in game.player.won:
                    game.player.ajoute_flag(num_b)
        game.strat_k(game.player, k1)

    return 1 if game.ai.a_gagner() else 0




# Renvoie le nombre de victoire de la strat_k avec k = k2 contre k=k1
def test_param_k(k1,k2, nb):
    victory = 0
    for i in range(nb):
        victory += test_param_k_ia_first(k1, k2)
    for i in range(nb):
        victory += test_param_k_player_first(k1, k2)
    return victory

# on fait 1000 partie pour un couple (k1, k2)
for k1 in range(1,6):
    for k2 in range(1,6):
        print(k2, " contre ", k1)
        nb_victory = test_param_k(k1, k2, 500)
        print(k2, " contre ", k1, " , nombre de victoire sur 1000 parties = ", nb_victory)