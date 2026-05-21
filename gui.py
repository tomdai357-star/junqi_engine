# gui.py
import pygame
import sys
from board import JunqiBoard
from pieces import generate_army

# --- Configuration Constants ---
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
BOARD_WIDTH = 550  

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)
LINE_COLOR = (150, 150, 150)

class JunqiGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Junqi - Deployment Phase (Pure Pygame)")
        
        # Grid Math for Drawing
        self.x_start = 80
        self.y_start = 80
        self.spacing = 90

        # macOS system font that supports Chinese characters
        try:
            self.font = pygame.font.SysFont("PingFang", 18)
            self.small_font = pygame.font.SysFont("PingFang", 14)
            self.large_font = pygame.font.SysFont("PingFang", 28)
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            self.large_font = pygame.font.Font(None, 32)

        # Connect to your backend Model
        self.board = JunqiBoard()
        
        # State Machine Variables
        self.selected_piece_name = None
        self.log_message = "Select a piece to deploy."
        
        # Convert the generated army list into an inventory dictionary for the UI
        p1_list = generate_army("P1")
        self.inventory = {}
        for piece in p1_list:
            if piece.name in self.inventory:
                self.inventory[piece.name] += 1
            else:
                self.inventory[piece.name] = 1

        # Build the hitboxes mathematically based on our new grid
        self.hitboxes = self._generate_hitboxes()

    def _generate_hitboxes(self):
        """Maps physical pixel areas to the backend (x,y) graph coordinates."""
        hitboxes = {}
        for y in range(6):  # Only mapping P1 territory (rows 0 to 5)
            for x in range(5):
                px_x = self.x_start + (x * self.spacing)
                px_y = self.y_start + (y * self.spacing)
                
                # Create a 40x40 pixel clickable box perfectly centered on the grid node
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = (px_x, px_y)
                hitboxes[(x, y)] = rect
                
        return hitboxes

    def validate_placement(self, piece_name, x, y):
        """The strict rules for standard Junqi deployment."""
        node = self.board.graph[(x, y)]
        
        if node["piece"] is not None:
            return False, "Space occupied."
        if node["type"] == "Camp":
            return False, "Camps must be empty."
        if piece_name == "军旗" and node["type"] != "HQ":
            return False, "Flag must be in HQ."
        if piece_name == "地雷" and y > 1:
            return False, "Mines must be in row 0 or 1."
        if piece_name == "炸弹" and y == 5:
            return False, "Bombs cannot be on the frontline."
            
        return True, "Placed successfully."

    def handle_click(self, pos):
        """The Controller: Routes mouse clicks to the UI or the Board."""
        mouse_x, mouse_y = pos
        
        # 1. Check if the click was in the UI Panel
        if mouse_x > BOARD_WIDTH:
            btn_y = 50
            for piece_name, count in self.inventory.items():
                if count > 0:
                    btn_rect = pygame.Rect(BOARD_WIDTH + 20, btn_y, 150, 40)
                    if btn_rect.collidepoint(pos):
                        self.selected_piece_name = piece_name
                        self.log_message = f"Holding: {piece_name}"
                        return
                btn_y += 50

        # 2. Check if the click was on a Board Hitbox
        if self.selected_piece_name:
            for (x, y), rect in self.hitboxes.items():
                if rect.collidepoint(pos):
                    is_valid, msg = self.validate_placement(self.selected_piece_name, x, y)
                    
                    if is_valid:
                        from pieces import Piece
                        self.board.graph[(x, y)]["piece"] = Piece("P1", self.selected_piece_name)
                        
                        self.inventory[self.selected_piece_name] -= 1
                        self.selected_piece_name = None
                        self.log_message = msg
                    else:
                        self.log_message = f"Invalid: {msg}"
                    return

    def draw_dynamic_board(self):
        """Draws the board lines and nodes using math instead of an image."""
        # Draw the main grid lines
        for y in range(6):
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (self.x_start, self.y_start + y * self.spacing), 
                             (self.x_start + 4 * self.spacing, self.y_start + y * self.spacing), 2)
        for x in range(5):
            pygame.draw.line(self.screen, LINE_COLOR, 
                             (self.x_start + x * self.spacing, self.y_start), 
                             (self.x_start + x * self.spacing, self.y_start + 5 * self.spacing), 2)

        # Draw the specific nodes based on the board.py graph
        for y in range(6):
            for x in range(5):
                px_x = self.x_start + x * self.spacing
                px_y = self.y_start + y * self.spacing
                node_type = self.board.graph[(x, y)]["type"]

                if node_type == "Camp":
                    # Draw a circle for camps
                    pygame.draw.circle(self.screen, WHITE, (px_x, px_y), 24)
                    pygame.draw.circle(self.screen, RED, (px_x, px_y), 24, 2)
                    label = self.small_font.render("行营", True, RED)
                elif node_type == "HQ":
                    # Draw a larger rectangle for HQ
                    rect = pygame.Rect(0, 0, 56, 30)
                    rect.center = (px_x, px_y)
                    pygame.draw.rect(self.screen, WHITE, rect)
                    pygame.draw.rect(self.screen, RED, rect, 2)
                    label = self.small_font.render("大本营", True, RED)
                else:
                    # Draw a standard rectangle for Posts
                    rect = pygame.Rect(0, 0, 46, 24)
                    rect.center = (px_x, px_y)
                    pygame.draw.rect(self.screen, WHITE, rect)
                    pygame.draw.rect(self.screen, RED, rect, 2)
                    label = self.small_font.render("兵站", True, RED)

                # Center the Chinese text inside the shape
                label_rect = label.get_rect(center=(px_x, px_y))
                self.screen.blit(label, label_rect)

    def draw(self):
        """The View: Renders the current state of the backend."""
        self.screen.fill(WHITE)
        
        # 1. Draw the dynamic background first
        self.draw_dynamic_board()
        
        # 2. Draw placed pieces on top
        for (x, y), rect in self.hitboxes.items():
            node = self.board.graph[(x, y)]
            if node["piece"]:
                # Draw a solid blue token
                pygame.draw.circle(self.screen, BLUE, rect.center, 22)
                text = self.font.render(node["piece"].name, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
                
        # 3. Draw UI Panel
        panel_x = BOARD_WIDTH + 20
        title = self.large_font.render("P1 Deployment", True, BLACK)
        self.screen.blit(title, (panel_x, 10))
        
        btn_y = 50
        for piece_name, count in self.inventory.items():
            if count > 0:
                color = GREEN if piece_name == self.selected_piece_name else GRAY
                btn_rect = pygame.Rect(panel_x, btn_y, 150, 40)
                pygame.draw.rect(self.screen, color, btn_rect)
                pygame.draw.rect(self.screen, BLACK, btn_rect, 2)
                
                label = self.font.render(f"{piece_name}  x{count}", True, BLACK)
                self.screen.blit(label, (panel_x + 10, btn_y + 10))
            btn_y += 50
            
        # 4. Draw Status Log
        log_text = self.font.render(self.log_message, True, RED)
        self.screen.blit(log_text, (20, WINDOW_HEIGHT - 40))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                    
            self.draw()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = JunqiGUI()
    gui.run()