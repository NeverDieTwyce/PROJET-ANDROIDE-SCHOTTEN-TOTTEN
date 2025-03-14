
class Cartes:
    def __init__(self, num, couleur):
        self.num = num # valeur de la carte
        self.couleur = couleur # couleur de la carte
        self.posx0 = None
        self.posy0 = None
        self.posx = None
        self.posy = None
    
    def changePos(self, x,y):
        self.posx = x
        self.posy = y
    
    def changePosInit(self, x,y):
        self.posx0 = x
        self.posy0 = y
    
    def resetPos(self):
        self.posx = self.posx0
        self.posy = self.posy0
    