import numpy as np

class Player:
    def __init__(self, num):
        self.main = np.array(
            [(-1, '') for _ in range(6)],
            dtype=[('num', np.int32), ('couleur', 'U2')]
        )
        self.num = num
        self.index = 0    # index pour géré la main du joueur
        self.won = []

    # on ajoute la carte à la main
    # en vérifiant bien que carte est bien différent de None et que la main n'est pas pleine
    def ajoute_carte(self, carte):
        if carte is None or self.index >= 6:
            return False
        self.main[self.index] = carte
        self.index += 1
        return True
    
    # on supprime la carte à la main si on la trouve, sinon il se passe rien
    def retire_carte(self, carte):
        if carte is None:
            return
        for i in range(len(self.main)):
            if self.main[i] == carte:
                self.main = np.delete(self.main, i)
                self.main = np.append(self.main, np.array((-1, ''),dtype=[('num', np.int32), ('couleur', 'U2')]))
                self.index -= 1
                break
    
    # on ajoute la borne num_borne dans les bornes gagnées
    def ajoute_flag(self, num_borne):
        if num_borne not in self.won:
            self.won.append(num_borne)
    

    # on vérifie si le joueur a gagné
    def a_gagner(self):
        bornes = sorted(self.won)
        # Vérifier 3 bornes consécutives
        for i in range(len(bornes) - 2):
            if bornes[i] + 1 == bornes[i+1] and bornes[i] + 1 == bornes[i+2] - 1:
                return True
        # Vérifier 5 bornes totales
        return len(self.won) >= 5

    def copy(self):
        """Crée une copie du joueur"""
        new_player = Player(self.num)
        new_player.main = np.copy(self.main)
        new_player.won = self.won.copy()
        new_player.index = self.index
        return new_player