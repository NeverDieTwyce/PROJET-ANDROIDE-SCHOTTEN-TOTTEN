from game import *
import multiprocessing
import numpy as np
import copy
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"


def worker(args):
    game_copy, coup, nb_simul, depth, joueur = args
    return game_copy.simulation(coup, nb_simul, depth, joueur)

def one_game_ia_first(nb_simul1, nb_simul2):
    game = Game()
    game.start()
    num_cores = multiprocessing.cpu_count()
    cpt =0

    with multiprocessing.Pool(num_cores) as pool:
        while not game.game_over():
            cpt += 1
            if cpt > 100:
                print("test corrompu")
                return -1
            # Tour IA 1
            game.board.checkwin(game.ai.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 1:
                    if num_b not in game.ai.won:
                        game.ai.ajoute_flag(num_b)
            
            if game.game_over():
                break   
            
            coup_rais = game.k_coup_raisonnable(game.ai, k=3)
            
            if coup_rais:
                args_list = [(game, coup, nb_simul1, 3, "ai") for coup in coup_rais]
                results = pool.map(worker, args_list)
                best_idx = np.argmax(results)
                borne_idx, carte_idx = coup_rais[best_idx]
                
                carte = game.ai.main[carte_idx]
                game.board.ajouter_carte(game.ai.num, borne_idx, (carte['num'], carte['couleur']))
                game.ai.retire_carte(carte)
                
                new_card = game.board.piocher_carte()
                if new_card:
                    game.ai.ajoute_carte(new_card)

            # Tour IA 2
            game.board.checkwin(game.player.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 0:
                    if num_b not in game.player.won:
                        game.player.ajoute_flag(num_b)

            coup_rais2 = game.k_coup_raisonnable(game.player, k=3)
            
            if coup_rais2:
                args_list = [(game, coup, nb_simul2, 3, "player") for coup in coup_rais2]
                results2 = pool.map(worker, args_list)
                best_idx2 = np.argmax(results2)
                borne_idx2, carte_idx2 = coup_rais2[best_idx2]
                
                carte2 = game.player.main[carte_idx2]
                game.board.ajouter_carte(game.player.num, borne_idx2, (carte2['num'], carte2['couleur']))
                game.player.retire_carte(carte2)
                
                new_card = game.board.piocher_carte()
                if new_card:
                    game.player.ajoute_carte(new_card)

    return 1 if game.ai.a_gagner() else 0


def one_game_no_simul(nb_simul1):
    game = Game()
    game.start()
    num_cores = multiprocessing.cpu_count()
    cpt =0

    with multiprocessing.Pool(num_cores) as pool:
        while not game.game_over():
            cpt += 1
            if cpt > 100:
                print("stat corrompu")
                return -1
            # Tour IA 2
            game.board.checkwin(game.player.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 0:
                    if num_b not in game.player.won:
                        game.player.ajoute_flag(num_b)

            played2 = game.strat_k(game.player, 3)
            game.board.checkwin(game.player.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 0:
                    if num_b not in game.player.won:
                        game.player.ajoute_flag(num_b)

            if game.game_over():
                break   

            # Tour IA 1
            game.board.checkwin(game.ai.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 1:
                    if num_b not in game.ai.won:
                        game.ai.ajoute_flag(num_b)
            coup_rais = game.k_coup_raisonnable(game.ai, k=3)
            
            if coup_rais:
                args_list = [(game, coup, nb_simul1, 3, "ai") for coup in coup_rais]
                results = pool.map(worker, args_list)
                best_idx = np.argmax(results)
                borne_idx, carte_idx = coup_rais[best_idx]
                
                carte = game.ai.main[carte_idx]
                game.board.ajouter_carte(game.ai.num, borne_idx, (carte['num'], carte['couleur']))
                game.ai.retire_carte(carte)
                
                new_card = game.board.piocher_carte()
                if new_card:
                    game.ai.ajoute_carte(new_card)

    return 1 if game.ai.a_gagner() else 0


def one_game_no_simul2(nb_simul1):
    game = Game()
    game.start()
    num_cores = multiprocessing.cpu_count()
    cpt =0

    with multiprocessing.Pool(num_cores) as pool:
        while not game.game_over():
            cpt += 1
            if cpt > 100:
                print("stat corrompu")
                return -1
            
             # Tour IA 1
            game.board.checkwin(game.ai.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 1:
                    if num_b not in game.ai.won:
                        game.ai.ajoute_flag(num_b)
            coup_rais = game.k_coup_raisonnable(game.ai, k=3)
            
            if coup_rais:
                args_list = [(game, coup, nb_simul1, 3, "ai") for coup in coup_rais]
                results = pool.map(worker, args_list)
                best_idx = np.argmax(results)
                borne_idx, carte_idx = coup_rais[best_idx]
                
                carte = game.ai.main[carte_idx]
                game.board.ajouter_carte(game.ai.num, borne_idx, (carte['num'], carte['couleur']))
                game.ai.retire_carte(carte)
                
                new_card = game.board.piocher_carte()
                if new_card:
                    game.ai.ajoute_carte(new_card)
            
            if game.game_over():
                break   

            # Tour IA 2
            game.board.checkwin(game.player.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 0:
                    if num_b not in game.player.won:
                        game.player.ajoute_flag(num_b)

            played2 = game.strat_k(game.player, 3)
            game.board.checkwin(game.player.num)
            for (num_b, num_j) in game.board.borne_won:
                if num_j == 0:
                    if num_b not in game.player.won:
                        game.player.ajoute_flag(num_b)
                        
    return 1 if game.ai.a_gagner() else 0

def stat_game_(sim1, sim2, nb_partie):
    victory = 0
    cpt = 0
    while cpt < nb_partie:
        s = one_game_ia_first(sim1, sim2)
        if s != -1:
            victory += s
            cpt += 1
            print("nombre de victoire =",victory, "  nombre de partie =", cpt)
        t = one_game_ia_first(sim2, sim1)
        if t != -1:
            if t == 0:
                victory += 1
                cpt += 1
                print("nombre de victoire =",victory, "  nombre de partie =", cpt)
            else:
                cpt += 1
                print("nombre de victoire =",victory, "  nombre de partie =", cpt)

    return victory

def stat_game_2(sim1, nb_partie):
    victory = 0
    cpt = 0
    while cpt < nb_partie:
        s = one_game_no_simul(sim1)
        if s != -1:
            victory += s
            cpt += 1
            print("nombre de victoire =",victory, "  nombre de partie =", cpt)
        s = one_game_no_simul2(sim1)
        if s != -1:
            victory += s
            cpt += 1
            print("nombre de victoire =",victory, "  nombre de partie =", cpt)
    return victory


if __name__ == '__main__':
    print("50 vs 500")
    victoires = stat_game_(50, 500, 1000) # Renvoie le nombre de victoire pour la simulation 50
    #print("100 vs 0 k=3 pour simul et k=3 pour no simul")
    #victoires = stat_game_2(100, 1000) # Renvoie le nombre de victoire pour la simulation 100
    print("Nombre de victoires de l'IA :", victoires)