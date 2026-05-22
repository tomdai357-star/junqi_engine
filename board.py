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

    def get_legal_moves(self, x, y):
        """
        Calculates Final Stage movement: 
        1-step adjacency + Straight-line Railroad sliding + Engineer BFS Cornering.
        """
        node = self.graph.get((x, y))
        if not node or not node["piece"]:
            return []

        piece = node["piece"]
        
        # 1. The Immovables
        if piece.name in ["地雷", "军旗"]:
            return []
            
        legal_moves = []
        
        def is_valid_target(nx, ny):
            target_node = self.graph[(nx, ny)]
            target_piece = target_node["piece"]
            
            if target_piece and target_piece.player == piece.player:
                return False
            if target_node["type"] == "Camp" and target_piece is not None:
                return False
            return True

        # 2. Check all immediate neighbors (Standard 1-step)
        for (nx, ny), path_type in node["neighbors"].items():
            if is_valid_target(nx, ny):
                legal_moves.append((nx, ny))
            
            # --- RAILROAD LOGIC ---
            if path_type == "RR":
                
                # 3A. The Engineer (Breadth-First Search for cornering)
                if piece.name == "工兵":
                    queue = [(nx, ny)]
                    visited = set([(x, y)]) # Mark the start node as visited
                    
                    while queue:
                        cx, cy = queue.pop(0)
                        
                        if (cx, cy) in visited:
                            continue
                        visited.add((cx, cy))
                        
                        if is_valid_target(cx, cy):
                            legal_moves.append((cx, cy))
                            
                        # If there is ANY piece here, the tracks are blocked. Stop flowing.
                        if self.graph[(cx, cy)]["piece"] is not None:
                            continue
                            
                        # If the node is empty, pour water into all connected RR paths!
                        for (nnx, nny), n_path in self.graph[(cx, cy)]["neighbors"].items():
                            if n_path == "RR" and (nnx, nny) not in visited:
                                queue.append((nnx, nny))
                                
                # 3B. Standard Pieces (Raycast for straight lines)
                elif self.graph[(nx, ny)]["piece"] is None:
                    dx = nx - x
                    dy = ny - y
                    curr_x, curr_y = nx, ny
                    
                    while True:
                        next_x = curr_x + dx
                        next_y = curr_y + dy
                        curr_node = self.graph[(curr_x, curr_y)]
                        
                        if (next_x, next_y) not in curr_node["neighbors"] or curr_node["neighbors"][(next_x, next_y)] != "RR":
                            break
                            
                        if is_valid_target(next_x, next_y):
                            legal_moves.append((next_x, next_y))
                            
                        if self.graph[(next_x, next_y)]["piece"] is not None:
                            break
                            
                        curr_x, curr_y = next_x, next_y
                        
        return list(set(legal_moves))
        
        # Helper function to check if a specific node is a valid landing spot
        def is_valid_target(nx, ny):
            target_node = self.graph[(nx, ny)]
            target_piece = target_node["piece"]
            
            if target_piece and target_piece.player == piece.player:
                return False
            if target_node["type"] == "Camp" and target_piece is not None:
                return False
            return True

        # 2. Check all immediate neighbors (Standard 1-step)
        for (nx, ny), path_type in node["neighbors"].items():
            if is_valid_target(nx, ny):
                legal_moves.append((nx, ny))
            
            # 3. The Raycast: If the path is a Railroad AND the adjacent node is completely empty, 
            # we can attempt to slide through it!
            if path_type == "RR" and self.graph[(nx, ny)]["piece"] is None:
                
                # Calculate the Direction Vector (e.g., dx = 1, dy = 0 means moving Right)
                dx = nx - x
                dy = ny - y
                
                curr_x, curr_y = nx, ny
                
                # Follow the tracks infinitely until broken
                while True:
                    next_x = curr_x + dx
                    next_y = curr_y + dy
                    curr_node = self.graph[(curr_x, curr_y)]
                    
                    # Rule A: Does the track physically continue in this exact straight line?
                    if (next_x, next_y) not in curr_node["neighbors"] or curr_node["neighbors"][(next_x, next_y)] != "RR":
                        break
                        
                    # Rule B: Can we legally land on this next node?
                    if is_valid_target(next_x, next_y):
                        legal_moves.append((next_x, next_y))
                        
                    # Rule C: Is there a physical blockage? (Any piece stops the slide)
                    if self.graph[(next_x, next_y)]["piece"] is not None:
                        break
                        
                    # Move the raycast forward to the next node
                    curr_x, curr_y = next_x, next_y
                    
        # Return unique moves (using set to remove duplicates)
        return list(set(legal_moves))

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