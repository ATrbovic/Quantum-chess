"""Desktop controls for the bounded quantum chess variant."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QVBoxLayout, QWidget,
)

from utils import grid_to_position


SYMBOLS = {
    "w": dict(zip(("King", "Queen", "Rook", "Bishop", "Knight", "Pawn"), "♔♕♖♗♘♙")),
    "b": dict(zip(("King", "Queen", "Rook", "Bishop", "Knight", "Pawn"), "♚♛♜♝♞♟")),
}


class ChessGUI(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.selected_piece = None
        self.setWindowTitle("Quantum Chess · Qiskit")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        controls = QHBoxLayout()
        self.move_mode = QComboBox()
        self.move_mode.addItem("Classical move", "classical")
        self.move_mode.addItem("Split: stay or move", "superposition")
        self.move_mode.addItem("Entangled split", "entangle")
        controls.addWidget(self.move_mode)
        self.control_piece = QComboBox()
        self.control_piece.setToolTip("An already split piece of your color controls the new branch.")
        controls.addWidget(self.control_piece)
        self.measure_button = QPushButton("Measure board")
        self.measure_button.setToolTip("Resolve all branches together and free their qubits. Uses your turn.")
        self.measure_button.clicked.connect(self.measure_board)
        controls.addWidget(self.measure_button)
        layout.addLayout(controls)

        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(0)
        layout.addLayout(self.board_layout)
        self.squares = {}
        for i, file in enumerate("abcdefgh"):
            file_label = QLabel(file)
            file_label.setAlignment(Qt.AlignCenter)
            self.board_layout.addWidget(file_label, 8, i + 1)
            rank_label = QLabel(str(8 - i))
            rank_label.setAlignment(Qt.AlignCenter)
            self.board_layout.addWidget(rank_label, i, 0)
        for row in range(8):
            for col in range(8):
                button = QPushButton()
                button.setFixedSize(64, 64)
                button.setFont(QFont("Arial", 26))
                button.clicked.connect(lambda checked=False, r=row, c=col: self.on_square_click(r, c))
                self.board_layout.addWidget(button, row, col + 1)
                self.squares[(row, col)] = button
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumHeight(48)
        self.message_label.setMaximumWidth(520)
        layout.addWidget(self.message_label)
        help_label = QLabel(
            "Select a piece, then a highlighted square. Split pieces occupy two reserved squares; "
            "a 0 outcome stays and a 1 outcome moves. Entangled splits share the control's outcome. "
            "Measure before moving or capturing a split piece. Measurement uses a turn."
        )
        help_label.setWordWrap(True)
        help_label.setMaximumWidth(520)
        layout.addWidget(help_label)
        self.move_mode.currentIndexChanged.connect(self.mode_changed)
        self.control_piece.currentIndexChanged.connect(self.highlight_valid_moves)
        self.update_board()

    def mode_changed(self):
        self.control_piece.setEnabled(self.move_mode.currentData() == "entangle")
        self.highlight_valid_moves()

    def update_status(self):
        check = " · Check" if self.game.is_king_in_check(self.game.current_turn) else ""
        self.status_label.setText(
            f"{self.game.current_turn.capitalize()}'s turn · "
            f"Qubits {self.game.active_qubits}/{self.game.num_qubits} · Qiskit{check}"
        )
        self.message_label.setText(self.game.last_message)

    def update_board(self):
        previous = self.control_piece.currentData()
        self.control_piece.blockSignals(True)
        self.control_piece.clear()
        for name in self.game.branches:
            if self.game.pieces[name].color == self.game.current_turn[0]:
                piece = self.game.pieces[name]
                squares = " / ".join(self.game.positions_for(name))
                self.control_piece.addItem(f"{piece.name} {squares} (q{piece.qubit_index})", name)
        index = self.control_piece.findData(previous)
        if index >= 0:
            self.control_piece.setCurrentIndex(index)
        if self.control_piece.count() == 0:
            self.control_piece.addItem("No split control available", None)
        self.control_piece.blockSignals(False)
        self.control_piece.setEnabled(self.move_mode.currentData() == "entangle")
        self.measure_button.setEnabled(bool(self.game.branches))
        self.update_status()
        self.highlight_valid_moves()

    def highlight_valid_moves(self, *_):
        mode = self.move_mode.currentData()
        control = self.control_piece.currentData()
        legal = self.game.legal_moves(self.selected_piece, mode, control) if self.selected_piece else []
        selected = self.game.positions_for(self.selected_piece) if self.selected_piece else ()
        names = {id(piece): name for name, piece in self.game.pieces.items()}
        for (row, col), button in self.squares.items():
            position = grid_to_position(row, col)
            piece = self.game.board[row][col]
            color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
            if position in legal:
                color = "#90EE90"
            if position in selected:
                color = "#FFD700"
            button.setStyleSheet(f"background-color: {color}; color: #151515; border: 1px solid #735539;")
            if piece is None:
                button.setText("")
                button.setToolTip(position)
                continue
            name = names[id(piece)]
            suffix = ""
            detail = f"{name} · {position}"
            if name in self.game.branches:
                bit = self.game.branches[name].index(position)
                suffix = str(bit)
                detail += f" · q{piece.qubit_index} branch {bit} · measure to resolve"
            button.setText(SYMBOLS[piece.color][piece.name] + suffix)
            button.setToolTip(detail)

    def on_square_click(self, row, col):
        piece = self.game.board[row][col]
        names = {id(p): name for name, p in self.game.pieces.items()}
        if piece is not None and piece.color == self.game.current_turn[0]:
            self.selected_piece = names[id(piece)]
            self.highlight_valid_moves()
            if self.selected_piece in self.game.branches:
                self.message_label.setText("This piece is split. Measure the board before moving it.")
            return
        if self.selected_piece is None:
            return
        try:
            moved = self.game.move_piece(
                self.selected_piece, grid_to_position(row, col),
                self.move_mode.currentData(), self.control_piece.currentData(),
            )
            if moved:
                self.selected_piece = None
            self.update_board()
        except Exception as error:
            self.message_label.setText(f"Move failed: {error}")

    def measure_board(self):
        try:
            self.game.measure_board()
            self.selected_piece = None
            self.update_board()
        except Exception as error:
            self.message_label.setText(f"Measurement failed: {error}")

    def run(self):
        self.show()
