# Game logic
# game.py
from board import JunqiBoard
from pieces import generate_army

class JunqiGame:
    def __init__(self):
        # Initialize the state
        self.board = JunqiBoard()
        self.current_turn = "P1"
        
        # Run deployment immediately
        self.setup_game()

    def setup_game(self):
        """Generates armies and places them on valid starting nodes."""
        p1_army = generate_army("P1")
        p2_army = generate_army("P2")

        # Loop through the entire graph coordinate system
        for y in range(12):
            for x in range(5):
                node = self.board.graph[(x, y)]
                
                # Rule 1: Campsites must be empty at the start
                if node["type"] == "Camp":
                    continue 

                # Rule 2: Fill P1 Territory (Rows 0 to 5)
                if y <= 5 and p1_army:
                    node["piece"] = p1_army.pop(0)
                    
                # Rule 3: Fill P2 Territory (Rows 6 to 11)
                elif y >= 6 and p2_army:
                    node["piece"] = p2_army.pop(0)

    def display_board(self):
        """A terminal renderer that checks for pieces before printing empty nodes."""
        print("\n=== JUNQI BATTLEFIELD ===")
        for y in range(12):
            row_output = []
            for x in range(5):
                node = self.board.graph[(x, y)]
                
                # If a piece exists here, print its Chinese name
                if node["piece"]:
                    row_output.append(f"[{node['piece'].name}]")
                # Otherwise, print the empty terrain
                elif node["type"] == "HQ":
                    row_output.append("[ 大本营 ]") # HQ
                elif node["type"] == "Camp":
                    row_output.append("( 行营 )") # Camp
                else:
                    row_output.append("[      ]") # Empty Post
                    
            print("  ".join(row_output))
            
            # Draw the river
            if y == 5:
                print("\n" + "="*50 + "  <-- RIVER / FRONTLINE\n")

if __name__ == "__main__":
    game = JunqiGame()
    game.display_board()