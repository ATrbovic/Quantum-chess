from utils import position_to_grid, grid_to_position

class QuantumChessPiece:
    def __init__(self, name, qubit_index, position, color):
        self.name = name
        self.qubit_index = qubit_index
        self.position = position
        self.color = color
        self.is_entangled = False
        self.entangled_with = None

    # def get_valid_moves(self, board):
    #     """Return a list of valid moves for this piece based on the current board state."""
    #     valid_moves = []

    #     row, col = position_to_grid(self.position)
    #     print(f"Calculating valid moves for {self.name} at {self.position} (row {row}, col {col})")

    #     # debug
    #     print("current board state:")
    #     for r in board:
    #         print(f" ".join([piece.name if piece else '.' for piece in r]))

    #     if self.name.startswith("w_pawn"):  # White pawn
    #         print(f"Checking forward move for {self.name} at ({row}, {col})")
    #         print(f"Square in front: ({row - 1}, {col}), value: {board[row - 1][col]}")
    #         # Check if the pawn can move forward one square
    #         if row > 0 and board[row - 1][col] is None:
    #             valid_moves.append(grid_to_position(row - 1, col))
    #             print(f"added move: {grid_to_position(row - 1, col)}")
    #         else:
    #             print(f"Square ({row - 1}, {col}) is not empty")
            
    #         # Check if the pawn can capture diagonally
    #         if row > 0 and col > 0:
    #             print(f"Checking square ({row - 1}, {col - 1}) for capture move")
    #             print(f"Square value: {board[row - 1][col - 1]}")
    #             if board[row - 1][col - 1] is not None and board[row - 1][col - 1].name.startswith("b_"):
    #                 valid_moves.append(grid_to_position(row - 1, col - 1))
    #                 print(f"Added capture move: {grid_to_position(row - 1, col - 1)}")
    #             else:
    #                 print(f"Square ({row - 1}, {col - 1}) is empty or not an enemy piece")
    #         if row > 0 and col < 7:
    #             print(f"Checking square ({row - 1}, {col + 1}) for capture move")
    #             print(f"Square value: {board[row - 1][col + 1]}")
    #             if board[row - 1][col + 1] is not None and board[row - 1][col + 1].name.startswith("b_"):
    #                 valid_moves.append(grid_to_position(row - 1, col + 1))
    #                 print(f"Added capture move: {grid_to_position(row - 1, col + 1)}")
    #             else:
    #                 print(f"Square ({row - 1}, {col + 1}) is empty or not an enemy piece")

    #     elif self.name.startswith("b_pawn"):  # Black pawn
    #         print(f"Checking forward move for {self.name} at ({row}, {col})")
    #         print(f"Square in front: ({row + 1}, {col}), value: {board[row + 1][col]}")
    #         # Check if the pawn can move forward one square
    #         if row < 7 and board[row + 1][col] is None:
    #             valid_moves.append(grid_to_position(row + 1, col))
    #             print(f"added move: {grid_to_position(row + 1, col)}")
    #         else:
    #             print(f"Square ({row + 1}, {col}) is not empty")

    #         # Check if the pawn can capture diagonally
    #         if row < 7 and col > 0:
    #             print(f"Checking square ({row + 1}, {col - 1}) for capture move")
    #             print(f"Square value: {board[row + 1][col - 1]}")
    #             if board[row + 1][col - 1] is not None and board[row + 1][col - 1].name.startswith("w_"):
    #                 valid_moves.append(grid_to_position(row + 1, col - 1))
    #                 print(f"Added capture move: {grid_to_position(row + 1, col - 1)}")
    #             else:
    #                 print(f"Square ({row + 1}, {col - 1}) is empty or not an enemy piece")
    #         if row < 7 and col < 7:
    #             print(f"Checking square ({row + 1}, {col + 1}) for capture move")
    #             print(f"Square value: {board[row + 1][col + 1]}")
    #             if board[row + 1][col + 1] is not None and board[row + 1][col + 1].name.startswith("w_"):
    #                 valid_moves.append(grid_to_position(row + 1, col + 1))
    #                 print(f"Added capture move: {grid_to_position(row + 1, col + 1)}")
    #             else:
    #                 print(f"Square ({row + 1}, {col + 1}) is empty or not an enemy piece")

    #     elif self.name.startswith("w_rook") or self.name.startswith("b_rook"):  # Rook
    #         # Horizontal and vertical moves
    #         directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    #         for dr, dc in directions:
    #             r, c = row + dr, col + dc
    #             while 0 <= r < 8 and 0 <= c < 8:
    #                 if board[r][c] is None:
    #                     valid_moves.append(grid_to_position(r, c))
    #                 else:
    #                     if (self.name.startswith("w_") and board[r][c].name.startswith("b_")) or \
    #                     (self.name.startswith("b_") and board[r][c].name.startswith("w_")):
    #                         valid_moves.append(grid_to_position(r, c))
    #                     break
    #                 r += dr
    #                 c += dc

    #     elif self.name.startswith("w_knight") or self.name.startswith("b_knight"):  # Knight
    #         # All possible L-shaped moves
    #         moves = [(-2, -1), (-1, -2), (-2, 1), (-1, 2),
    #                 (2, -1), (1, -2), (2, 1), (1, 2)]
    #         for dr, dc in moves:
    #             r, c = row + dr, col + dc
    #             if 0 <= r < 8 and 0 <= c < 8:
    #                 if board[r][c] is None or \
    #                 (self.name.startswith("w_") and board[r][c].name.startswith("b_")) or \
    #                 (self.name.startswith("b_") and board[r][c].name.startswith("w_")):
    #                     valid_moves.append(grid_to_position(r, c))

    #     elif self.name.startswith("w_bishop") or self.name.startswith("b_bishop"):  # Bishop
    #         # Diagonal moves
    #         directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    #         for dr, dc in directions:
    #             r, c = row + dr, col + dc
    #             while 0 <= r < 8 and 0 <= c < 8:
    #                 if board[r][c] is None:
    #                     valid_moves.append(grid_to_position(r, c))
    #                 else:
    #                     if (self.name.startswith("w_") and board[r][c].name.startswith("b_")) or \
    #                     (self.name.startswith("b_") and board[r][c].name.startswith("w_")):
    #                         valid_moves.append(grid_to_position(r, c))
    #                     break
    #                 r += dr
    #                 c += dc

    #     elif self.name.startswith("w_queen") or self.name.startswith("b_queen"):  # Queen
    #         # Combination of rook and bishop moves
    #         directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    #         for dr, dc in directions:
    #             r, c = row + dr, col + dc
    #             while 0 <= r < 8 and 0 <= c < 8:
    #                 if board[r][c] is None:
    #                     valid_moves.append(grid_to_position(r, c))
    #                 else:
    #                     if (self.name.startswith("w_") and board[r][c].name.startswith("b_")) or \
    #                     (self.name.startswith("b_") and board[r][c].name.startswith("w_")):
    #                         valid_moves.append(grid_to_position(r, c))
    #                     break
    #                 r += dr
    #                 c += dc

    #     elif self.name.startswith("w_king") or self.name.startswith("b_king"):  # King
    #         print(f"Checking moves for {self.name} at ({row}, {col})")
    #         # All adjacent squares
    #         moves = [(-1, -1), (-1, 0), (-1, 1),
    #                 (0, -1),          (0, 1),
    #                 (1, -1),  (1, 0), (1, 1)]
    #         for dr, dc in moves:
    #             r, c = row + dr, col + dc
    #             if 0 <= r < 8 and 0 <= c < 8:
    #                 if board[r][c] is None or \
    #                 (self.name.startswith("w_") and board[r][c].name.startswith("b_")) or \
    #                 (self.name.startswith("b_") and board[r][c].name.startswith("w_")):
    #                     valid_moves.append(grid_to_position(r, c))
    #                     print(f"Added move: {grid_to_position(r, c)}")
    #                 else:
    #                     print(f"Square ({r}, {c}) is occupied by a friendly piece")
    #             else:
    #                 print(f"Square ({r}, {c}) is out of bounds")

    #     print(f"Valid moves for {self.name}: {valid_moves}")
    #     return valid_moves
    def get_valid_moves(self, board):
        """Return a list of valid moves for this piece based on the current board state."""
        valid_moves = []
        row, col = position_to_grid(self.position)
        print(f"Calculating valid moves for {self.color} {self.name} at {self.position} (row {row}, col {col})")

        # Debug: print current board state
        print("Current board state:")
        for r in board:
            print(" ".join([piece.name if piece else '.' for piece in r]))

        if self.name.lower() == "pawn":
            if self.color == "w":  # White pawn moves upward (decreasing row)
                print(f"Checking forward move for white pawn at ({row}, {col})")
                # One square forward
                if row > 0 and board[row - 1][col] is None:
                    move = grid_to_position(row - 1, col)
                    valid_moves.append(move)
                    print(f"Added move: {move}")
                    # Two squares forward from starting position
                    if row == 6 and board[row - 2][col] is None:
                        move2 = grid_to_position(row - 2, col)
                        valid_moves.append(move2)
                        print(f"Added two-square move: {move2}")
                else:
                    print(f"Square ({row - 1}, {col}) is not empty")
                # Diagonal captures for white pawn
                if row > 0 and col > 0:
                    print(f"Checking capture move at ({row - 1}, {col - 1})")
                    if board[row - 1][col - 1] is not None and board[row - 1][col - 1].color == "b":
                        move = grid_to_position(row - 1, col - 1)
                        valid_moves.append(move)
                        print(f"Added capture move: {move}")
                    else:
                        print(f"Square ({row - 1}, {col - 1}) is empty or not an enemy piece")
                if row > 0 and col < 7:
                    print(f"Checking capture move at ({row - 1}, {col + 1})")
                    if board[row - 1][col + 1] is not None and board[row - 1][col + 1].color == "b":
                        move = grid_to_position(row - 1, col + 1)
                        valid_moves.append(move)
                        print(f"Added capture move: {move}")
                    else:
                        print(f"Square ({row - 1}, {col + 1}) is empty or not an enemy piece")
            elif self.color == "b":  # Black pawn moves downward (increasing row)
                print(f"Checking forward move for black pawn at ({row}, {col})")
                # One square forward
                if row < 7 and board[row + 1][col] is None:
                    move = grid_to_position(row + 1, col)
                    valid_moves.append(move)
                    print(f"Added move: {move}")
                    # Two squares forward from starting position
                    if row == 1 and board[row + 2][col] is None:
                        move2 = grid_to_position(row + 2, col)
                        valid_moves.append(move2)
                        print(f"Added two-square move: {move2}")
                else:
                    print(f"Square ({row + 1}, {col}) is not empty")
                # Diagonal captures for black pawn
                if row < 7 and col > 0:
                    print(f"Checking capture move at ({row + 1}, {col - 1})")
                    if board[row + 1][col - 1] is not None and board[row + 1][col - 1].color == "w":
                        move = grid_to_position(row + 1, col - 1)
                        valid_moves.append(move)
                        print(f"Added capture move: {move}")
                    else:
                        print(f"Square ({row + 1}, {col - 1}) is empty or not an enemy piece")
                if row < 7 and col < 7:
                    print(f"Checking capture move at ({row + 1}, {col + 1})")
                    if board[row + 1][col + 1] is not None and board[row + 1][col + 1].color == "w":
                        move = grid_to_position(row + 1, col + 1)
                        valid_moves.append(move)
                        print(f"Added capture move: {move}")
                    else:
                        print(f"Square ({row + 1}, {col + 1}) is empty or not an enemy piece")

        elif self.name.lower() == "rook":
            # Horizontal and vertical moves
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        valid_moves.append(grid_to_position(r, c))
                    else:
                        if board[r][c].color != self.color:
                            valid_moves.append(grid_to_position(r, c))
                        break
                    r += dr
                    c += dc

        elif self.name.lower() == "knight":
            # All possible L-shaped moves
            moves = [(-2, -1), (-1, -2), (-2, 1), (-1, 2),
                    (2, -1), (1, -2), (2, 1), (1, 2)]
            for dr, dc in moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        valid_moves.append(grid_to_position(r, c))

        elif self.name.lower() == "bishop":
            # Diagonal moves
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        valid_moves.append(grid_to_position(r, c))
                    else:
                        if board[r][c].color != self.color:
                            valid_moves.append(grid_to_position(r, c))
                        break
                    r += dr
                    c += dc

        elif self.name.lower() == "queen":
            # Combination of rook and bishop moves
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None:
                        valid_moves.append(grid_to_position(r, c))
                    else:
                        if board[r][c].color != self.color:
                            valid_moves.append(grid_to_position(r, c))
                        break
                    r += dr
                    c += dc

        elif self.name.lower() == "king":
            print(f"Checking moves for {self.color} king at ({row}, {col})")
            # All adjacent squares
            moves = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0, 1),
                    (1, -1),  (1, 0), (1, 1)]
            for dr, dc in moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        move = grid_to_position(r, c)
                        valid_moves.append(move)
                        print(f"Added move: {move}")
                    else:
                        print(f"Square ({r}, {c}) is occupied by a friendly piece")
                else:
                    print(f"Square ({r}, {c}) is out of bounds")

        print(f"Valid moves for {self.color} {self.name}: {valid_moves}")
        return valid_moves

    def __repr__(self):
        return f"{self.name} at {self.position}"

    def move_to(self, new_position):
        """Move the piece to a new position on the board."""
        self.position = new_position
        print(f"{self.name} moved to {new_position}.")

    def entangle_with(self, other_piece):
        """Entangle this piece with another piece."""
        self.is_entangled = True
        self.entangled_with = other_piece
        other_piece.is_entangled = True
        other_piece.entangled_with = self
        print(f"{self.name} is now entangled with {other_piece.name}.")

    def break_entanglement(self):
        """Break the entanglement with another piece."""
        if self.is_entangled and self.entangled_with:
            self.is_entangled = False
            self.entangled_with.is_entangled = False
            temp = self.entangled_with
            self.entangled_with = None
            temp.entangled_with = None
            print(f"Entanglement between {self.name} and {temp.name} is broken.")

    def reset(self):
        """Reset the piece to its initial state."""
        self.is_entangled = False
        self.entangled_with = None
        print(f"{self.name} has been reset.")

    def apply_quantum_effect(self, effect_function):
        """Apply a quantum effect to the piece using a provided function."""
        effect_function(self.qubit_index)
        print(f"Quantum effect applied to {self.name}.")