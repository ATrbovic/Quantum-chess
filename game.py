from pieces import QuantumChessPiece
from quantum_logic import initialize_circuit, apply_superposition, entangle_pieces, measure_circuit
from utils import position_to_grid, grid_to_position
from PyQt5.QtCore import QThread, pyqtSignal

class QuantumSimulationThread(QThread):
    """Thread to run the quantum simulation asynchronously."""
    finished = pyqtSignal(str)  # Signal to emit the measurement outcome.

    def __init__(self, qc, qubit_indices):
        super().__init__()
        self.qc = qc
        self.qubit_indices = qubit_indices

    def run(self):
        """Run the quantum simulation and emit the result."""
        outcome = measure_circuit(self.qc, self.qubit_indices)
        self.finished.emit(outcome)

class QuantumChessGame:
    def __init__(self):
        self.num_qubits = 32  # Adjust based on the number of pieces and desired complexity
        self.qc = initialize_circuit(self.num_qubits)

        # Initialize the board with None for empty squares
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # Initialize white pieces
        self.pieces = {
            "w_pawn1": QuantumChessPiece("Pawn", 0, "a2", "w"),
            "w_pawn2": QuantumChessPiece("Pawn", 1, "b2", "w"),
            "w_pawn3": QuantumChessPiece("Pawn", 2, "c2", "w"),
            "w_pawn4": QuantumChessPiece("Pawn", 3, "d2", "w"),
            "w_pawn5": QuantumChessPiece("Pawn", 4, "e2", "w"),
            "w_pawn6": QuantumChessPiece("Pawn", 5, "f2", "w"),
            "w_pawn7": QuantumChessPiece("Pawn", 6, "g2", "w"),
            "w_pawn8": QuantumChessPiece("Pawn", 7, "h2", "w"),
            "w_rook1": QuantumChessPiece("Rook", 8, "a1", "w"),
            "w_rook2": QuantumChessPiece("Rook", 9, "h1", "w"),
            "w_knight1": QuantumChessPiece("Knight", 10, "b1", "w"),
            "w_knight2": QuantumChessPiece("Knight", 11, "g1", "w"),
            "w_bishop1": QuantumChessPiece("Bishop", 12, "c1", "w"),
            "w_bishop2": QuantumChessPiece("Bishop", 13, "f1", "w"),
            "w_queen": QuantumChessPiece("Queen", 14, "d1", "w"),
            "w_king": QuantumChessPiece("King", 15, "e1", "w"),

            # Initialize black pieces
            "b_pawn1": QuantumChessPiece("Pawn", 16, "a7", "b"),
            "b_pawn2": QuantumChessPiece("Pawn", 17, "b7", "b"),
            "b_pawn3": QuantumChessPiece("Pawn", 18, "c7", "b"),
            "b_pawn4": QuantumChessPiece("Pawn", 19, "d7", "b"),
            "b_pawn5": QuantumChessPiece("Pawn", 20, "e7", "b"),
            "b_pawn6": QuantumChessPiece("Pawn", 21, "f7", "b"),
            "b_pawn7": QuantumChessPiece("Pawn", 22, "g7", "b"),
            "b_pawn8": QuantumChessPiece("Pawn", 23, "h7", "b"),
            "b_rook1": QuantumChessPiece("Rook", 24, "a8", "b"),
            "b_rook2": QuantumChessPiece("Rook", 25, "h8", "b"),
            "b_knight1": QuantumChessPiece("Knight", 26, "b8", "b"),
            "b_knight2": QuantumChessPiece("Knight", 27, "g8", "b"),
            "b_bishop1": QuantumChessPiece("Bishop", 28, "c8", "b"),
            "b_bishop2": QuantumChessPiece("Bishop", 29, "f8", "b"),
            "b_queen": QuantumChessPiece("Queen", 30, "d8", "b"),
            "b_king": QuantumChessPiece("King", 31, "e8", "b"),
        }

        # Place pieces on the board
        for piece_name, piece in self.pieces.items():
            row, col = position_to_grid(piece.position)
            self.board[row][col] = piece

        self.current_turn = "white"

    def move_piece(self, piece_name, target_position, move_type="superposition"):
        piece = self.pieces[piece_name]
        start_row, start_col = position_to_grid(piece.position)
        end_row, end_col = position_to_grid(target_position)

        # Handle captures
        target_piece = self.board[end_row][end_col]
        if target_piece and target_piece.color != piece.color:
            print(f"{piece.name} captures {target_piece.name} at {target_position}!")
            # Find and remove the captured piece from the pieces dictionary
            captured_piece_name = None
            for name, p in self.pieces.items():
                if p is target_piece:
                    captured_piece_name = name
                    break
            if captured_piece_name:
                del self.pieces[captured_piece_name]

        # Update board position immediately for visual feedback
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.position = target_position

        # Skip quantum simulation for classical moves
        if move_type == "classical":
            self.switch_turn()
            return

        # Handle quantum operations asynchronously
        self.simulation_thread = QuantumSimulationThread(self.qc, [piece.qubit_index])
        self.simulation_thread.finished.connect(self.handle_simulation_result)
        
        # Apply quantum operations in the thread
        if move_type == "superposition":
            self.qc = apply_superposition(self.qc, piece.qubit_index)
        elif move_type == "entangle":
            if piece.qubit_index + 1 < self.num_qubits:
                self.qc = entangle_pieces(self.qc, piece.qubit_index, piece.qubit_index + 1)
        
        # Start the thread
        self.simulation_thread.start()

    def handle_simulation_result(self, outcome):
        """Handle the quantum simulation result"""
        print(f"Quantum operation completed with outcome: {outcome}")
        # Update the GUI here if needed
        self.switch_turn()

    def switch_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def is_game_over(self):
        # Placeholder for game-over conditions (e.g., checkmate)
        return False

    def display_board(self):
        # Placeholder for displaying the current state of the board
        for row in self.board:
            print(" ".join([piece.name[0] if piece else '.' for piece in row]))
        print("\n" + "-" * 17 + "\n")

    def validate_move(self, piece_name, target_position):
        # Placeholder for move validation logic
        return True

    def execute_move(self, piece_name, target_position, move_type="superposition"):
        if self.validate_move(piece_name, target_position):
            self.move_piece(piece_name, target_position, move_type)
        else:
            print("Invalid move. Try again.")

    def start_game(self):
        # Main game loop
        while not self.is_game_over():
            self.display_board()
            piece_name = input(f"{self.current_turn}'s turn. Enter piece name to move: ")
            target_position = input("Enter target position: ")
            move_type = input("Enter move type (superposition, entangle, classical, measure): ")
            self.execute_move(piece_name, target_position, move_type)