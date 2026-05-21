# gui.py
import pygame
import sys
import platform
from board import JunqiBoard

# --- Configuration Constants ---
WINDOW_WIDTH = 580
BOARD_HEIGHT = 580  
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
        pygame.display.set_caption("Junqi - Deployment Phase (Strict MVC)")
        
        # Grid Math for Drawing (P1 Territory y=0 to y=5)
        self.x_start = 100
        self.y_start = 60
        self.spacing = 90

        # P1 Army Data Embedded for GUI Rendering 
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
            ["炸弹", 0, 2, "Bomb (Rankless)"], 
            ["地雷", 0, 3, "Landmine (Rankless)"],
            ["军旗", 0, 1, "Flag (Rankless)"]
        ]
        self.counts_dict = {item[0]: item[2] for item in self.pieces_data}

        # --- BULLETPROOF MAC FONT SETUP ---
        try:
            # Force Pygame to look at the exact macOS font file path
            mac_font_path = "/System/Library/Fonts/PingFang.ttc" 
            self.font_main = pygame.font.Font(mac_font_path, 18)
            self.font_small = pygame.font.Font(mac_font_path, 14)
            self.font_large = pygame.font.Font(mac_font_path, 26)
        except:
            print("[!] Warn: PingFang.ttc failed. Trying local 'chinese_font.ttf' or English fallback.")
            try:
                # Fallback if you download a .ttf file into the folder later
                self.font_main = pygame.font.Font("chinese_font.ttf", 18)
                self.font_small = pygame.font.Font("chinese_font.ttf", 14)
                self.font_large = pygame.font.Font("chinese_font.ttf", 26)
            except:
                self.font_main = pygame.font.Font(None, 24)
                self.font_small = pygame.font.Font(None, 18)
                self.font_large = pygame.font.Font(None, 32)

        # Connect to Backend Model
        self.board = JunqiBoard()
        self._pre_initialize_p1_terrain()
        
        # GUI STATE MACHINE
        self.held_piece = None  
        self.log_message = "Deployment Phase: Select a piece from the panel below."
        self.valid_spots = []  

        # Click Zone Pre-calculation
        self.viewer_zones = self._generate_board_hitboxes()
        self.panel_zones = self._generate_panel_buttons()

    def _pre_initialize_p1_terrain(self):
        """Implicit terrain rules derived from standard board, stored in graph."""
        for y in range(6):
            for x in range(5):
                node = self.board.graph[(x, y)]
                node["piece"] = None
                if y == 0 and x in (1, 3):
                    node["type"] = "HQ"
                elif y in (1, 2, 3) and x in (1, 3):
                    node["type"] = "Camp"
                else:
                    node["type"] = "Post"

    def _generate_board_hitboxes(self):
        """Maps physical visual pixels on the rotated board to backend (x,y) graph."""
        hitboxes = {}
        for y in range(6):  
            for x in range(5):
                # ROTATION MAGIC: Visual bottom row maps to backend row 0
                draw_y_vis = 5 - y 
                
                px_x = self.x_start + (x * self.spacing)
                px_y = self.y_start + (draw_y_vis * self.spacing)
                
                rect = pygame.Rect(0, 0, 50, 50)
                rect.center = (px_x, px_y)
                hitboxes[(x, y)] = rect  
        return hitboxes

    def _generate_panel_buttons(self):
        """Creates detailed click zones for the control panel table."""
        zones = {}
        btn_width = 110
        btn_height = 40
        padding_x = 20
        padding_y = 15
        
        start_x = 25
        start_y = BOARD_HEIGHT + 20 
        
        col = 0
        row = 0
        
        for item in self.pieces_data:
            name = item[0]
            px = start_x + col * (btn_width + padding_x)
            py = start_y + row * (btn_height + padding_y)
            zones[name] = pygame.Rect(px, py, btn_width, btn_height)
            
            col += 1
            if col > 3: 
                col = 0
                row += 1
        return zones

    def get_valid_deployment_spots(self, piece_name):
        """Controller logic: returns list of valid backend coords for the held piece."""
        valid_spots = []
        for y in range(6):  
            for x in range(5):
                node = self.board.graph[(x, y)]
                if node["piece"] is not None or node["type"] == "Camp":
                    continue
                
                if piece_name == "军旗":
                    if node["type"] == "HQ":
                        valid_spots.append((x, y))
                elif piece_name == "地雷":
                    if y <= 1:
                        valid_spots.append((x, y))
                elif piece_name == "炸弹":
                    if y < 5:
                        valid_spots.append((x, y))
                else:
                    valid_spots.append((x, y))
        return valid_spots

    def draw_viewer_component(self):
        """Renders the rotated graph state."""
        title = self.font_large.render("Junqi Battlefield", True, RED)
        self.screen.blit(title, (20, 10))
        label_bound = self.font_main.render("P1 Territory (Rotated 180°)", True, DARK_GRAY)
        self.screen.blit(label_bound, (20, BOARD_HEIGHT - 30))

        pygame.draw.rect(self.screen, BLACK, (0, 0, WINDOW_WIDTH, BOARD_HEIGHT))
        
        # Grid Lines
        for y in range(6):
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (self.x_start, self.y_start + y * self.spacing), 
                             (self.x_start + 4 * self.spacing, self.y_start + y * self.spacing), 2)
        for x in range(5):
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (self.x_start + x * self.spacing, self.y_start), 
                             (self.x_start + x * self.spacing, self.y_start + 5 * self.spacing), 2)

        # Nodes
        for (x, y), rect in self.viewer_zones.items():
            node_backend = self.board.graph[(x, y)]
            terrain_type = node_backend["type"]
            piece = node_backend["piece"]

            if terrain_type == "Camp":
                pygame.draw.circle(self.screen, DARK_GRAY, rect.center, 26, 2)
                terrain_text = self.font_small.render("行营", True, LIGHT_GRAY)
            elif terrain_type == "HQ":
                terrain_rect = pygame.Rect(0, 0, 60, 36)
                terrain_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, terrain_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, terrain_rect, 2)
                terrain_text = self.font_small.render("大本营", True, LIGHT_GRAY)
            else:
                terrain_rect = pygame.Rect(0, 0, 48, 28)
                terrain_rect.center = rect.center
                pygame.draw.rect(self.screen, BLACK, terrain_rect)
                pygame.draw.rect(self.screen, DARK_GRAY, terrain_rect, 2)
                terrain_text = self.font_small.render("兵站", True, LIGHT_GRAY)

            terrain_text_rect = terrain_text.get_rect(center=rect.center)
            self.screen.blit(terrain_text, terrain_text_rect)

            # Valid Spot Highlight
            if self.held_piece and (x, y) in self.valid_spots:
                s = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 150), (30, 30), 28)
                self.screen.blit(s, (rect.centerx - 30, rect.centery - 30))
                
            # Deployed Piece
            if piece:
                s = pygame.Surface((56, 34), pygame.SRCALPHA)
                pygame.draw.rect(s, (50, 100, 200, 220), (0,0,56,34), border_radius=4)
                pygame.draw.rect(s, (100, 200, 255, 255), (0,0,56,34), 2, border_radius=4)
                self.screen.blit(s, (rect.centerx - 28, rect.centery - 17))
                
                piece_text = self.font_main.render(piece.name, True, WHITE)
                piece_rect = piece_text.get_rect(center=rect.center)
                self.screen.blit(piece_text, piece_rect)

    def draw_panel_component(self):
        """Renders the interactive dashboard control panel."""
        panel_bg = pygame.Rect(0, BOARD_HEIGHT, WINDOW_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_bg)
        pygame.draw.line(self.screen, LIGHT_GRAY, (0, BOARD_HEIGHT), (WINDOW_WIDTH, BOARD_HEIGHT), 4)

        log_text = self.font_main.render(self.log_message, True, WHITE)
        self.screen.blit(log_text, (WINDOW_WIDTH - 300, BOARD_HEIGHT + PANEL_HEIGHT - 30))

        headers = ["Piece (P1)", "Tier", "Qty", "Action"]
        header_positions = [25, 140, 230, 310]
        header_y = BOARD_HEIGHT + 10
        for i, h in enumerate(headers):
            h_text = self.font_small.render(h, True, LIGHT_GRAY)
            self.screen.blit(h_text, (header_positions[i], header_y))

        y_offset = BOARD_HEIGHT + 30
        line_height = 28
        
        display_data = [
            ["司令", 9, "Field Marshal"],
            ["军长", 8, "General"],
            ["师长", 7, "Div General"],
            ["旅长", 6, "Brig General"],
            ["团长", 5, "Colonel"],
            ["营长", 4, "Major"],
            ["连长", 3, "Captain"],
            ["排长", 2, "Lieutenant"],
            ["工兵", 1, "Engineer"],
            ["炸弹", "S", "Bomb"],
            ["地雷", "S", "Landmine"],
            ["军旗", "S", "Flag"]
        ]

        for item in display_data:
            name, tier, desc = item
            count = self.counts_dict[name]
            
            name_text = self.font_main.render(name, True, WHITE)
            self.screen.blit(name_text, (25, y_offset))
            tier_text = self.font_small.render(f"Rank {tier}", True, WHITE)
            self.screen.blit(tier_text, (140, y_offset))
            desc_text = self.font_small.render(desc, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (140, y_offset + 12))
            count_text = self.font_main.render(str(count), True, WHITE)
            self.screen.blit(count_text, (230, y_offset))

            btn_rect = pygame.Rect(310, y_offset - 2, 80, 20)
            
            if self.held_piece == name:
                btn_color = GREEN
                btn_txt = "Held"
                pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=4)
            elif count > 0:
                btn_color = DARK_GRAY
                btn_txt = "Select"
                pygame.draw.rect(self.screen, LIGHT_GRAY, btn_rect, border_radius=4)
                pygame.draw.rect(self.screen, BLACK, btn_rect, 1, border_radius=4)
            else:
                btn_color = LIGHT_GRAY
                btn_txt = "-"
                pygame.draw.rect(self.screen, (100,100,100), btn_rect, border_radius=4)

            btn_label = self.font_small.render(btn_txt, True, BLACK)
            btn_label_rect = btn_label.get_rect(center=btn_rect.center)
            self.screen.blit(btn_label, btn_label_rect)
            
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
                    pos = pygame.mouse.get_pos()
                    self.handle_events(pos)
            self.draw()
            
        pygame.quit()
        sys.exit()

    def handle_events(self, pos):
        """Unified Controller logic."""
        zones = getattr(self, "action_button_zones", {})
        for name, rect in zones.items():
            if rect.collidepoint(pos):
                if self.held_piece == name:
                    self.held_piece = None
                    self.log_message = "Deselected piece."
                    self.valid_spots = []
                elif self.counts_dict[name] > 0:
                    self.held_piece = name
                    self.log_message = f"Holding {name}. Click a valid spot."
                    self.valid_spots = self.get_valid_deployment_spots(name)
                return 

        if self.held_piece:
            for (x, y), rect in self.viewer_zones.items():
                if rect.collidepoint(pos):
                    if (x, y) in self.valid_spots:
                        from pieces import Piece
                        
                        self.board.graph[(x, y)]["piece"] = Piece("P1", self.held_piece)
                        self.counts_dict[self.held_piece] -= 1
                        self.log_message = f"Deployed {self.held_piece} to (Rotated: ({x}, {y}))"
                        
                        self.held_piece = None
                        self.valid_spots = []
                    return 

        if self.held_piece and not any(r.collidepoint(pos) for r in self.viewer_zones.values()):
            self.held_piece = None
            self.log_message = "Deselected piece."
            self.valid_spots = []

if __name__ == "__main__":
    if platform.system() != "Darwin":
        print("[!] Warn: Run on macOS for native Chinese font rendering.")
        
    dashboard = JunqiEngineDashboard()
    dashboard.run()