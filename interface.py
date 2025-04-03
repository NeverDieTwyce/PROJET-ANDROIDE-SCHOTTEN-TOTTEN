import pygame
import numpy as np
import time

# Dimensions de la fenêtre de jeu
WIDTH, HEIGHT = 1000, 700

class Interface:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.card_size = (90, 80)  # taille des cartes
        self.dragging = None  # Index de la carte en cours de déplacement
        self.offset_x = 0
        self.offset_y = 0
        self.nb_tour = 0
        self.hovered_borne = None
        # Positions des cartes du joueur
        self.card_positions = [(50 + i * (self.card_size[0] - 20), 
                              HEIGHT - self.card_size[1] - 50) 
                              for i in range(6)]


    # affiche tous les éléments graphique du jeu
    def draw_board(self, player, opponent, board):
        self.draw_background()
        self.affiche_pioche(board.index_pioche)
        self.draw_borne()
        self.surbrillance()
        self.draw_won_borne(player)
        self.draw_won_borne(opponent)
        self.draw_opponent_cards(opponent.main)
        self.draw_card_on_board(board.borne_nums, board.borne_colors)
        self.draw_player_cards(player.main)
        pygame.display.flip()


    # affiche les cartes du joueurs
    def draw_player_cards(self, cards):
        for i, card in enumerate(cards):
            if card['num'] != -1:  # Si l'emplacement n'est pas vide
                img_path = f"cartes/carte_{card['couleur']}/{card['num']}_{card['couleur']}.png"
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, self.card_size)
                self.screen.blit(img, (self.card_positions[i][0], self.card_positions[i][1]))
    

    # affiches les cartes de l'adversaire, caché bien évidemment
    def draw_opponent_cards(self, cards):
        for i, card in enumerate(cards):
            if card['num'] != -1:
                img = pygame.image.load("cartes/dos_carte.png").convert_alpha()
                img = pygame.transform.scale(img, self.card_size)
                x = WIDTH - self.card_size[0] - 50 - i * (self.card_size[0] - 20)
                y = 50
                self.screen.blit(img, (x, y))
    
    # affiche les bornes
    def draw_borne(self):
        for i in range(9):
            img = pygame.image.load(f"cartes/flag{i%3}.png").convert_alpha()
            img = pygame.transform.scale(img, self.card_size)
            x = 30 + i * (self.card_size[0] + 15)
            y = HEIGHT//2 - self.card_size[0]/2
            self.screen.blit(img, (x, y))


    # dessine l'arrière plan, ici on a choisi du rose clair
    def draw_background(self):
        self.screen.fill((255, 182, 193))  # Rose clair

    # Permet le déplacement des cartes du joueur
    # joue la carte déplacé 
    def drag_drop(self, event, player, board):
        """Gère le drag-and-drop des cartes"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        moved = False
        borne_idx = -1
        color = ''
        borne_y = HEIGHT//2 - self.card_size[0]/2  # Position Y des bornes

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifie si le clic est sur une carte du joueur
            for i, (x, y) in enumerate(self.card_positions):
                if (x <= mouse_x <= x + self.card_size[0] and 
                    y <= mouse_y <= y + self.card_size[1] and 
                    player.main[i]['num'] != -1):
                    self.dragging = i
                    self.offset_x = x - mouse_x
                    self.offset_y = y - mouse_y
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging is not None:
            # Déplace la carte avec la souris
            new_x = mouse_x + self.offset_x
            new_y = mouse_y + self.offset_y
            self.card_positions[self.dragging] = (new_x, new_y)
            if self.dragging is not None:
                # Calcul de la borne survolée pendant le drag
                self.hovered_borne = None
                if (borne_y <= mouse_y <= borne_y + self.card_size[1]):
                    borne_idx = int((mouse_x - 30) // (self.card_size[0] + 15))
                    self.hovered_borne = max(0, min(8, borne_idx))

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging is not None:
            # Vérifie si le drop est sur une borne
            card_x, card_y = self.card_positions[self.dragging]
            if (borne_y <= card_y <= borne_y + self.card_size[1]):
                # Calcule l'index de la borne
                borne_idx = int((mouse_x - 30) // (self.card_size[0] + 15))
                borne_idx = max(0, min(8, borne_idx))  # Clamp entre 0-8
                
                # Récupère les infos de la carte
                carte = player.main[self.dragging]
                success = board.ajouter_carte(0, borne_idx, (carte['num'], carte['couleur']))
                
                if success:
                    # Supprime la carte jouée
                    carte = player.main[self.dragging]
                    player.retire_carte(carte)
                    color = carte['couleur']
                    moved = True

            # Réinitialise la position de la carte
            self.card_positions[self.dragging] = (
                50 + self.dragging * (self.card_size[0] - 20),
                HEIGHT - self.card_size[1] - 50
            )
            self.dragging = None
            self.hovered_borne = None

        return moved, borne_idx, color

    # Affiche les cartes posées sur toutes les bornes
    def draw_card_on_board(self, board_nums, board_colors):
        borne_spacing = self.card_size[0] + 15  # Espacement entre les bornes
        base_y = HEIGHT // 2 - self.card_size[1] // 2 - 15  # Position Y centrale
        
        for borne_idx in range(9):
            # Position X de la borne
            x = 15 + borne_idx * borne_spacing
            
            # Cartes du joueur 0 (en bas)
            for k in range(3):
                num = board_nums[borne_idx, 0, k]
                color = board_colors[borne_idx, 0, k]
                if num != -1:
                    img = pygame.image.load(f"cartes/carte_{color}/{num}_{color}.png").convert_alpha()
                    img = pygame.transform.scale(img, self.card_size)
                    y_offset = base_y + 90 + k * (self.card_size[1] // 2)
                    self.screen.blit(img, (x + 15, y_offset))
                   
            
            # Cartes du joueur 1 (en haut)
            for k in range(2,-1,-1):
                num = board_nums[borne_idx, 1, k]
                color = board_colors[borne_idx, 1, k]
                if num != -1:
                    img = pygame.image.load(f"cartes/carte_{color}/{num}_{color}.png").convert_alpha()
                    img = pygame.transform.scale(img, self.card_size)
                    y_offset = base_y - self.card_size[1] - k * (self.card_size[1] // 2) + 10
                    self.screen.blit(img, (x + 15, y_offset))
    

    # Dessine une surbrillance autour de la borne survolée ( en vert )
    def surbrillance(self, color=(0,255,0)):
        if self.hovered_borne is not None:
            borne_spacing = self.card_size[0] + 15
            x = 30 + self.hovered_borne * borne_spacing
            y = HEIGHT//2 - self.card_size[0]/2
            pygame.draw.rect(self.screen, color, (x, y, self.card_size[0], self.card_size[1]), 3)

    # Colorie les bornes gagnées par le joueur en bleu, et celle de l'adversaire en rouge
    def draw_won_borne(self, player):
        if player.num == 0:
            color = (0,0,255)
        else:
            color = (255,0,0)
        for flag in player.won:
            borne_spacing = self.card_size[0] + 15
            x = 30 + flag * borne_spacing
            y = HEIGHT//2 - self.card_size[0]/2
            pygame.draw.rect(self.screen, color, (x, y, self.card_size[0], self.card_size[1]), 3)     
    

    def affiche_pioche(self, index_pioche):
        nb_carte_rest = "Pioche " + str(54 - index_pioche)
        couleur_texte = (255, 255, 255)  # Blanc
        couleur_contour = (0, 0, 0)  # Noir
        font = pygame.font.Font(None, 26)
        
        x, y = 60, 50

        # Rendre le texte principal
        texte = font.render(nb_carte_rest, True, couleur_texte)

        # Charger et afficher les cartes de la pioche
        img = pygame.image.load("cartes/dos_carte.png").convert()
        img = pygame.transform.scale(img, self.card_size)
      
        for i in range(max((54 - index_pioche)//5, 1)):  # Empiler 4 cartes
            self.screen.blit(img, (x + (5-i) * 5, y))
            last_x = x + (5-i) * 5

        texte_rect = texte.get_rect(center=(last_x+45, y+40))  # Centrer sur (x+45, y+40)
        # Rendre le contour en le dessinant autour du texte
        decalages = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)]
        for dx, dy in decalages:
            texte_contour = font.render(nb_carte_rest, True, couleur_contour)
            self.screen.blit(texte_contour, texte_rect.move(dx, dy))

        # Dessiner le texte principal au-dessus du contour
        self.screen.blit(texte, texte_rect)

    def justif(self, num, val):
        text = "La meilleur combinaison sur la borne " + str(num) +" était "
        if val[0] == 0:
            text += "une Horde Sauvage"
        elif val[0] == 1:
            text += "une Suite"
        elif val[0] == 2:
            text += "une Couleur"
        elif val[0] == 3:
            text += "un Brelan"
        elif val[0] == 4:
            text += "une Suite Couleur"
        
        text += " de valeur  " + str(val[1]+1)

        self.show_text_popup(text)
            
    


    def show_text_popup(self, text, position=(100, 100), size=(800, 100)):
        """Affiche et gère un popup fermable"""
        # 1. Sauvegarde de l'écran sous le popup
        screenshot = self.screen.copy()
        
        # 2. Création du popup
        popup_rect = pygame.Rect(position[0], position[1], size[0], size[1])
        
        # Couleurs
        BACKGROUND = (240, 240, 245)
        BORDER = (50, 50, 80)
        
        # 3. Boucle du popup
        popup_active = True
        while popup_active:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
                # Fermeture par:
                # - Clic dans le popup
                # - Touche ESC/ENTREE/ESPACE
                if (event.type == pygame.MOUSEBUTTONDOWN and 
                    popup_rect.collidepoint(event.pos)) or \
                (event.type == pygame.KEYDOWN and 
                    event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)):
                    popup_active = False
            
            # Dessin
            self.screen.blit(screenshot, (0, 0))  # Restaure le fond
            pygame.draw.rect(self.screen, BACKGROUND, popup_rect)
            pygame.draw.rect(self.screen, BORDER, popup_rect, 2)
            
            # Texte
            font = pygame.font.Font(None, 28)
            y_offset = position[1] + 20
            for line in text.split('\n'):
                text_surf = font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surf, (position[0] + 20, y_offset))
                y_offset += 30
            
            # Bouton de fermeture (optionnel)
            close_rect = pygame.Rect(
                position[0] + size[0] - 40, 
                position[1] + 10, 
                30, 30
            )
            pygame.draw.rect(self.screen, (255, 100, 100), close_rect)
            pygame.draw.line(self.screen, (255,255,255), (close_rect.x+5, close_rect.y+5), 
                            (close_rect.x+25, close_rect.y+25), 2)
            pygame.draw.line(self.screen, (255,255,255), (close_rect.x+25, close_rect.y+5), 
                            (close_rect.x+5, close_rect.y+25), 2)
            
            pygame.display.flip()
            pygame.time.delay(30)
        
        return True
    
   
    def afficher_chargement(self,duree_secondes, texte="Attente du tour adverse..."):
        """
        Affiche une barre de chargement qui se remplit progressivement
        avec un texte centré pendant une durée déterminée.
        
        Args:
            screen: Surface Pygame où dessiner
            duree_secondes: Durée totale du chargement
            texte: Message à afficher
        """
        # Paramètres visuels
        largeur, hauteur = self.screen.get_size()
        barre_largeur = largeur * 0.6  # 60% de la largeur de l'écran
        barre_hauteur = 30
        barre_x = (largeur - barre_largeur) // 2
        barre_y = hauteur * 0.7  # 70% de la hauteur
        
        couleur_fond = (50, 50, 80)
        couleur_barre = (100, 200, 100)
        couleur_texte = (240, 240, 240)
        
        font = pygame.font.Font(None, 36)
        
        debut = time.time()
        progression = 0.0
        
        while progression < 1.0:
            # Calcul de la progression
            temps_ecoule = time.time() - debut
            progression = min(temps_ecoule / duree_secondes, 1.0)
            
            # Gestion des événements (pour ne pas bloquer)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Effacer l'écran (ou dessiner par-dessus l'état actuel)
            # screen.fill((0, 0, 0))  # Décommenter pour fond noir
            
            # Dessiner la barre de fond
            pygame.draw.rect(self.screen, couleur_fond, 
                            (barre_x, barre_y, barre_largeur, barre_hauteur))
            
            # Dessiner la partie remplie
            largeur_remplie = int(barre_largeur * progression)
            pygame.draw.rect(self.screen, couleur_barre, 
                            (barre_x, barre_y, largeur_remplie, barre_hauteur))
            
            # Contour de la barre
            pygame.draw.rect(self.screen, (200, 200, 200), 
                            (barre_x, barre_y, barre_largeur, barre_hauteur), 2)
            
            # Afficher le texte centré
            texte_surface = font.render(texte, True, couleur_texte)
            texte_rect = texte_surface.get_rect(center=(largeur//2, hauteur//2))
            self.screen.blit(texte_surface, texte_rect)
            
            # Pourcentage (optionnel)
            pourcentage = int(progression * 100)
            pourcent_surface = font.render(f"{pourcentage}%", True, couleur_texte)
            self.screen.blit(pourcent_surface, 
                    (barre_x + barre_largeur + 10, barre_y))
            
            pygame.display.flip()
            pygame.time.delay(30)  # Limite à ~30 FPS