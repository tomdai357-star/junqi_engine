# gui.py
import pygame
import sys
from board import JunqiBoard

# --- Configuration Constants ---
WINDOW_WIDTH = 580
BOARD_HEIGHT = 650  # Taller to fit 12 rows
PANEL_HEIGHT = 220  
WINDOW_HEIGHT = BOARD_HEIGHT + PANEL_HEIGHT

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

class JunqiEngineDashboard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Junqi - Full Deployment Phase")
        
        self.x_start = 100
        self.y_start = 30
        self.x_spacing = 95
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
        
        # Track both players' inventories
        self.counts = {
            "P1": {item[0]: item[2] for item in self.pieces_data},
            "P2": {item[0]: item[2] for item in self.pieces_data}
        }
        self.current_player = "P1"

        self.font_main = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_large = pygame.font.Font(None, 32)

        self.board = JunqiBoard()
        self._pre_initialize_full_terrain()
        
        self.held_piece = None  
        self.log_message = "P1 Turn: Select a piece to deploy."
        self.valid_spots = []  

        self.viewer_zones = self._generate_board_hitboxes()
        self.panel_zones = self._generate_panel_buttons()
        
        # Player Switch Button Zone
        self.btn_switch_player = pygame.Rect(WINDOW_WIDTH - 150, BOARD_HEIGHT - 40, 130, 30)

    def _pre_initialize_full_terrain(self):
        """Sets up the perfect 5-camp cross pattern for both P1 and P2."""
        for y in range(12):
            for x in range(5):
                node = self.board.graph[(x, y)]
                node["piece"] = None
                
                # Headquarters
                if y in (0, 11) and x in (1, 3):
                    node["type"] = "HQ"
                # P1 Camps (5 per side in a cross)
                elif y in (1, 3) and x in (1, 3): node["type"] = "Camp"
                elif y == 2 and x == 2: node["type"] = "Camp"
                # P2 Camps (5 per side in a cross)
                elif y in (8, 10) and x in (1, 3): node["type"] = "Camp"
                elif y == 9 and x == 2: node["type"] = "Camp"
                # Everything else
                else:
                    node["type"] = "Post"

    def _generate_board_hitboxes(self):
        """Maps all 12 rows, maintaining the 180-degree visual inversion."""
        hitboxes = {}
        for y in range(12):  
            for x in range(5):
                draw_y_vis = 11 - y 
                
                px_x = self.x_start + (x * self.x_spacing)
                px_y = self.y_start + (draw_y_vis * self.y_spacing)
                
                # Add the River Gap if this node is in P1's visual half (bottom)
                if draw_y_vis > 5:
                    px_y += self.river_gap
                    
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = (px_x, px_y)
                hitboxes[(x, y)] = rect  
        return hitboxes

    def _generate_panel_buttons(self):
        zones = {}
        btn_width = 110
        btn_height = 40
        padding_x = 20
        padding_y = 15
        start_x = 25
        start_y = BOARD_HEIGHT + 20 
        
        col, row = 0, 0
        for item in self.pieces_data:
            name = item[0]
            px = start_x + col * (btn_width + padding_x)
            py = start_y + row * (btn_height + padding_y)
            zones[name] = pygame.Rect(px, py, btn_width, btn_height)
            col += 1
            if col > 3: 
                col, row = 0, row + 1
        return zones

    def get_valid_deployment_spots(self, piece_name):
        """Controller logic strictly enforces territories based on active player."""
        valid_spots = []
        for y in range(12):  
            for x in range(5):
                node = self.board.graph[(x, y)]
                if node["piece"] is not None or node["type"] == "Camp":
                    continue
                    
                # TERRITORY LOCKOUT
                if self.current_player == "P1" and y > 5: continue
                if self.current_player == "P2" and y < 6: continue
                
                # PIECE SPECIFIC RULES
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
        pygame.draw.rect(self.screen, BLACK, (0, 0, WINDOW_WIDTH, BOARD_HEIGHT))
        
        # UI Titles
        title = self.font_large.render("Junqi Battlefield", True, RED)
        self.screen.blit(title, (20, 10))
        
        p2_label = self.font_small.render("P2 Territory (Rows 6-11)", True, DARK_GRAY)
        self.screen.blit(p2_label, (20, 40))
        p1_label = self.font_small.render("P1 Territory (Rows 0-5)", True, DARK_GRAY)
        self.screen.blit(p1_label, (20, BOARD_HEIGHT - 30))

        # Draw Lines
        for (x, y), rect in self.viewer_zones.items():
            if x < 4:
                right_rect = self.viewer_zones[(x + 1, y)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, right_rect.center, 2)
            if y < 11 and y != 5: # Don't draw vertical lines across the river!
                up_rect = self.viewer_zones[(x, y + 1)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, up_rect.center, 2)

        # Draw Nodes
        for (x, y), rect in self.viewer_zones.items():
            node = self.board.graph[(x, y)]
            terrain_type = node["type"]
            piece = node["piece"]

            if terrain_type == "Camp":
                pygame.draw.circle(self.screen, DARK_GRAY, rect.center, 20, 2)
                t_text = self.font_small.render("Camp", True, LIGHT_GRAY)
            elif terrain_type == "HQ":
                t_rect = pygame.Rect(0, 0, 46, 26)
                t_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, t_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, t_rect, 2)
                t_text = self.font_small.render("HQ", True, LIGHT_GRAY)
            else:
                t_rect = pygame.Rect(0, 0, 36, 22)
                t_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, t_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, t_rect, 2)
                t_text = self.font_small.render("Post", True, LIGHT_GRAY)

            t_text_rect = t_text.get_rect(center=rect.center)
            self.screen.blit(t_text, t_text_rect)

            if self.held_piece and (x, y) in self.valid_spots:
                s = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 150), (20, 20), 18)
                self.screen.blit(s, (rect.centerx - 20, rect.centery - 20))
                
            if piece:
                s = pygame.Surface((44, 26), pygame.SRCALPHA)
                # Color code pieces by owner
                color = (50, 100, 200, 220) if piece.player == "P1" else (200, 50, 50, 220)
                pygame.draw.rect(s, color, (0,0,44,26), border_radius=3)
                pygame.draw.rect(s, WHITE, (0,0,44,26), 1, border_radius=3)
                self.screen.blit(s, (rect.centerx - 22, rect.centery - 13))
                
                rank = next((item[1] for item in self.pieces_data if item[0] == piece.name), 0)
                if piece.name == "军旗": display_str = "Flag"
                elif piece.name == "地雷": display_str = "Mine"
                elif piece.name == "炸弹": display_str = "Bomb"
                else: display_str = f"R{rank}"
                
                p_text = self.font_small.render(display_str, True, WHITE)
                p_rect = p_text.get_rect(center=rect.center)
                self.screen.blit(p_text, p_rect)

        # Draw Switch Button
        btn_color = BLUE if self.current_player == "P1" else RED
        pygame.draw.rect(self.screen, btn_color, self.btn_switch_player, border_radius=4)
        btn_txt = self.font_small.render(f"Deploying: {self.current_player}", True, WHITE)
        self.screen.blit(btn_txt, btn_txt.get_rect(center=self.btn_switch_player.center))

    def draw_panel_component(self):
        panel_bg = pygame.Rect(0, BOARD_HEIGHT, WINDOW_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_bg)
        pygame.draw.line(self.screen, LIGHT_GRAY, (0, BOARD_HEIGHT), (WINDOW_WIDTH, BOARD_HEIGHT), 4)

        log_text = self.font_main.render(self.log_message, True, WHITE)
        self.screen.blit(log_text, (WINDOW_WIDTH - 300, BOARD_HEIGHT + PANEL_HEIGHT - 30))

        headers = [f"Piece ({self.current_player})", "Tier", "Qty", "Action"]
        header_positions = [25, 170, 250, 310]
        header_y = BOARD_HEIGHT + 10
        for i, h in enumerate(headers):
            h_text = self.font_small.render(h, True, LIGHT_GRAY)
            self.screen.blit(h_text, (header_positions[i], header_y))

        y_offset = BOARD_HEIGHT + 30
        line_height = 28

        for item in self.pieces_data:
            name, tier, _, desc = item
            # Pull from the active player's inventory
            count = self.counts[self.current_player][name]
            
            name_text = self.font_main.render(desc, True, WHITE)
            self.screen.blit(name_text, (25, y_offset))
            
            tier_str = f"Rank {tier}" if tier > 0 else "Special"
            tier_text = self.font_small.render(tier_str, True, LIGHT_GRAY)
            self.screen.blit(tier_text, (170, y_offset + 3))
            
            count_text = self.font_main.render(str(count), True, WHITE)
            self.screen.blit(count_text, (250, y_offset))

            btn_rect = pygame.Rect(310, y_offset - 2, 80, 20)
            
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
            
            zones = getattr(self, "action_button_zones", {})
            zones[name] = btn_rect
            setattr(self, "action_button_zones", zones)

            y_offset += line_height

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
        # 1. Switch Player Button
        if self.btn_switch_player.collidepoint(pos):
            self.current_player = "P2" if self.current_player == "P1" else "P1"
            self.held_piece = None # Drop piece when switching
            self.valid_spots = []
            self.log_message = f"{self.current_player} Turn: Select a piece."
            return

        # 2. UI Panel Buttons
        zones = getattr(self, "action_button_zones", {})
        for name, rect in zones.items():
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

        # 3. Board Click Placement
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

        # 4. Click out of bounds
        if self.held_piece and not any(r.collidepoint(pos) for r in self.viewer_zones.values()):
            self.held_piece = None
            self.log_message = "Deselected piece."
            self.valid_spots = []

if __name__ == "__main__":
    dashboard = JunqiEngineDashboard()
    dashboard.run()