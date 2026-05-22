# main.py
import pygame
import sys
from settings import *
from board import JunqiBoard
from pieces import Piece
from renderer import JunqiRenderer

class JunqiEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Junqi - Game Engine")
        
        # Attach our external rendering class
        self.renderer = JunqiRenderer(self.screen)
        
        self.counts = {
            "P1": {item[0]: item[2] for item in PIECES_DATA},
            "P2": {item[0]: item[2] for item in PIECES_DATA}
        }
        
        self.game_phase = "SETUP" 
        self.current_player = "P1" 
        self.held_piece = None  
        self.log_message = "P1 Turn: Select a piece to deploy."
        self.valid_spots = []  

        self.board = JunqiBoard()
        self._pre_initialize_full_terrain()
        
        self.viewer_zones = self._generate_board_hitboxes()
        self.action_button_zones = self._generate_panel_buttons()
        
        self.btn_switch_player = pygame.Rect(BOARD_WIDTH + 20, 20, PANEL_WIDTH - 40, 40)
        self.btn_start_battle = pygame.Rect(BOARD_WIDTH + 20, WINDOW_HEIGHT - 100, PANEL_WIDTH - 40, 40)

    def _pre_initialize_full_terrain(self):
        for y in range(12):
            for x in range(5):
                node = self.board.graph[(x, y)]
                node["piece"] = None
                if y in (0, 11) and x in (1, 3): node["type"] = "HQ"
                elif y in (2, 4) and x in (1, 3): node["type"] = "Camp"
                elif y == 3 and x == 2: node["type"] = "Camp"
                elif y in (7, 9) and x in (1, 3): node["type"] = "Camp"
                elif y == 8 and x == 2: node["type"] = "Camp"
                else: node["type"] = "Post"

    def _generate_board_hitboxes(self):
        hitboxes = {}
        for y in range(12):  
            for x in range(5):
                draw_y_vis = 11 - y 
                px_x = X_START + (x * X_SPACING)
                px_y = Y_START + (draw_y_vis * Y_SPACING)
                if draw_y_vis > 5: px_y += RIVER_GAP
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = (px_x, px_y)
                hitboxes[(x, y)] = rect  
        return hitboxes

    def _generate_panel_buttons(self):
        zones = {}
        y_offset = 110
        line_height = 36
        btn_x = BOARD_WIDTH + 270
        for item in PIECES_DATA:
            zones[item[0]] = pygame.Rect(btn_x, y_offset - 5, 70, 28)
            y_offset += line_height
        return zones

    def is_deployment_complete(self):
        p1_ready = sum(self.counts["P1"].values()) == 0
        p2_ready = sum(self.counts["P2"].values()) == 0
        return p1_ready and p2_ready

    def get_valid_deployment_spots(self, piece_name):
        valid_spots = []
        for y in range(12):  
            for x in range(5):
                node = self.board.graph[(x, y)]
                if node["piece"] is not None or node["type"] == "Camp": continue
                if self.current_player == "P1" and y > 5: continue
                if self.current_player == "P2" and y < 6: continue
                
                if piece_name == "军旗":
                    if node["type"] == "HQ": valid_spots.append((x, y))
                elif piece_name == "地雷":
                    if self.current_player == "P1" and y <= 1: valid_spots.append((x, y))
                    if self.current_player == "P2" and y >= 10: valid_spots.append((x, y))
                elif piece_name == "炸弹":
                    if self.current_player == "P1" and y < 5: valid_spots.append((x, y))
                    if self.current_player == "P2" and y > 6: valid_spots.append((x, y))
                else:
                    valid_spots.append((x, y))
        return valid_spots

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_events(pygame.mouse.get_pos())
            
            # Delegate all drawing to the renderer module
            self.renderer.draw(self)
            
        pygame.quit()
        sys.exit()

    def handle_events(self, pos):
        if self.game_phase == "SETUP":
            if self.btn_switch_player.collidepoint(pos):
                self.current_player = "P2" if self.current_player == "P1" else "P1"
                self.held_piece = None
                self.valid_spots = []
                self.log_message = f"{self.current_player} Turn: Select a piece."
                return

            if self.is_deployment_complete() and self.btn_start_battle.collidepoint(pos):
                self.game_phase = "BATTLE"
                self.current_player = "P1" 
                self.held_piece = None
                self.log_message = "BATTLE COMMENCED! P1 to move."
                return

            for name, rect in self.action_button_zones.items():
                if rect.collidepoint(pos):
                    if self.held_piece == name:
                        self.held_piece = None
                        self.log_message = "Deselected piece."
                        self.valid_spots = []
                    elif self.counts[self.current_player][name] > 0:
                        self.held_piece = name
                        desc = next(item[3] for item in PIECES_DATA if item[0] == name)
                        self.log_message = f"Holding {desc}. Click a valid spot."
                        self.valid_spots = self.get_valid_deployment_spots(name)
                    return 

            if self.held_piece:
                for (x, y), rect in self.viewer_zones.items():
                    if rect.collidepoint(pos):
                        if (x, y) in self.valid_spots:
                            self.board.graph[(x, y)]["piece"] = Piece(self.current_player, self.held_piece)
                            self.counts[self.current_player][self.held_piece] -= 1
                            
                            desc = next(item[3] for item in PIECES_DATA if item[0] == self.held_piece)
                            self.log_message = f"Deployed {desc} to ({x}, {y})"
                            self.held_piece = None
                            self.valid_spots = []
                        return 

            if self.held_piece and pos[0] < BOARD_WIDTH:
                self.held_piece = None
                self.log_message = "Deselected piece."
                self.valid_spots = []

        elif self.game_phase == "BATTLE":
            if self.btn_switch_player.collidepoint(pos):
                self.current_player = "P2" if self.current_player == "P1" else "P1"
                self.log_message = f"{self.current_player}'s Turn. (Fog of War updated)"
                return
                
            for (x, y), rect in self.viewer_zones.items():
                if rect.collidepoint(pos):
                    node = self.board.graph[(x, y)]
                    piece = node["piece"]
                    
                    if piece and piece.player == self.current_player:
                        self.log_message = f"Selected friendly piece at ({x}, {y}). Awaiting Movement Phase."
                    elif piece:
                        self.log_message = f"Clicked enemy piece. Cannot move."
                    else:
                        self.log_message = f"Clicked empty node at ({x}, {y})."
                    return

if __name__ == "__main__":
    engine = JunqiEngine()
    engine.run()
