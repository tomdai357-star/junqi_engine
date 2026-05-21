# Junqi Board Inititalization 
class JunqiBoard:
    def __init__(self):
        # The graph: keys are (x, y), values are dictionaries containing node data and edges
        self.graph = {}
        self._build_nodes()
        self._build_edges()

    def _build_nodes(self):
        """Generates all 60 stations and assigns their proper types."""
        for y in range(12):
            for x in range(5):
                # Fold the y-coordinate to mirror Player 2's side perfectly onto Player 1's logic
                mirror_y = y if y < 6 else 11 - y
                
                # Assign types based on the mirrored half-board blueprint
                if mirror_y == 0 and x in (1, 3):
                    node_type = "HQ"
                elif mirror_y in (2, 4) and x in (1, 3):
                    node_type = "Camp"
                elif mirror_y == 3 and x == 2:
                    node_type = "Camp"
                else:
                    node_type = "Post"
                    
                self.graph[(x, y)] = {
                    "type": node_type,
                    "piece": None,
                    "neighbors": {} # Will hold connected_node: path_type
                }

    def _add_edge(self, p1, p2, path_type):
        """Helper to create bidirectional connections."""
        self.graph[p1]["neighbors"][p2] = path_type
        self.graph[p2]["neighbors"][p1] = path_type
        

    def _build_edges(self):
        """Connects the grid based on Road, Railroad, and Diagonal rules."""
        
        # 1. Vertical Connections
        for x in range(5):
            for y in range(11):
                # The River gap: Pieces can only cross at the 3 railroad bridges (cols 0, 2, 4)
                if y == 5 and x not in (0, 2, 4):
                    continue 
                    
                # Continuous vertical Railroads exist on cols 0, 2, 4 from row 1 down to row 10
                if x in (0, 2, 4) and 1 <= y < 10:
                    self._add_edge((x, y), (x, y + 1), "RR")
                else:
                    self._add_edge((x, y), (x, y + 1), "Road")
                    
        # 2. Horizontal Connections
        for y in range(12):
            for x in range(4):
                # Horizontal Railroads run across rows 1, 5 (P1 Frontline), 6 (P2 Frontline), and 10
                if y in (1, 5, 6, 10):
                    self._add_edge((x, y), (x + 1, y), "RR")
                else:
                    self._add_edge((x, y), (x + 1, y), "Road")
                    
        # 3. Diagonal Connections
        # Diagonals ONLY exist around Campsites. We use them as anchors.
        camps = [pos for pos, data in self.graph.items() if data["type"] == "Camp"]
        for cx, cy in camps:
            # Map the 4 diagonal corners of the camp
            diagonals = [
                (cx - 1, cy - 1), (cx + 1, cy - 1),
                (cx - 1, cy + 1), (cx + 1, cy + 1)
            ]
            for dx, dy in diagonals:
                # Ensure the destination actually exists on the board (prevents out-of-bounds)
                if (dx, dy) in self.graph:
                    self._add_edge((cx, cy), (dx, dy), "D.Road")

    def print_text_board(self):
        """Prints an ASCII representation of the board state to the terminal."""
        print("\n=== JUNQI BOARD STATE ===")
        for y in range(12):
            row_output = []
            for x in range(5):
                node_type = self.graph[(x, y)]["type"]
                
                # Format the text so the grid aligns nicely
                if node_type == "HQ":
                    row_output.append("[ HQ ]")
                elif node_type == "Camp":
                    row_output.append("(Camp)")
                else:
                    row_output.append("[Post]")
            
            # Print the row
            print("  ".join(row_output))
            
            # Print the river gap between player territories
            if y == 5:
                print("\n" + "="*40 + "  <-- RIVER / FRONTLINE\n")

if __name__ == "__main__":
    # 1. Instantiate the board (Builds the graph in memory)
    game_board = JunqiBoard()
    
    # 2. Call our new visualization tool
    game_board.print_text_board()