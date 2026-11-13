"""Chess variant with at most ten coherent binary position choices."""

from pieces import QuantumChessPiece
from quantum_logic import MAX_QUBITS, QuantumRegister
from utils import position_to_grid


class QuantumChessGame:
    def __init__(self, num_qubits=MAX_QUBITS, seed=None):
        self.quantum = QuantumRegister(num_qubits, seed=seed)
        self.num_qubits = self.quantum.num_qubits
        self.pieces = {}
        self.branches = {}  # piece id -> (position if 0, position if 1)
        self.current_turn = "white"
        self.last_message = "Select a piece and a move mode."
        self.last_measurement = {}
        for color, pawn_rank, back_rank in (("w", 2, 1), ("b", 7, 8)):
            for i, file in enumerate("abcdefgh", 1):
                self.pieces[f"{color}_pawn{i}"] = QuantumChessPiece(
                    "Pawn", None, f"{file}{pawn_rank}", color)
            for kind, files in (("Rook", "ah"), ("Knight", "bg"),
                                ("Bishop", "cf"), ("Queen", "d"), ("King", "e")):
                for i, file in enumerate(files, 1):
                    suffix = str(i) if len(files) == 2 else ""
                    self.pieces[f"{color}_{kind.lower()}{suffix}"] = QuantumChessPiece(
                        kind, None, f"{file}{back_rank}", color)
        self._rebuild_board()

    @property
    def qc(self):
        return self.quantum.circuit

    @property
    def active_qubits(self):
        return self.quantum.active_qubits

    def positions_for(self, piece_name):
        return self.branches.get(piece_name, (self.pieces[piece_name].position,))

    def _rebuild_board(self):
        # Both branch squares are reserved. Other pieces cannot enter or pass
        # through either square until the joint measurement resolves the board.
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for name, piece in self.pieces.items():
            for position in self.positions_for(name):
                row, col = position_to_grid(position)
                if self.board[row][col] is not None:
                    raise RuntimeError("Two pieces cannot reserve the same square.")
                self.board[row][col] = piece

    def _possible_boards(self):
        if not self.branches:
            yield [row[:] for row in self.board]
            return
        # Check only branches with nonzero amplitude, preserving correlations.
        for bits, probability in self.quantum.probabilities().items():
            if probability < 1e-12:
                continue
            board = [[None for _ in range(8)] for _ in range(8)]
            for name, piece in self.pieces.items():
                position = piece.position
                if name in self.branches:
                    bit = int(bits[-1 - self.quantum.allocations[name]])
                    position = self.branches[name][bit]
                row, col = position_to_grid(position)
                board[row][col] = piece
            yield board

    @staticmethod
    def _in_check(board, color):
        king = next(((r, c) for r in range(8) for c in range(8)
                     if board[r][c] is not None and board[r][c].color == color
                     and board[r][c].name == "King"), None)
        if king is None:
            return True
        kr, kc = king
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece is None or piece.color == color:
                    continue
                dr, dc = kr - r, kc - c
                if piece.name == "Pawn":
                    if dr == (-1 if piece.color == "w" else 1) and abs(dc) == 1:
                        return True
                elif piece.name == "Knight":
                    if (abs(dr), abs(dc)) in {(1, 2), (2, 1)}:
                        return True
                elif piece.name == "King":
                    if max(abs(dr), abs(dc)) == 1:
                        return True
                else:
                    straight = dr == 0 or dc == 0
                    diagonal = abs(dr) == abs(dc)
                    if not ((straight and piece.name in {"Rook", "Queen"})
                            or (diagonal and piece.name in {"Bishop", "Queen"})):
                        continue
                    sr, sc = (dr > 0) - (dr < 0), (dc > 0) - (dc < 0)
                    nr, nc = r + sr, c + sc
                    while (nr, nc) != king and board[nr][nc] is None:
                        nr, nc = nr + sr, nc + sc
                    if (nr, nc) == king:
                        return True
        return False

    def is_king_in_check(self, color):
        return any(self._in_check(board, color[0]) for board in self._possible_boards())

    def _validate_move(self, piece_name, target_position, move_type, entangle_with):
        if move_type not in {"classical", "superposition", "entangle"}:
            raise ValueError("Choose classical, superposition, or entangle.")
        position_to_grid(target_position)
        if piece_name not in self.pieces:
            raise ValueError("Select a piece on the board.")
        piece = self.pieces[piece_name]
        if piece.color != self.current_turn[0]:
            raise ValueError(f"It is {self.current_turn}'s turn.")
        if piece_name in self.branches:
            raise ValueError("Measure the board before moving a split piece.")
        if target_position not in piece.get_valid_moves(self.board):
            raise ValueError("That piece cannot move to this square.")
        er, ec = position_to_grid(target_position)
        occupant = self.board[er][ec]
        if occupant is not None:
            if occupant.name == "King":
                raise ValueError("Kings cannot be captured.")
            if any(occupant is self.pieces[name] for name in self.branches):
                raise ValueError("Measure the board before capturing a split piece.")
        if move_type != "classical":
            if self.active_qubits >= self.num_qubits:
                raise ValueError("All qubits are in use. Measure the board to free them.")
            if occupant is not None or piece.name == "King":
                raise ValueError("Split moves require an empty square and a non-king piece.")
            if piece.name == "Pawn" and er in (0, 7):
                raise ValueError("Use a classical move to promote a pawn.")
        if move_type == "entangle":
            if (entangle_with not in self.branches
                    or self.pieces[entangle_with].color != piece.color):
                raise ValueError("Choose one of your already split pieces as the control.")
        sr, sc = position_to_grid(piece.position)
        for board in self._possible_boards():
            if move_type != "classical" and self._in_check(board, piece.color):
                raise ValueError("Resolve check with a classical move before splitting.")
            board[sr][sc] = None
            board[er][ec] = piece
            if self._in_check(board, piece.color):
                raise ValueError("This move could leave your king in check.")

    def validate_move(self, piece_name, target_position, move_type="classical", entangle_with=None):
        try:
            self._validate_move(piece_name, target_position, move_type, entangle_with)
        except ValueError as error:
            self.last_message = str(error)
            return False
        return True

    def legal_moves(self, piece_name, move_type="classical", entangle_with=None):
        if piece_name not in self.pieces or piece_name in self.branches:
            return []
        legal = []
        for target in self.pieces[piece_name].get_valid_moves(self.board):
            try:
                self._validate_move(piece_name, target, move_type, entangle_with)
            except ValueError:
                continue
            legal.append(target)
        return legal

    def move_piece(self, piece_name, target_position, move_type="classical", entangle_with=None):
        if move_type == "measure":
            return self.measure_board()
        if not self.validate_move(piece_name, target_position, move_type, entangle_with):
            return False
        piece = self.pieces[piece_name]
        if move_type == "classical":
            captured = next((name for name, other in self.pieces.items()
                             if other.position == target_position), None)
            if captured is not None:
                del self.pieces[captured]
            piece.position = target_position
            if piece.name == "Pawn" and target_position[1] in "18":
                piece.name = "Queen"
            self.last_message = f"{self.current_turn.capitalize()} {piece.name.lower()} moved to {target_position}."
        else:
            control = entangle_with if move_type == "entangle" else None
            piece.qubit_index = self.quantum.split(piece_name, control=control)
            self.branches[piece_name] = (piece.position, target_position)
            self.last_message = (
                f"{self.current_turn.capitalize()} {piece.name.lower()}: "
                f"{piece.position} or {target_position} (q{piece.qubit_index})."
            )
            if control is not None:
                self.last_message += f" Correlated with q{self.pieces[control].qubit_index}."
        self._rebuild_board()
        self.switch_turn()
        return True

    def measure_board(self):
        if not self.branches:
            self.last_message = "No split pieces to measure."
            return False
        if self.is_king_in_check(self.current_turn):
            self.last_message = "Move out of check in every branch before using a turn to measure."
            return False
        outcomes = self.quantum.measure_all()
        for name, bit in outcomes.items():
            self.pieces[name].position = self.branches[name][bit]
            self.pieces[name].qubit_index = None
        self.last_measurement = outcomes
        self.branches.clear()
        self._rebuild_board()
        self.last_message = "Measured: " + ", ".join(
            f"{'White' if self.pieces[name].color == 'w' else 'Black'} "
            f"{self.pieces[name].name.lower()} → {self.pieces[name].position}" for name in outcomes)
        self.switch_turn()
        return True

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def execute_move(self, piece_name, target_position, move_type="classical", entangle_with=None):
        return self.move_piece(piece_name, target_position, move_type, entangle_with)

    def display_board(self):
        for row in self.board:
            print(" ".join(piece.name[0] if piece else "." for piece in row))

    def start_game(self):
        while True:
            self.display_board()
            piece = input(f"{self.current_turn}: piece, measure, or quit: ")
            if piece == "quit":
                return
            if piece == "measure":
                self.measure_board()
            else:
                target = input("Target square: ")
                mode = input("Mode (classical, superposition, entangle): ")
                control = input("Split control piece: ") if mode == "entangle" else None
                self.move_piece(piece, target, mode, control)
            print(self.last_message)
