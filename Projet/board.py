from card import Cartes
import random

class Board:

    def __init__(self):
        self.pioche = [] # pioche
        self.board = [[[] for _ in range(2)] for _ in range(9)] # les 9 flags, (9,2,3)
        self.unseencard = [] # toutes les cartes posé sur le terrain
        self.couleur = ['ro','ja','bl','ve','or','vi']
        self.duel_borne = []
        self.borne_won = []

    def restart(self):
        self.board = [[[] for _ in range(2)] for _ in range(9)]
        self.pioche = []
        
        for color in self.couleur:
            for val in range(9):
                self.pioche.append(Cartes(val+1,color))
                self.unseencard.append(Cartes(val+1,color))

        random.shuffle(self.pioche)
    
    def supprime_carte(self, num, couleur):
        for carte in self.unseencard:
            if carte.num == num and carte.couleur == couleur:
                self.unseencard.remove(carte)

    def piocher(self):
        if len(self.pioche) > 0:
            return self.pioche.pop()
        else:
            print("Pioche vide")
            return 
    
    def ajoute_carte_board(self, num_board, carte, num_joueur):
        if len(self.board[num_board][num_joueur]) < 3 and num_board not in self.borne_won:
            self.board[num_board][num_joueur].append(carte)
            self.supprime_carte(carte.num, carte.couleur)
            if len(self.board[num_board][num_joueur]) == 3:
                if num_board not in self.duel_borne:
                    self.duel_borne.append((num_board,num_joueur))
            return True
        else:
            print("la borne ",num_board," contient déjà 3 cartes")
            return False
    
    def isCouleur(self, list_card):
        return list_card[0].couleur == list_card[1].couleur and list_card[1].couleur == list_card[2].couleur

    def isSuite(self, list_card):
        liste_val = sorted(card.num for card in list_card)
        return liste_val[0] + 1 == liste_val[1] and liste_val[1] + 1 == liste_val[2]


    def isSuiteCouleur(self, list_card):
        return self.isSuite(list_card) and self.isCouleur(list_card)

    def isBrelan(self, list_card):
        return list_card[0].num == list_card[1].num and list_card[1].num == list_card[2].num

    def somme(self, list_card):
        return list_card[0].num + list_card[1].num + list_card[2].num

        
    def composition(self, list_card):
        somme_value = self.somme(list_card)
        if self.isSuiteCouleur(list_card):        # Suite Couleur valeur de 4
            return (4, somme_value)
        elif self.isBrelan(list_card):
            return (3, somme_value)          # Brelan de valeur 3
        elif self.isCouleur(list_card):
            return (2, somme_value)          # Couleur de valeur 2
        elif self.isSuite(list_card):
            return (1, somme_value)          # Suite de valeur 1
        else:
            return (0, somme_value)          # somme de valeur 0

    def carte_dispo(self, num, color):
        for carte in self.unseencard:
            if carte.num == num and carte.couleur == color:
                return True
        return False
    
    def carte_dispo_num(self, num):
        for carte in self.unseencard:
            if carte.num == num :
                return True
        return False
    
    def carte_dispo_couleur(self, color):
        for carte in self.unseencard:
            if carte.couleur == color:
                return True
        return False
    
    def best_comp(self, list_card):
        if len(list_card) == 2:
            val = sorted([list_card[0].num, list_card[1].num])
            couleur = [list_card[0].couleur, list_card[1].couleur]
            somme = list_card[0].num + list_card[1].num
            
            if couleur[0] == couleur[1]:     # Suite couleur
                if val[0] == val[1]+1:
                    if val[1]+1 <= 9:
                        if self.carte_dispo(val[1]+1, couleur[0]):
                            return (4, somme+val[1]+1)
                    if val[0]-1 >= 1:
                        if self.carte_dispo(val[0]-1, couleur[0]):
                            return (4, somme+val[0]-1)
            
            if val[0] == val[1]:             # Brelan
                if self.carte_dispo_num(val[1]):
                    return (3, somme+val[0])
            
            if couleur[0] == couleur[1]:     # Couleur
                if self.carte_dispo_couleur(couleur[0] ):
                    for i in range(9, 0, -1):
                        if self.carte_dispo_num(i):
                            return (2, somme+i)
            if val[1]+1 <= 9:                 # Suite (sans couleur)
                if self.carte_dispo_num(val[1]+1):
                    return (1, somme+val[1]+1)
            if val[0]-1 >= 1:
                if self.carte_dispo_num(val[0]-1):
                    return (1, somme+val[0]-1) 

            for i in range(9, 0, -1):         # Somme 
                if self.carte_dispo_num(i):
                    return (0, somme+i)
        elif len(list_card) == 1:
            val = list_card[0].num
            couleur = list_card[0].couleur
            # Suite couleur
            if val+2 <= 9:
                if self.carte_dispo(val+1, couleur) and self.carte_dispo(val+2, couleur):
                    return (4, val+val+1+val+2)
            if val+1 <= 9:
                if self.carte_dispo(val-1, couleur) and self.carte_dispo(val+1, couleur):
                    return (4, val-1+val+val+1)
            if val <= 9:
                if self.carte_dispo(val-1, couleur) and self.carte_dispo(val-2, couleur):
                    return (4, val-1+val+val-2)
            # Brelan
            for i in range(len(self.couleur)):
                for j in range(i + 1, len(self.couleur)): 
                    if self.carte_dispo(val, self.couleur[i]) and self.carte_dispo(val, self.couleur[j]):
                        return (3, 3*val)
            # Couleur
            for i in range(9, 0, -1):
                for j in range(i, 0, -1):
                    if self.carte_dispo(i, couleur) and self.carte_dispo(j, couleur):
                        return (2, val+i+j)
            # Suite
            if val+2 <= 9:
                if self.carte_dispo_num(val+1) and self.carte_dispo_num(val+2):
                    return (1, val+val+1+val+2)
            if val+1 <= 9:
                if self.carte_dispo_num(val-1) and self.carte_dispo_num(val+1):
                    return (1, val-1+val+val+1)
            if val <= 9:
                if self.carte_dispo_num(val-1) and self.carte_dispo_num(val-2):
                    return (1, val-1+val+val-2)
            # Somme
            for i in range(9, 0, -1):
                for j in range(i, 0, -1):
                    if self.carte_dispo_num(i) and self.carte_dispo_num(j):
                        return (0, val+i+j)
        
        elif len(list_card) == 0:
            # Suite Couleur
            for couleur in self.couleur:
                for num in range(9, 2, -1): 
                    if (self.carte_dispo(num, couleur) and 
                        self.carte_dispo(num-1, couleur) and 
                        self.carte_dispo(num-2, couleur)):
                        return (4, num + (num-1) + (num-2))

            #Brelan
            for num in range(9, 0, -1):
                count = sum(1 for carte in self.unseencard if carte.num == num)
                if count >= 3:
                    return (3, 3 * num)

            #Couleur
            for couleur in self.couleur:
                candidates = [carte.num for carte in self.unseencard if carte.couleur == couleur]
                if len(candidates) >= 3:
                    candidates.sort(reverse=True)  # Prendre les plus grandes valeurs
                    return (2, sum(candidates[:3]))

            #Suite
            for num in range(9, 2, -1):
                if (self.carte_dispo_num(num) and 
                    self.carte_dispo_num(num-1) and 
                    self.carte_dispo_num(num-2)):
                    return (1, num + (num-1) + (num-2))

            # Somme
            candidates = sorted([carte.num for carte in self.unseencard], reverse=True)
            if len(candidates) >= 3:
                return (0, sum(candidates[:3]))

        
    def check_win_borne(self):
        liste_win = []
        for (num_borne, num_joueur) in self.duel_borne:  # Copie pour éviter des bugs de suppression
            borne_player0 = self.board[num_borne][0] 
            borne_player1 = self.board[num_borne][1]
            if len(borne_player0) == len(borne_player1):
                # Ordre lexicographique pour comparer les compositions
                compo0 = self.composition(borne_player0)
                compo1 = self.composition(borne_player1)
                if compo0 > compo1:
                    liste_win.append((0, num_borne))  # Joueur 0 gagne
                    self.borne_won.append(num_borne)
                elif compo0 < compo1:
                    liste_win.append((1, num_borne))  # Joueur 1 gagne
                    self.borne_won.append(num_borne)
                else:
                    liste_win.append((num_joueur, num_borne))  # Cas rare d'égalité
                    self.borne_won.append(num_borne)
            
            elif len(borne_player0) > len(borne_player1):
                compo0 = self.composition(borne_player0)
                compo1 = self.best_comp(borne_player1)
                if compo0 > compo1:
                    liste_win.append((0, num_borne))
                    self.borne_won.append(num_borne)

            elif len(borne_player0) < len(borne_player1):
                compo0 = self.best_comp(borne_player0)
                compo1 = self.composition(borne_player1)
                if compo0 < compo1:
                    liste_win.append((1, num_borne))
                    self.borne_won.append(num_borne)
        return liste_win if liste_win else None  # Retourne None si aucune borne n'est gagnée



                 