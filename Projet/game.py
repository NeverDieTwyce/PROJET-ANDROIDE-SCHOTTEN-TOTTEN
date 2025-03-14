from board import Board
from card import Cartes
from player import Joueur
from random import randint

class Game:

    def __init__(self):
        self.board = Board()
        self.player0 = Joueur(0) # Joueur
        self.player1 = Joueur(1) # IA
        
    
    def restart(self):
        self.board.restart()
        self.player0.restart()
        self.player1.restart()
        for _ in range(6):
            carte = self.board.piocher()
            self.player0.ajoute_carte(carte)
        for _ in range(6):
            carte = self.board.piocher()
            self.player1.ajoute_carte(carte)

    
    def random_strat_IA(self):
        if self.player1.main == []:
            return True
        played = False
        choix = randint(0,len(self.player1.main)-1)
        borne = randint(0,8)
        while not played:
            if len(self.board.board[borne][1]) < 3 and borne not in self.board.borne_won:
                carte = self.player1.main[choix]
                self.player1.retire_carte(carte)
                self.board.ajoute_carte_board(borne, carte, 1)
                played = True
            else:
                borne = randint(0,8)
        return True
        


    
    
