# Piece class setup
# pieces.py

# 1. THE RULEBOOK (Rank Hierarchy)
# Higher numbers defeat lower numbers. 
# 0, -1, and -2 are reserved for special combat rules later.
JUNQI_RANKS = {
    "司令": 9,  # Field Marshal
    "军长": 8,  # General
    "师长": 7,  # Major General
    "旅长": 6,  # Brigadier General
    "团长": 5,  # Colonel
    "营长": 4,  # Major
    "连长": 3,  # Captain
    "排长": 2,  # Lieutenant
    "工兵": 1,  # Engineer
    "炸弹": 0,  # Bomb (Special: Destroys both pieces on impact)
    "地雷": -1, # Landmine (Static: Destroys attackers except Engineers)
    "军旗": -2  # Flag (Static: Game over if captured)
}

# 2. THE BLUEPRINT (Piece Object)
class Piece:
    def __init__(self, player, name):
        self.player = player           # "P1" or "P2"
        self.name = name               # e.g., "司令"
        self.rank = JUNQI_RANKS[name]  # Automatically pulls the math value from above
        self.is_revealed = False       # Fog of War toggle

    def __repr__(self):
        """Formats how the piece looks when printed to the terminal."""
        status = "(!)" if self.is_revealed else "(?)"
        return f"[{self.player} {self.name} {status}]"

# 3. THE MANUFACTURER (Army Generation)
def generate_army(player_id):
    """Generates the exact 25 pieces needed for one player's standard army."""
    army_list = [
        "司令", "军长", "军旗",                  # 1 of each
        "师长", "师长", "旅长", "旅长",           # 2 of each
        "团长", "团长", "营长", "营长", "炸弹", "炸弹", # 2 of each
        "连长", "连长", "连长", "排长", "排长", "排长", # 3 of each
        "工兵", "工兵", "工兵", "地雷", "地雷", "地雷"  # 3 of each
    ]
    
    # Use a list comprehension to stamp out a Piece object for every string
    return [Piece(player_id, name) for name in army_list]


# Quick test block to ensure it works when run directly
if __name__ == "__main__":
    p1_army = generate_army("P1")
    print("Player 1 Army Generated:")
    print(p1_army)