import numpy as np
from numba import njit

from typing import List, Tuple

COULEUR = np.array(['ro','bl','ve','ja','or','vi'], dtype="U2")

duel_dtype = np.dtype([('num_borne', np.int32), ('joueur', np.int32), ('ordre', 'U2')])
won_dtype = np.dtype([('num_borne', np.int32), ('joueur', np.int32)])

class Board:
    def __init__(self):
        # Tableaux des bornes
        self.borne_nums = np.full((9, 2, 3), -1, dtype=np.int32)
        self.borne_colors = np.full((9, 2, 3), "", dtype="U2")
        
        # Création et mélange de la pioche
        self.pioche = np.array(
            [(num, color) for num in range(1, 10) for color in COULEUR],
            dtype=[('num', np.int32), ('couleur', 'U2')]
        )
        np.random.shuffle(self.pioche)
        self.index_pioche = 0

        # Cartes non vues (copie indépendante de la pioche)
        self.unseen = self.pioche.copy()
        
        # Bornes remportées et en duel
        self.borne_won = np.zeros(0, dtype=won_dtype)  
        self.borne_duel = np.zeros(0, dtype=duel_dtype) 

    def copy(self):
        """Crée une copie complète du plateau"""
        new_board = Board()
        new_board.borne_nums = np.copy(self.borne_nums)
        new_board.borne_colors = np.copy(self.borne_colors)
        new_board.pioche = np.copy(self.pioche)
        new_board.index_pioche = self.index_pioche
        new_board.unseen = np.copy(self.unseen)
        new_board.borne_won = np.copy(self.borne_won)
        new_board.borne_duel = np.copy(self.borne_duel)
        return new_board

    def ajouter_carte(self, joueur, num_borne, carte):
        """Ajoute une carte et met à jour les cartes non vues"""
        for (num_b, num_j) in self.borne_won:
            if num_b == num_borne:
                return False
        success, self.borne_duel= _ajouter_carte(self.borne_nums, self.borne_colors, joueur, num_borne, carte[0], carte[1], self.borne_duel)
        if success:
            self.unseen = _supprime_unseen(self.unseen, carte[0], carte[1])
        return success

    def piocher_carte(self):
        """Pioche une carte et incrémente l'index"""
        if self.index_pioche < len(self.pioche):
            carte = self.pioche[self.index_pioche]
            self.index_pioche += 1
            return carte
        return None

    def combinaison(self, num_borne, num_joueur):
        """Calcul la valeur d'une combinaison pour une borne donnée"""
        nums = self.borne_nums[num_borne, num_joueur]
        colors = self.borne_colors[num_borne, num_joueur]
        
        if not _isValid(nums, colors):
            return (0, 0)  # Combinaison invalide
        
        suite = _isSuite(nums)
        couleur = _isCouleur(colors)
        valeur = _somme_num(nums)
        
        if suite and couleur:
            return (4, valeur)
        elif _isBrelan(nums):
            return (3, valeur)
        elif couleur:
            return (2, valeur)
        elif suite:
            return (1, valeur)
        else:
            return (0, valeur)

    def best_comp(self, num_joueur, num_borne):
        """Retourne la meilleure combinaison possible"""
           # Crée un tableau compatible avec Numba
        card_dtype = np.dtype([('num', np.int32), ('couleur', 'U2')])
        liste_card = np.zeros(3, dtype=card_dtype)
        
        count = 0
        for i in range(3):
            num = self.borne_nums[num_borne, num_joueur, i]
            color = self.borne_colors[num_borne, num_joueur, i]
            if num != -1 and color != "":
                liste_card[count] = (num, color)
                count += 1
        
        # Redimensionne selon le nombre de cartes réelles
        liste_card = liste_card[:count]
        return _best_comp(self.unseen, liste_card, COULEUR)

    def checkwin(self, num):
        winners = []
        non_full = []
        for (num_borne, num_joueur, str) in self.borne_duel:
            if num_joueur == num:
                other_player_three_cards = False
                for (num_borne2, num_joueur2, str2) in self.borne_duel:
                    if num_borne == num_borne2 and num_joueur != num_joueur2:
                        other_player_three_cards = True
                        if str == "pr":
                            if self.combinaison(num_borne, num_joueur) >= self.combinaison(num_borne, num_joueur2):
                                winners.append((num_borne, num_joueur))
                                self.borne_won = np.append(self.borne_won, np.array([(num_borne, num_joueur)], dtype=won_dtype))
                            else:
                                winners.append((num_borne, num_joueur2))
                                self.borne_won = np.append(self.borne_won, np.array([(num_borne, num_joueur2)], dtype=won_dtype))
                        elif str == "sc":
                            if self.combinaison(num_borne, num_joueur2) >= self.combinaison(num_borne, num_joueur):
                                winners.append((num_borne, num_joueur2))
                                self.borne_won = np.append(self.borne_won, np.array([(num_borne, num_joueur2)], dtype=won_dtype))
                            else:
                                winners.append((num_borne, num_joueur))
                                self.borne_won = np.append(self.borne_won, np.array([(num_borne, num_joueur)], dtype=won_dtype))
                if other_player_three_cards == False:
                    if self.combinaison(num_borne, num_joueur) >= self.best_comp(1-num_joueur, num_borne):
                        winners.append((num_borne, num_joueur))
                        self.borne_won = np.append(self.borne_won, np.array([(num_borne, num_joueur)], dtype=won_dtype))
                        non_full.append((num_borne, self.best_comp(1-num_joueur, num_borne)))
        return non_full 
    

@njit(cache=True)
def _supprime_unseen(unseen, num, couleur):
    """Supprime une carte du tableau unseen (version Numba)"""
    mask = np.ones(len(unseen), dtype=np.bool_)
    for i in range(len(unseen)):
        if unseen[i]['num'] == num and unseen[i]['couleur'] == couleur:
            mask[i] = False
            break
    return unseen[mask]

@njit(cache=True)
def _ajouter_carte(borne_nums, borne_colors, joueur, num_borne, num, couleur, borne_duel):
    """Ajoute une carte à une borne et gère les duels (version Numba compatible)"""
    if joueur not in (0, 1) or num_borne < 0 or num_borne >= 9:
        return False, borne_duel
        
    for k in range(3):
        if borne_nums[num_borne, joueur, k] == -1:
            borne_nums[num_borne, joueur, k] = num
            borne_colors[num_borne, joueur, k] = couleur
            
            # Vérifie si c'est la 3ème carte (k == 2 car index 0-1-2)
            if k == 2:
                nouveau_duel = np.zeros(1, dtype=duel_dtype)
                nouveau_duel[0]['num_borne'] = num_borne
                nouveau_duel[0]['joueur'] = joueur
                
                # Vérifie si un duel existe déjà
                deja_en_duel = False
                for i in range(len(borne_duel)):
                    if borne_duel[i]['num_borne'] == num_borne:
                        deja_en_duel = True
                        break
                
                if not deja_en_duel:
                    nouveau_duel[0]['ordre'] = 'pr'  # premier
                else:
                    nouveau_duel[0]['ordre'] = 'sc'  # second
                
                # Ajoute le nouveau duel (méthode compatible Numba)
                if len(borne_duel) == 0:
                    borne_duel = nouveau_duel
                else:
                    borne_duel = np.concatenate((borne_duel, nouveau_duel))
    
            return True, borne_duel
        
    return False, borne_duel

@njit(cache=True)
def _isValid(card_nums, card_colors):
    """Vérifie qu'il y a exactement 3 cartes valides"""
    count_nums = 0
    count_colors = 0
    for i in range(len(card_nums)):
        if card_nums[i] != -1:
            count_nums += 1
        if card_colors[i] != "":
            count_colors += 1
    return count_nums == 3 and count_colors == 3

@njit(cache=True)
def _isSuite(list_nums):
    nums_sorted = np.sort(list_nums)
    return (nums_sorted[0] + 2 == nums_sorted[1] + 1 == nums_sorted[2])

@njit(cache=True)
def _isBrelan(list_nums):
    return list_nums[0] == list_nums[1] == list_nums[2]

@njit(cache=True)
def _isCouleur(list_colors):
    return list_colors[0] == list_colors[1] == list_colors[2]

@njit(cache=True)
def _somme_num(list_card):
    return np.sum(list_card)

@njit(cache=True)
def carte_dispo_num(unseencard, num: int) -> bool:
    for carte in unseencard:
        if carte['num'] == num:
            return True
    return False

@njit(cache=True)
def carte_dispo_couleur(unseencard, color: str) -> bool:
    for carte in unseencard:
        if carte['couleur'] == color:
            return True
    return False

@njit(cache=True)
def _carte_dispo_num_et_couleur(unseencard, num, couleur):
    for c in unseencard:
        if c['num'] == num and c['couleur'] == couleur:
            return True
    return False


@njit(cache=True)
def _is_valid_numba(nums, colors):
    """Version manuelle pour compter les éléments valides"""
    count_nums = 0
    count_colors = 0
    
    for i in range(len(nums)):
        if nums[i] != -1:
            count_nums += 1
        if colors[i] != '':
            count_colors += 1
            
    return count_nums == 3 and count_colors == 3

@njit(cache=True)
def _combinaison_numba(nums, colors):
    """Version Numba de Board.combinaison()"""
    if not _is_valid_numba(nums, colors):
        return (0, 0)
    
    suite = (nums[0]+1 == nums[1] and nums[0]+2 == nums[2]) or \
            (nums[1]+1 == nums[2] and nums[0]+1 == nums[1])
    couleur = colors[0] == colors[1] == colors[2]
    valeur = np.sum(nums)
    
    if suite and couleur: return (4, valeur)
    if nums[0] == nums[1] == nums[2]: return (3, valeur)
    if couleur: return (2, valeur)
    if suite: return (1, valeur)
    return (0, valeur)

@njit(cache=True)
def _best_comp(unseencard, list_card, couleurs_possibles):
    if len(list_card) == 2:
        val0, val1 = list_card[0]['num'], list_card[1]['num']
        # Remplacement de np.array([val0, val1]).sort() par un tri manuel
        if val0 > val1:
            val_min, val_max = val1, val0
        else:
            val_min, val_max = val0, val1
        couleur0, couleur1 = list_card[0]['couleur'], list_card[1]['couleur']
        somme = val0 + val1
        
        # Suite couleur
        if couleur0 == couleur1 and (val_max - val_min == 1):
            if val_max + 1 <= 9 and _carte_dispo_num_et_couleur(unseencard, val_max + 1, couleur0):
                return (4, somme + val_max + 1)
            if val_min - 1 >= 1 and _carte_dispo_num_et_couleur(unseencard, val_min - 1, couleur0):
                return (4, somme + val_min - 1)
            
        if couleur0 == couleur1 and abs(val0 - val1) == 2:  # <-- Écart de 2
            middle_val = (val0 + val1) // 2
            if _carte_dispo_num_et_couleur(unseencard, middle_val, couleur0):
                return (4, val0 + val1 + middle_val)  # Suite couleur
        
        # Brelan
        if val0 == val1 and carte_dispo_num(unseencard, val1):
            return (3, somme + val0)
        
        # Couleur
        if couleur0 == couleur1 and carte_dispo_couleur(unseencard, couleur0):
            for i in range(9, 0, -1):
                if carte_dispo_num(unseencard, i):
                    return (2, somme + i)
        
        # Suite (sans couleur)
        if (val_max - val_min == 1):
            if val_max + 1 <= 9 and carte_dispo_num(unseencard, val_max + 1):
                return (1, somme + val_max + 1)
            if val_min - 1 >= 1 and carte_dispo_num(unseencard, val_min - 1):
                return (1, somme + val_min - 1)
        if abs(val0 - val1) == 2:  # <-- Écart de 2
            middle_val = (val0 + val1) // 2
            if carte_dispo_num(unseencard, middle_val):
                return (1, val0 + val1 + middle_val)  # Suite couleur

        # Somme
        for i in range(9, 0, -1):
            if carte_dispo_num(unseencard, i):
                return (0, somme + i)
    
    elif len(list_card) == 1:
        val = list_card[0]['num']
        couleur = list_card[0]['couleur']
        somme = val
        
        # Suite couleur
        if val + 2 <= 9:
            if (_carte_dispo_num_et_couleur(unseencard, val + 1, couleur) and 
                _carte_dispo_num_et_couleur(unseencard, val + 2, couleur)):
                return (4, val + (val + 1) + (val + 2))
        if val + 1 <= 9 and val - 1 >= 1:
            if (_carte_dispo_num_et_couleur(unseencard, val - 1, couleur) and 
                _carte_dispo_num_et_couleur(unseencard, val + 1, couleur)):
                return (4, (val - 1) + val + (val + 1))
        if val - 2 >= 1:
            if (_carte_dispo_num_et_couleur(unseencard, val - 1, couleur) and 
                _carte_dispo_num_et_couleur(unseencard, val - 2, couleur)):
                return (4, (val - 2) + (val - 1) + val)
        
        # Brelan
        count = 0
        for c in unseencard:
            if c['num'] == val:
                count += 1
                if count == 2:  # On a déjà 1 carte, il en faut 2 de plus
                    return (3, 3 * val)
        
        # Couleur
        max1 = max2 = 0
        for c in unseencard:
            if c['couleur'] == couleur:
                if c['num'] > max1:
                    max2 = max1
                    max1 = c['num']
                elif c['num'] > max2:
                    max2 = c['num']
        if max1 > 0 and max2 > 0:
            return (2, val + max1 + max2)
        
        # Suite
        if val + 2 <= 9:
            if carte_dispo_num(unseencard, val + 1) and carte_dispo_num(unseencard, val + 2):
                return (1, val + (val + 1) + (val + 2))
        if val + 1 <= 9 and val - 1 >= 1:
            if carte_dispo_num(unseencard, val - 1) and carte_dispo_num(unseencard, val + 1):
                return (1, (val - 1) + val + (val + 1))
        if val - 2 >= 1:
            if carte_dispo_num(unseencard, val - 1) and carte_dispo_num(unseencard, val - 2):
                return (1, (val - 2) + (val - 1) + val)
        
        # Somme
        max1 = max2 = 0
        for c in unseencard:
            if c['num'] > max1:
                max2 = max1
                max1 = c['num']
            elif c['num'] > max2:
                max2 = c['num']
        if max1 > 0 and max2 > 0:
            return (0, val + max1 + max2)
    
    elif len(list_card) == 0:
        # Suite Couleur
        for couleur in couleurs_possibles:
            for num in range(9, 2, -1):
                if (_carte_dispo_num_et_couleur(unseencard, num, couleur) and 
                    _carte_dispo_num_et_couleur(unseencard, num - 1, couleur) and 
                    _carte_dispo_num_et_couleur(unseencard, num - 2, couleur)):
                    return (4, num + (num - 1) + (num - 2))
        
        # Brelan
        for num in range(9, 0, -1):
            count = 0
            for c in unseencard:
                if c['num'] == num:
                    count += 1
                    if count == 3:
                        return (3, 3 * num)
        
        # Couleur
        for couleur in couleurs_possibles:
            max1 = max2 = max3 = 0
            for c in unseencard:
                if c['couleur'] == couleur:
                    if c['num'] > max1:
                        max3 = max2
                        max2 = max1
                        max1 = c['num']
                    elif c['num'] > max2:
                        max3 = max2
                        max2 = c['num']
                    elif c['num'] > max3:
                        max3 = c['num']
            if max1 > 0 and max2 > 0 and max3 > 0:
                return (2, max1 + max2 + max3)
        
        # Suite
        for num in range(9, 2, -1):
            if (carte_dispo_num(unseencard, num) and 
                carte_dispo_num(unseencard, num - 1) and 
                carte_dispo_num(unseencard, num - 2)):
                return (1, num + (num - 1) + (num - 2))

        # Somme
        max1 = max2 = max3 = 0
        for c in unseencard:
            if c['num'] > max1:
                max3 = max2
                max2 = max1
                max1 = c['num']
            elif c['num'] > max2:
                max3 = max2
                max2 = c['num']
            elif c['num'] > max3:
                max3 = c['num']
        if max1 > 0 and max2 > 0 and max3 > 0:
            return (0, max1 + max2 + max3)
        
    return (0, 0)  # Aucune combinaison trouvée




if __name__ == "__main__":
    board = Board()
    print("Nombre de cartes non vues initiales:", len(board.unseen))
    
    success = board.ajouter_carte(0, 0, (7, 'ro'))
    success = board.ajouter_carte(0, 0, (8, 'ro'))
    success = board.ajouter_carte(0, 0, (6, 'ro'))

    success = board.ajouter_carte(1, 0, (7, 'vi'))
    
   

    print(board.checkwin())