import pygame

# Dimensions de la fenêtre de jeu
WIDTH, HEIGHT = 1000, 700

class Interface:

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.card_size = (90,80) # taille des cartes
        self.dragging = None  # Carte en cours de déplacement
        self.offset_x = 0
        self.offset_y = 0
        self.nb_tour = 0


    def draw_board(self, player, opponent, board):
        player_cards = player.main
        opponent_cards = opponent.main
        board_flags = board.board
        # Afficher les cartes des joueurs et l'état des bornes
        self.draw_background()
        self.draw_board_bornes(board_flags)
        self.draw_player_cards(player_cards)
        self.draw_opponent_cards(opponent_cards)
        self.draw_flag_win(player, opponent)
        pygame.display.flip()  # Rafraîchir l'affichage


    def draw_player_cards(self, cards):
        # Afficher les cartes du joueur 0
        decalage_bas = 50 
        decalage_droite = 50 

        for i, card in enumerate(cards):
            name = f"cartes/carte_{card.couleur}/{card.num}_{card.couleur}.jpg"
            carte = pygame.image.load(name)  
            carte = pygame.transform.scale(carte, self.card_size)
            x = decalage_droite + i * (self.card_size[0]-20)
            y =  HEIGHT - self.card_size[1] -decalage_bas
            if card.posx == None or self.nb_tour%2 !=0: 
                card.changePos(x,y)
                card.changePosInit(x,y)
            self.screen.blit(carte, (card.posx,card.posy))


    def draw_opponent_cards(self, cards):
        # Afficher les cartes de l'adversaire (les cartes sont cachées)
        decalage_haut = 50  
        decalage_gauche = WIDTH - self.card_size[0] - 50

        for i, card in enumerate(cards):
            carte = pygame.image.load("cartes/dos_carte.png") 
            carte = pygame.transform.scale(carte, self.card_size) 
            x = decalage_gauche - i * (self.card_size[0]-20) 
            y = decalage_haut
            if card.posx == None or self.nb_tour%2 == 0: 
                card.changePos(x,y)
                card.changePosInit(x,y)
            self.screen.blit(carte, (card.posx,card.posy))


    def draw_board_bornes(self, board):
        # Dessine les bornes (9 cases)
        decalage_droite = 5
        taille_borne = (WIDTH//9 -10, 90)  # taille des cartes de la borne
        pos_y = HEIGHT//2.3
        
        # dessine les flag sur le board
        for i, case in enumerate(board):
            pos_x = (i % 9)  *(taille_borne[0]+10) + decalage_droite
            name_img = f"cartes/flag{1 + (i%3)}.png"
            carte = pygame.image.load(name_img) 
            carte = pygame.transform.scale(carte, taille_borne)
            self.screen.blit(carte, (pos_x, pos_y)) 

        # dessine les cartes sur chaque flag
        for i, flag in enumerate(board):
            for j, liste_carte in enumerate(flag):
                pos_x = (i % 9)  *(taille_borne[0]+10) + decalage_droite
                
                if j == 0:
                    for k, carte in enumerate(liste_carte):
                        name = f"cartes/carte_{carte.couleur}/{carte.num}_{carte.couleur}.jpg"
                        carte = pygame.image.load(name)
                        carte = pygame.transform.scale(carte, self.card_size)   
                        self.screen.blit(carte, (pos_x + decalage_droite , pos_y + taille_borne[1] + k*(self.card_size[1] - (2/3)*self.card_size[1])))
                elif j ==1:
                    for k in range(len(liste_carte)-1,-1,-1):
                        carte = liste_carte[k]
                        name = f"cartes/carte_{carte.couleur}/{carte.num}_{carte.couleur}.jpg"
                        carte = pygame.image.load(name)
                        carte = pygame.transform.scale(carte, self.card_size) 
                        self.screen.blit(carte, (pos_x + decalage_droite , pos_y - self.card_size[1] - k*(self.card_size[1] - (2/3)*self.card_size[1])))

    def surbrillance(self, num_board, color):
        decalage_droite = 5
        taille_borne = (WIDTH//9 -10, 90)  # taille des cartes de la borne
        pos_y = HEIGHT//2.3
        
        # dessine les flag sur le board
        pos_x = (num_board % 9)  *(taille_borne[0]+10) + decalage_droite
        pygame.draw.rect(self.screen, color, (pos_x, pos_y, taille_borne[0], taille_borne[1]), 3)
        pygame.display.flip()

    def deplace_carte(self, event, player, opponent, board):
        pos_y = HEIGHT//2.3
        taille_borne = (WIDTH//9 -10, 90)
        player_cards = player.main
        opponent_cards = opponent.main
        board_flags = board.board
        num_board = None
        couleur = None
        # Détection du clic sur une carte
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for i, card in enumerate(player_cards):
                card_rect = pygame.Rect(card.posx, card.posy, *self.card_size)
                if card_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = i
                    self.offset_x = card.posx - mouse_x
                    self.offset_y = card.posy - mouse_y
                    break  # On prend la première carte touchée

        # Déplacement de la carte
        elif event.type == pygame.MOUSEMOTION and self.dragging is not None:
            mouse_x, mouse_y = event.pos
            player_cards[self.dragging].changePos(mouse_x + self.offset_x, mouse_y + self.offset_y)
            self.draw_board(player, opponent, board)  # Met à jour l'affichage
            if (pos_y-self.card_size[1]+10 <= player_cards[self.dragging].posy) and (player_cards[self.dragging].posy <= pos_y+taille_borne[1]-10):
                num_board = (player_cards[self.dragging].posx // (WIDTH//9) ) % 9
                if len(board.board[num_board][0]) <3 and num_board not in board.borne_won:
                    couleur = (0,255,0)
                    self.surbrillance(num_board, couleur)
                else:
                    couleur = (255,0,0)
                    self.surbrillance(num_board, couleur)

            self.draw_player_cards(player_cards)

        # Relâchement de la carte
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging is not None:
            if (pos_y-self.card_size[1]+10 <= player_cards[self.dragging].posy) and (player_cards[self.dragging].posy <= pos_y+taille_borne[1]-10):
                num_board = (player_cards[self.dragging].posx // (WIDTH//9) ) % 9
                if board.ajoute_carte_board(num_board, player_cards[self.dragging], player.num):
                    player.retire_carte(player_cards[self.dragging])
                    self.dragging = None
                    return True, num_board, couleur
                else:
                    player_cards[self.dragging].resetPos()
                    self.dragging = None  # Fin du déplacement
            else:
                player_cards[self.dragging].resetPos()
                self.dragging = None  # Fin du déplacement
        
        return (False, num_board, couleur)
        
    
    def draw_flag_win(self, player, opponent):
        for flag in player.flag:
            self.surbrillance(flag, (20,20,255))
        for flag in opponent.flag:
            self.surbrillance(flag, (255,20,20))

        
    def draw_background(self):
        background_color =  (255, 182, 193)
        self.screen.fill(background_color)
    
    def to_string(self, board):
        # Parcours les lignes du tableau (9 lignes)
        result = ""
        for i in range(9):
            # On affiche chaque ligne avec ses deux listes à l'intérieur
            result += f"Row {i+1}: "
            for j in range(2):
                if j == 1:
                    result += "|"
                for k in range(len(board[i][j])):
                    result += f"{board[i][j][k].num} "
            result += "\n"
        print(result)

