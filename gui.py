# gui.py
import pygame
import sys
from board import JunqiBoard

# --- Side-by-Side Configuration Constants ---
BOARD_WIDTH = 550
PANEL_WIDTH = 400
WINDOW_WIDTH = BOARD_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = 650  

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
LINE_COLOR = (120, 120, 120)
IRON_BLOCK = (100, 100, 110) # Color for Face-Down pieces

class JunqiEngineDashboard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Junqi - Game Engine")
        
        self.x_start = 90
        self.y_start = 60
        self.x_spacing = 90
        self.y_spacing = 45
        self.river_gap = 30

        self.pieces_data = [
            ["司令", 9, 1, "Field Marshal"],
            ["军长", 8, 1, "General"],
            ["师长", 7, 2, "Div General"],
            ["旅长", 6, 2, "Brig General"],
            ["团长", 5, 2, "Colonel"],
            ["营长", 4, 2, "Major"],
            ["连长", 3, 3, "Captain"],
            ["排长", 2, 3, "Lieutenant"],
            ["工兵", 1, 3, "Engineer"],
            ["炸弹", 0, 2, "Bomb"], 
            ["地雷", 0, 3, "Mine"],
            ["军旗", 0, 1, "Flag"]
        ]
        
        self.counts = {
            "P1": {item[0]: item[2] for item in self.pieces_data},
            "P2": {item[0]: item[2] for item in self.pieces_data}
        }
        
        # --- PHASE 1: MASTER STATE VARIABLES ---
        self.game_phase = "SETUP" # Can be "SETUP" or "BATTLE"
        self.current_player = "P1" 
        self.held_piece = None  
        self.log_message = "P1 Turn: Select a piece to deploy."
        self.valid_spots = []  

        self.font_main = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_large = pygame.font.Font(None, 32)

        self.board = JunqiBoard()
        self._pre_initialize_full_terrain()
        
        self.viewer_zones = self._generate_board_hitboxes()
        self.action_button_zones = self._generate_panel_buttons()
        
        # UI Buttons
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
                px_x = self.x_start + (x * self.x_spacing)
                px_y = self.y_start + (draw_y_vis * self.y_spacing)
                if draw_y_vis > 5: px_y += self.river_gap
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = (px_x, px_y)
                hitboxes[(x, y)] = rect  
        return hitboxes

    def _generate_panel_buttons(self):
        zones = {}
        y_offset = 110
        line_height = 36
        btn_x = BOARD_WIDTH + 270
        for item in self.pieces_data:
            zones[item[0]] = pygame.Rect(btn_x, y_offset - 5, 70, 28)
            y_offset += line_height
        return zones

    def is_deployment_complete(self):
        """Checks if both players have placed all 25 pieces."""
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

    def draw_viewer_component(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, BOARD_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, LIGHT_GRAY, (BOARD_WIDTH, 0), (BOARD_WIDTH, WINDOW_HEIGHT), 4)
        
        title = self.font_large.render("Junqi Battlefield", True, RED)
        self.screen.blit(title, (20, 10))
        
        p2_label = self.font_small.render("P2 Territory", True, DARK_GRAY)
        self.screen.blit(p2_label, (20, 40))
        p1_label = self.font_small.render("P1 Territory", True, DARK_GRAY)
        self.screen.blit(p1_label, (20, WINDOW_HEIGHT - 30))

        # Lines
        for (x, y), rect in self.viewer_zones.items():
            if x < 4:
                right_rect = self.viewer_zones[(x + 1, y)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, right_rect.center, 2)
            if y < 11 and y != 5:
                up_rect = self.viewer_zones[(x, y + 1)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, up_rect.center, 2)

        # Nodes
        for (x, y), rect in self.viewer_zones.items():
            node = self.board.graph[(x, y)]
            terrain_type = node["type"]
            piece = node["piece"]

            # Draw Terrain Base
            if terrain_type == "Camp":
                pygame.draw.circle(self.screen, DARK_GRAY, rect.center, 20, 2)
            elif terrain_type == "HQ":
                t_rect = pygame.Rect(0, 0, 46, 26)
                t_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, t_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, t_rect, 2)
            else:
                t_rect = pygame.Rect(0, 0, 36, 22)
                t_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, t_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, t_rect, 2)

            # Valid Spot Highlight (Only in SETUP)
            if self.game_phase == "SETUP" and self.held_piece and (x, y) in self.valid_spots:
                s = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 150), (20, 20), 18)
                self.screen.blit(s, (rect.centerx - 20, rect.centery - 20))
                
            # --- PHASE 1: FOG OF WAR DRAWING LOGIC ---
            if piece:
                s = pygame.Surface((44, 26), pygame.SRCALPHA)
                
                # Check if we should hide the piece
                is_face_down = False
                if self.game_phase == "BATTLE" and piece.player != self.current_player:
                    is_face_down = True
                
                if is_face_down:
                    # Draw a solid iron block
                    pygame.draw.rect(s, IRON_BLOCK, (0,0,44,26), border_radius=3)
                    pygame.draw.rect(s, WHITE, (0,0,44,26), 1, border_radius=3)
                    self.screen.blit(s, (rect.centerx - 22, rect.centery - 13))
                else:
                    # Draw normal piece (Blue for P1, Red for P2)
                    color = (50, 100, 200, 220) if piece.player == "P1" else (200, 50, 50, 220)
                    pygame.draw.rect(s, color, (0,0,44,26), border_radius=3)
                    pygame.draw.rect(s, WHITE, (0,0,44,26), 1, border_radius=3)
                    self.screen.blit(s, (rect.centerx - 22, rect.centery - 13))
                    
                    # Add English text
                    rank = next((item[1] for item in self.pieces_data if item[0] == piece.name), 0)
                    if piece.name == "军旗": display_str = "Flag"
                    elif piece.name == "地雷": display_str = "Mine"
                    elif piece.name == "炸弹": display_str = "Bomb"
                    else: display_str = f"R{rank}"
                    
                    p_text = self.font_small.render(display_str, True, WHITE)
                    p_rect = p_text.get_rect(center=rect.center)
                    self.screen.blit(p_text, p_rect)

    def draw_panel_component(self):
        pygame.draw.rect(self.screen, DARK_GRAY, (BOARD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT))

        # --- PHASE 1: SETUP PANEL ---
        if self.game_phase == "SETUP":
            btn_color = BLUE if self.current_player == "P1" else RED
            pygame.draw.rect(self.screen, btn_color, self.btn_switch_player, border_radius=6)
            btn_txt = self.font_main.render(f"Deploying: {self.current_player} (Click to Switch)", True, WHITE)
            self.screen.blit(btn_txt, btn_txt.get_rect(center=self.btn_switch_player.center))

            headers = [f"Piece ({self.current_player})", "Tier", "Qty", "Action"]
            header_positions = [BOARD_WIDTH + 20, BOARD_WIDTH + 140, BOARD_WIDTH + 210, BOARD_WIDTH + 270]
            header_y = 80
            for i, h in enumerate(headers):
                h_text = self.font_small.render(h, True, LIGHT_GRAY)
                self.screen.blit(h_text, (header_positions[i], header_y))

            y_offset = 110
            line_height = 36
            for item in self.pieces_data:
                name, tier, _, desc = item
                count = self.counts[self.current_player][name]
                
                name_text = self.font_main.render(desc, True, WHITE)
                self.screen.blit(name_text, (BOARD_WIDTH + 20, y_offset))
                tier_str = f"Rank {tier}" if tier > 0 else "Special"
                tier_text = self.font_small.render(tier_str, True, LIGHT_GRAY)
                self.screen.blit(tier_text, (BOARD_WIDTH + 140, y_offset + 3))
                count_text = self.font_main.render(str(count), True, WHITE)
                self.screen.blit(count_text, (BOARD_WIDTH + 220, y_offset))

                btn_rect = self.action_button_zones[name]
                if self.held_piece == name:
                    pygame.draw.rect(self.screen, GREEN, btn_rect, border_radius=4)
                    btn_txt = "Held"
                elif count > 0:
                    pygame.draw.rect(self.screen, LIGHT_GRAY, btn_rect, border_radius=4)
                    pygame.draw.rect(self.screen, BLACK, btn_rect, 1, border_radius=4)
                    btn_txt = "Select"
                else:
                    pygame.draw.rect(self.screen, (100,100,100), btn_rect, border_radius=4)
                    btn_txt = "-"

                btn_label = self.font_small.render(btn_txt, True, BLACK)
                self.screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))
                y_offset += line_height

            # Display START BATTLE Button if ready
            if self.is_deployment_complete():
                pygame.draw.rect(self.screen, GREEN, self.btn_start_battle, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, self.btn_start_battle, 2, border_radius=6)
                start_txt = self.font_large.render("START BATTLE", True, BLACK)
                self.screen.blit(start_txt, start_txt.get_rect(center=self.btn_start_battle.center))

        # --- PHASE 1: BATTLE PANEL ---
        elif self.game_phase == "BATTLE":
            title_text = self.font_large.render("BATTLE PHASE", True, RED)
            self.screen.blit(title_text, (BOARD_WIDTH + 20, 20))
            
            # The End Turn Button
            btn_color = BLUE if self.current_player == "P1" else RED
            pygame.draw.rect(self.screen, btn_color, self.btn_switch_player, border_radius=6)
            pygame.draw.rect(self.screen, WHITE, self.btn_switch_player, 2, border_radius=6)
            btn_txt = self.font_main.render(f"End Turn (Pass to { 'P2' if self.current_player == 'P1' else 'P1' })", True, WHITE)
            self.screen.blit(btn_txt, btn_txt.get_rect(center=self.btn_switch_player.center))

            info_text = self.font_main.render("Movement Engine Pending...", True, LIGHT_GRAY)
            self.screen.blit(info_text, (BOARD_WIDTH + 20, 150))

        # Universal Log Message
        log_text = self.font_main.render(self.log_message, True, WHITE)
        self.screen.blit(log_text, (BOARD_WIDTH + 20, WINDOW_HEIGHT - 40))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_viewer_component()
        self.draw_panel_component()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_events(pygame.mouse.get_pos())
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self, pos):
        # ----------------------------------------------------
        # SETUP PHASE INPUTS
        # ----------------------------------------------------
        if self.game_phase == "SETUP":
            # 1. Switch Player
            if self.btn_switch_player.collidepoint(pos):
                self.current_player = "P2" if self.current_player == "P1" else "P1"
                self.held_piece = None
                self.valid_spots = []
                self.log_message = f"{self.current_player} Turn: Select a piece."
                return

            # 2. Start Battle
            if self.is_deployment_complete() and self.btn_start_battle.collidepoint(pos):
                self.game_phase = "BATTLE"
                self.current_player = "P1" # P1 always goes first
                self.held_piece = None
                self.log_message = "BATTLE COMMENCED! P1 to move."
                return

            # 3. Panel Clicks
            for name, rect in self.action_button_zones.items():
                if rect.collidepoint(pos):
                    if self.held_piece == name:
                        self.held_piece = None
                        self.log_message = "Deselected piece."
                        self.valid_spots = []
                    elif self.counts[self.current_player][name] > 0:
                        self.held_piece = name
                        desc = next(item[3] for item in self.pieces_data if item[0] == name)
                        self.log_message = f"Holding {desc}. Click a valid spot."
                        self.valid_spots = self.get_valid_deployment_spots(name)
                    return 

            # 4. Board Clicks
            if self.held_piece:
                for (x, y), rect in self.viewer_zones.items():
                    if rect.collidepoint(pos):
                        if (x, y) in self.valid_spots:
                            from pieces import Piece
                            self.board.graph[(x, y)]["piece"] = Piece(self.current_player, self.held_piece)
                            self.counts[self.current_player][self.held_piece] -= 1
                            
                            desc = next(item[3] for item in self.pieces_data if item[0] == self.held_piece)
                            self.log_message = f"Deployed {desc} to ({x}, {y})"
                            self.held_piece = None
                            self.valid_spots = []
                        return 

            # 5. Deselect
            if self.held_piece and pos[0] < BOARD_WIDTH:
                self.held_piece = None
                self.log_message = "Deselected piece."
                self.valid_spots = []

        # ----------------------------------------------------
        # BATTLE PHASE INPUTS
        # ----------------------------------------------------
        elif self.game_phase == "BATTLE":
            # 1. End Turn Button
            if self.btn_switch_player.collidepoint(pos):
                self.current_player = "P2" if self.current_player == "P1" else "P1"
                self.log_message = f"{self.current_player}'s Turn. (Fog of War updated)"
                return
                
            # 2. Clicking pieces on the board
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
    dashboard = JunqiEngineDashboard()
    dashboard.run()