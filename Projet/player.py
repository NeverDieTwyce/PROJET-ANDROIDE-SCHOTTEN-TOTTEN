

class Joueur:

    def __init__(self, num):
        self.num = num # jeu à deux joueur donc num prendra que deux valeurs possible ici 0 ou 1
        self.main = [] # la main du joueur
        self.flag = [] # flag remporté par le joueur 

    def ajoute_carte(self, carte):
        if len(self.main) < 6:
            self.main.append(carte)
        else:
            print("Erreur Joueur", self.num, " a deja 6 cartes en main")
    
    def retire_carte(self, carte):
        if len(self.main) > 0:
            self.main.remove(carte)
        else:
            print("Erreur Joueur", self.num, " a pas de cartes en main")
    
    def remporte_flag(self, num_flag):
        if len(self.flag) < 9:
            self.flag.append(num_flag)
        else:
            print("Erreur Joueur", self.num, " a remporte plus de 9 flags")

    def restart(self):
        self.main = []
        self.flag = []

    def a_gagner(self):
        if len(self.flag) >= 5:
            print("Joueur ", self.num ," a gagné 5 flags")
            return True
        if len(self.flag) >= 3:
            self.flag = sorted(self.flag)
            for i in range(len(self.flag) - 2):
                if self.flag[i] + 1 == self.flag[i + 1] and self.flag[i + 1] + 1 == self.flag[i + 2]:
                    print("Joueur ", self.num ," a gagné 3 flags consécutif")
                    return True
        return False


        