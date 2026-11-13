"""Piece geometry; turn and king-safety rules live in game.py."""

from utils import grid_to_position, position_to_grid


class QuantumChessPiece:
    def __init__(self, name, qubit_index, position, color):
        self.name = name
        self.qubit_index = qubit_index
        self.position = position
        self.color = color

    def get_valid_moves(self, board):
        row, col = position_to_grid(self.position)
        moves = []
        if self.name == "Pawn":
            direction = -1 if self.color == "w" else 1
            ahead = row + direction
            if 0 <= ahead < 8:
                if board[ahead][col] is None:
                    moves.append(grid_to_position(ahead, col))
                    if row == (6 if self.color == "w" else 1):
                        if board[row + 2 * direction][col] is None:
                            moves.append(grid_to_position(row + 2 * direction, col))
                for c in (col - 1, col + 1):
                    if 0 <= c < 8 and board[ahead][c] is not None:
                        if board[ahead][c].color != self.color:
                            moves.append(grid_to_position(ahead, c))
            return moves
        if self.name == "Knight":
            directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]
        elif self.name == "King":
            directions = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                          if dr or dc]
        else:
            directions = []
            if self.name in {"Rook", "Queen"}:
                directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if self.name in {"Bishop", "Queen"}:
                directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                occupant = board[r][c]
                if occupant is None or occupant.color != self.color:
                    moves.append(grid_to_position(r, c))
                if occupant is not None or self.name in {"King", "Knight"}:
                    break
                r, c = r + dr, c + dc
        return moves

    def __repr__(self):
        return f"{self.color} {self.name} at {self.position}"
