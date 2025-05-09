import numpy as np
from numba import njit, int32, types
from numba.typed import List
from board import _combinaison_numba, _best_comp, Board, COULEUR
from player import Player
from interface import Interface
import pygame
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

class Game:
    def __init__(self, difficulty = "facile"):
        self.board = Board() 
        self.player = Player(0)  # Joueur humain
        self.ai= Player(1)  # IA
        self.difficulty = difficulty 
    
    def copy(self):
        """Crée une copie complète du jeu"""
        new_game = Game()
        new_game.board = self.board.copy()
        new_game.player = self.player.copy()
        new_game.ai = self.ai.copy()
        return new_game
    
    def game_over(self):
        """Vérifie si la partie est terminée"""
        return self.player.a_gagner() or self.ai.a_gagner()
    
    def start(self):
        for i in range(6):
            carte = self.board.piocher_carte()
            self.player.ajoute_carte(carte)

        for i in range(6):
            carte = self.board.piocher_carte()
            self.ai.ajoute_carte(carte)
    
    def k_coup_raisonnable(self, player ,k=3):
        # Convertit les données pour Numba
        main_valide = [carte for carte in player.main if carte['num'] != -1]
        if not main_valide:
            # print("aucune carte à jouer pour le player ", player.num)
            return []
        # Convertir en tableau Numba
        main_numba = np.array(main_valide, dtype=carte_dtype)
        couleurs_numba = np.array(COULEUR, dtype='U2')
        
        # Appel de la version Numba
        coups, scores = _k_coup_raisonnable_numba(
            player.num,
            self.board.borne_nums,
            self.board.borne_colors.astype('U2'),
            main_numba,
            self.board.unseen,
            couleurs_numba,
            k,
            self.board.borne_won

        )
        
        # Convertit le résultat en format utilisable
        valid = coups[:, 0] != -1
        return [(int(c[0]), int(c[1])) for c in coups[valid]]
    
    # Permet de choisir un coup aléatoirement parmis les k meilleurs
    def strat_k(self, player=None ,k=3):
        if player == None:
            player = self.ai
        coup_rais = self.k_coup_raisonnable(player, k)
        if len(coup_rais) > 0:
            idx = np.random.randint(len(coup_rais))
            coup = coup_rais[idx]
            num_borne = coup[0]
            carte_ajouer = player.main[coup[1]]
            # Vérifier si l'ajout est réussi avant de retirer la carte
            success = self.board.ajouter_carte(player.num, num_borne, (carte_ajouer['num'], carte_ajouer['couleur']))
            if success:
                player.retire_carte(carte_ajouer)
                carte = self.board.piocher_carte()
                if carte:
                    player.ajoute_carte(carte)
                return True
        elif len(coup_rais) == 0:
            #print("aucun coup rais")
            # si on trouve aucun coup, dans ce cas là on joue un coup aléatoirement
            for carte_idx in range(len(player.main)):
                if player.main[carte_idx]['num'] == -1:
                    continue
                for borne_idx in range(9):
                    if self.board.ajouter_carte(player.num, borne_idx, player.main[carte_idx]):
                        player.retire_carte(player.main[carte_idx])
                        new_card = self.board.piocher_carte()
                        if new_card:
                            player.ajoute_carte(new_card)
                        return True
                    

    # Simule N parties en parallèle pour un coup donné
    def simulation(self, coup, simulations=500, k=3, joueur='ai'):
        result = 0
        cpt = 0
        while cpt < simulations:
            s = self.simulate_one(coup, k, joueur)
            if s != -1:
                result += s
                cpt += 1
        return result


    # Prépare une copie du jeu avec le coup initial
    def _prepare_sim_game(self, coup):
        sim_game = self.copy()
        borne_idx, carte_idx = coup
        carte = sim_game.ai.main[carte_idx]
        
        if not sim_game.board.ajouter_carte(sim_game.ai.num, borne_idx, (carte['num'], carte['couleur'])):
            return None
            
        sim_game.ai.retire_carte(carte)
        new_card = sim_game.board.piocher_carte()
        if new_card:
            sim_game.ai.ajoute_carte(new_card)
        return sim_game
 
    # Execute une simulation pour un coup donné jusqu'à la fin de la partie 
    def simulate_one(self, coup, k, joueur):
        sim_game = self.copy()
        borne_idx, carte_idx = coup
        if joueur == "ai":
            carte = sim_game.ai.main[carte_idx]
            cpt = 0

            sim_game.board.checkwin(sim_game.ai.num)
            for (num_b, num_j) in sim_game.board.borne_won:
                if num_j == 1:
                    if num_b not in sim_game.ai.won:
                        sim_game.ai.ajoute_flag(num_b)

            if not sim_game.board.ajouter_carte(sim_game.ai.num, borne_idx, (carte['num'], carte['couleur'])):
                return 0
                
            sim_game.ai.retire_carte(carte)
            new_card = sim_game.board.piocher_carte()
            if new_card:
                sim_game.ai.ajoute_carte(new_card)
            
            cpt = 0

            # Simuler la partie jusqu'à la fin
            while not sim_game.game_over():
                cpt += 1
                if cpt > 35:
                    print("simulation bloqué")
                    pygame.init()
                    WIDTH, HEIGHT = 1000, 700
                    flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, depth=32)
                    ui = Interface(screen)
                    ui.draw_board(sim_game.player, sim_game.ai, sim_game.board)
                    return -1
                
                sim_game.board.checkwin(sim_game.player.num)
                for (num_b, num_j) in sim_game.board.borne_won:
                    if num_j == 0:
                        if num_b not in sim_game.player.won:
                            sim_game.player.ajoute_flag(num_b)
                played2 = sim_game.strat_k(sim_game.player, k)

                if sim_game.game_over():
                    break

                sim_game.board.checkwin(sim_game.ai.num)
                for (num_b, num_j) in sim_game.board.borne_won:
                    if num_j == 1:
                        if num_b not in sim_game.ai.won:
                            sim_game.ai.ajoute_flag(num_b)
                played1 = sim_game.strat_k(sim_game.ai, k)
    
            return 1 if sim_game.ai.a_gagner() else 0
        
        elif joueur == "player":
            carte = sim_game.player.main[carte_idx]
            cpt = 0

            sim_game.board.checkwin(sim_game.player.num)
            for (num_b, num_j) in sim_game.board.borne_won:
                if num_j == 0:
                    if num_b not in sim_game.player.won:
                        sim_game.player.ajoute_flag(num_b)

            if not sim_game.board.ajouter_carte(sim_game.player.num, borne_idx, (carte['num'], carte['couleur'])):
                return 0
                
            sim_game.player.retire_carte(carte)
            new_card = sim_game.board.piocher_carte()
            if new_card:
                sim_game.player.ajoute_carte(new_card)
            
            cpt = 0

            # Simuler la partie jusqu'à la fin
            while not sim_game.game_over():
                cpt += 1
                if cpt > 35:
                    print("simulation bloqué")
                    return -1
                
                sim_game.board.checkwin(sim_game.ai.num)
                for (num_b, num_j) in sim_game.board.borne_won:
                    if num_j == 1:
                        if num_b not in sim_game.ai.won:
                            sim_game.ai.ajoute_flag(num_b)
                played1 = sim_game.strat_k(sim_game.ai, k)

                if sim_game.game_over():
                    break
                
                sim_game.board.checkwin(sim_game.player.num)
                for (num_b, num_j) in sim_game.board.borne_won:
                    if num_j == 0:
                        if num_b not in sim_game.player.won:
                            sim_game.player.ajoute_flag(num_b)
                played2 = sim_game.strat_k(sim_game.player, k)

            return 1 if sim_game.player.a_gagner() else 0

       


# Définition du type de carte pour Numba
carte_dtype = np.dtype([('num', np.int32), ('couleur', 'U2')])


@njit(cache=True)
def _k_coup_raisonnable_numba(ai_num, borne_nums, borne_colors, main, unseen, couleurs, k, borne_won):
    coups = np.full((k, 2), -1, dtype=np.int32)
    scores = np.full(k, -9999, dtype=np.int32)
    
    for borne_idx in range(9):
        # Utilise la logique existante du board
        existing = np.sum(borne_nums[borne_idx, ai_num] != -1)
        if existing == 3: continue # le cas où la borne contient déjà trois cartes, on saute cette bornes
        
        skip = False 

        for i in range(len(borne_won)):
            if borne_won[i]['num_borne'] == borne_idx:
                skip = True # cas où la borne est déjà remporté, on la saute aussi
                break
        
        if skip == True : continue

        priority = existing * 100 # on priorise les bornes ayant déjà des cartes posé (heuristique choisit arbitrairement)
        
        for carte_idx in range(len(main)):
            if main[carte_idx]['num'] == -1: continue

            # Simulation temporaire
            temp_nums = borne_nums.copy()
            temp_colors = borne_colors.copy()
            pos = np.where(temp_nums[borne_idx, ai_num] == -1)[0][0]
            
            temp_nums[borne_idx, ai_num, pos] = main[carte_idx]['num']
            temp_colors[borne_idx, ai_num, pos] = main[carte_idx]['couleur']

            # Crée current_cards pour best_comp, dans le cas où la bornes contient moins de deux cartes ( en considérant le coup joué)
            if pos < 2:
                current_cards = np.zeros(3, dtype=carte_dtype)
                count = 0
                for i in range(3):
                    num = temp_nums[borne_idx, ai_num, i]
                    color = temp_colors[borne_idx, ai_num, i]
                    if num != -1 and color != "":
                        current_cards[count]['num'] = num
                        current_cards[count]['couleur'] = color
                        count += 1
                current_cards = current_cards[:count]  # Redimensionne

            
            if pos == 2:
                type_comb, valeur = _combinaison_numba(
                    temp_nums[borne_idx, ai_num],
                    temp_colors[borne_idx, ai_num]
                )
            else:
                type_comb, valeur = _best_comp(unseen, current_cards, couleurs)
            
            score = (type_comb * 1000) + valeur + priority
            
            # Mise à jour des meilleurs scores
            min_idx = np.argmin(scores)
            if score > scores[min_idx]:
                coups[min_idx] = [borne_idx, carte_idx]
                scores[min_idx] = score
    
    return coups, scores

