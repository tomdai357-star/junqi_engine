# renderer.py
import pygame
from settings import *

class JunqiRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_main = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_large = pygame.font.Font(None, 32)
        # Dedicated smaller font for pieces so "Bomb" and "Mine" fit perfectly
        self.font_piece = pygame.font.Font(None, 16) 

    def _draw_wrapped_text(self, surface, text, font, color, max_width, x, y):
        """Helper to wrap long log messages into multiple lines."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y + i * font.get_linesize()))

    def draw(self, engine):
        self.screen.fill(BLACK)
        self.draw_viewer(engine)
        self.draw_panel(engine)
        pygame.display.flip()

    def draw_viewer(self, engine):
        pygame.draw.rect(self.screen, BLACK, (0, 0, BOARD_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, LIGHT_GRAY, (BOARD_WIDTH, 0), (BOARD_WIDTH, WINDOW_HEIGHT), 4)
        
        title = self.font_large.render("Junqi Battlefield", True, RED)
        self.screen.blit(title, (20, 10))
        p2_label = self.font_small.render("P2 Territory", True, DARK_GRAY)
        self.screen.blit(p2_label, (20, 40))
        p1_label = self.font_small.render("P1 Territory", True, DARK_GRAY)
        self.screen.blit(p1_label, (20, WINDOW_HEIGHT - 30))

        # Lines
        for (x, y), rect in engine.viewer_zones.items():
            if x < 4:
                right_rect = engine.viewer_zones[(x + 1, y)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, right_rect.center, 2)
            if y < 11 and y != 5:
                up_rect = engine.viewer_zones[(x, y + 1)]
                pygame.draw.line(self.screen, LINE_COLOR, rect.center, up_rect.center, 2)

        # Nodes
        for (x, y), rect in engine.viewer_zones.items():
            node = engine.board.graph[(x, y)]
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

            # Valid Spot Highlight
            is_setup_highlight = engine.game_phase == "SETUP" and engine.held_piece and (x, y) in engine.valid_spots
            is_battle_highlight = engine.game_phase == "BATTLE" and getattr(engine, 'selected_pos', None) and (x, y) in engine.valid_spots
            
            if is_setup_highlight or is_battle_highlight:
                s = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 150), (20, 20), 18)
                self.screen.blit(s, (rect.centerx - 20, rect.centery - 20))
                
            if piece:
                s = pygame.Surface((44, 26), pygame.SRCALPHA)
                color = (50, 100, 200, 220) if piece.player == "P1" else (200, 50, 50, 220)
                pygame.draw.rect(s, color, (0,0,44,26), border_radius=3)
                pygame.draw.rect(s, WHITE, (0,0,44,26), 1, border_radius=3)
                self.screen.blit(s, (rect.centerx - 22, rect.centery - 13))
                
                is_visible = True
                if engine.game_phase == "BATTLE" and piece.player != engine.current_player:
                    is_visible = False
                    
                if is_visible:
                    rank = next((item[1] for item in PIECES_DATA if item[0] == piece.name), 0)
                    if piece.name == "军旗": display_str = "Flag"
                    elif piece.name == "地雷": display_str = "Mine"
                    elif piece.name == "炸弹": display_str = "Bomb"
                    else: display_str = f"R{rank}"
                    
                    # Use the new piece font
                    p_text = self.font_piece.render(display_str, True, WHITE)
                    p_rect = p_text.get_rect(center=rect.center)
                    self.screen.blit(p_text, p_rect)

            # Selected Piece Highlight
            if engine.game_phase == "BATTLE" and getattr(engine, 'selected_pos', None) == (x, y):
                sel_surf = pygame.Surface((48, 30), pygame.SRCALPHA)
                pygame.draw.rect(sel_surf, (255, 255, 0, 255), (0,0,48,30), 3, border_radius=4)
                self.screen.blit(sel_surf, (rect.centerx - 24, rect.centery - 15))

    def draw_panel(self, engine):
        pygame.draw.rect(self.screen, DARK_GRAY, (BOARD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT))

        if engine.game_phase == "SETUP":
            btn_color = BLUE if engine.current_player == "P1" else RED
            pygame.draw.rect(self.screen, btn_color, engine.btn_switch_player, border_radius=6)
            btn_txt = self.font_main.render(f"Deploying: {engine.current_player} (Click to Switch)", True, WHITE)
            self.screen.blit(btn_txt, btn_txt.get_rect(center=engine.btn_switch_player.center))

            headers = [f"Piece ({engine.current_player})", "Tier", "Qty", "Action"]
            header_positions = [BOARD_WIDTH + 20, BOARD_WIDTH + 140, BOARD_WIDTH + 210, BOARD_WIDTH + 270]
            header_y = 80
            for i, h in enumerate(headers):
                h_text = self.font_small.render(h, True, LIGHT_GRAY)
                self.screen.blit(h_text, (header_positions[i], header_y))

            y_offset = 110
            line_height = 36
            for item in PIECES_DATA:
                name, tier, _, desc = item
                count = engine.counts[engine.current_player][name]
                
                name_text = self.font_main.render(desc, True, WHITE)
                self.screen.blit(name_text, (BOARD_WIDTH + 20, y_offset))
                tier_str = f"Rank {tier}" if tier > 0 else "Special"
                tier_text = self.font_small.render(tier_str, True, LIGHT_GRAY)
                self.screen.blit(tier_text, (BOARD_WIDTH + 140, y_offset + 3))
                count_text = self.font_main.render(str(count), True, WHITE)
                self.screen.blit(count_text, (BOARD_WIDTH + 220, y_offset))

                btn_rect = engine.action_button_zones[name]
                if engine.held_piece == name:
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

            # DEV AUTO-FILL
            if hasattr(engine, 'btn_randomize'):
                pygame.draw.rect(self.screen, (130, 60, 180), engine.btn_randomize, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, engine.btn_randomize, 2, border_radius=6)
                rand_txt = self.font_main.render("DEV: Auto-Fill Board", True, WHITE)
                self.screen.blit(rand_txt, rand_txt.get_rect(center=engine.btn_randomize.center))

            if engine.is_deployment_complete():
                pygame.draw.rect(self.screen, GREEN, engine.btn_start_battle, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, engine.btn_start_battle, 2, border_radius=6)
                start_txt = self.font_large.render("START BATTLE", True, BLACK)
                self.screen.blit(start_txt, start_txt.get_rect(center=engine.btn_start_battle.center))

        elif engine.game_phase in ["BATTLE", "GAME_OVER"]:
            title_text = self.font_large.render("BATTLE PHASE", True, RED)
            self.screen.blit(title_text, (BOARD_WIDTH + 20, 20))
            
            btn_color = BLUE if engine.current_player == "P1" else RED
            pygame.draw.rect(self.screen, btn_color, engine.btn_switch_player, border_radius=6)
            pygame.draw.rect(self.screen, WHITE, engine.btn_switch_player, 2, border_radius=6)
            btn_txt = self.font_main.render(f"End Turn (Pass to { 'P2' if engine.current_player == 'P1' else 'P1' })", True, WHITE)
            self.screen.blit(btn_txt, btn_txt.get_rect(center=engine.btn_switch_player.center))

        # --- DYNAMIC LOG WRAPPING ---
        # Shifted up slightly to allow multiple lines to render downwards
        self._draw_wrapped_text(
            surface=self.screen, 
            text=engine.log_message, 
            font=self.font_main, 
            color=WHITE, 
            max_width=PANEL_WIDTH - 40, 
            x=BOARD_WIDTH + 20, 
            y=WINDOW_HEIGHT - 50 
        )