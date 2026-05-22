# settings.py

# --- Window Constants ---
BOARD_WIDTH = 550
PANEL_WIDTH = 400
WINDOW_WIDTH = BOARD_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = 650  

# --- Grid Math ---
X_START = 90
Y_START = 60
X_SPACING = 90
Y_SPACING = 45
RIVER_GAP = 30

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
LINE_COLOR = (120, 120, 120)

# --- Game Data ---
PIECES_DATA = [
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