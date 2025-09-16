from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QVBoxLayout, QStatusBar
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from game import QuantumChessGame
from utils import position_to_grid, grid_to_position

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class ChessGUI(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Quantum Chess")
        self.setGeometry(100, 100, 600, 650)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)
        
        # Create status label
        self.status_label = QLabel("White's Turn")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setStyleSheet("background-color: #E6E6FA; padding: 10px; border: 2px solid #4B0082;")
        main_layout.addWidget(self.status_label)
        
        # Create board layout
        self.layout = QGridLayout()
        board_widget = QWidget()
        board_widget.setLayout(self.layout)
        main_layout.addWidget(board_widget)
        
        self.squares = {}
        self.piece_labels = {}
        self.selected_piece = None
        self.create_board()
        self.place_pieces()
        self.update_status()

    def update_status(self):
        """Update the status label with current turn information."""
        current_player = "White" if self.game.current_turn == "white" else "Black"
        self.status_label.setText(f"{current_player}'s Turn")
        
        # Change color based on current player
        if self.game.current_turn == "white":
            self.status_label.setStyleSheet("background-color: #E6E6FA; color: #4B0082; padding: 10px; border: 2px solid #4B0082; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("background-color: #FFE4E1; color: #8B0000; padding: 10px; border: 2px solid #8B0000; font-weight: bold;")

    def on_square_click(self, row, col):
        """Handle click events on the squares."""
        if self.selected_piece:
            piece_name = self.selected_piece
            try:
                piece = self.game.pieces[piece_name]
                target_position = grid_to_position(row, col)

                if target_position in piece.get_valid_moves(self.game.board):
                    self.game.move_piece(piece_name, target_position, move_type="classical")
                    self.update_board()
                    self.update_status()
                    self.selected_piece = None
                    print(f"Moved {piece_name} to {target_position}")
                else:
                    print(f"Invalid move for {piece_name} to {target_position}")
            except KeyError:
                print(f"Error: Piece {piece_name} not found in pieces dictionary")
                self.selected_piece = None
                self.update_board()
            except Exception as e:
                print(f"Error during move: {e}")
                self.selected_piece = None
                self.update_board()
        else:
            print(f"No piece selected. Clicked on square ({row}, {col})")

    def update_gui(self):
        """Update the board display based on the current game state."""
        for piece_name, (label, _) in self.piece_labels.items():
            label.deleteLater()
        self.piece_labels.clear()
        self.place_pieces()

    def create_board(self):
        """Create the chessboard with alternating colors and square IDs."""
        for row in range(8):
            for col in range(8):
                # Traditional chess board colors
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                frame = QWidget()
                frame.setStyleSheet(f"background-color: {color}; border: 1px solid #8B4513;")
                frame.setFixedSize(60, 60)
                self.layout.addWidget(frame, row, col)

                # Store frame with its position
                self.squares[(row, col)] = frame

                # Connect square click event
                frame.mousePressEvent = lambda event, row=row, col=col: self.on_square_click(row, col)

    def place_pieces(self):
        """Place the pieces on the board based on the game state."""
        # Unicode chess piece symbols
        piece_symbols = {
            "w": {
                "Pawn": "♙", "Rook": "♖", "Knight": "♘", 
                "Bishop": "♗", "Queen": "♕", "King": "♔"
            },
            "b": {
                "Pawn": "♟", "Rook": "♜", "Knight": "♞", 
                "Bishop": "♝", "Queen": "♛", "King": "♚"
            }
        }
        
        for piece_name, piece in self.game.pieces.items():
            row, col = position_to_grid(piece.position)
            print(f"Placing {piece.name} at {piece.position} -> grid ({row}, {col})")
            
            # Get the appropriate symbol
            symbol = piece_symbols[piece.color][piece.name]
            
            label = ClickableLabel(symbol, self.squares[(row, col)])
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 24, QFont.Bold))
            
            # Different styling for white and black pieces
            if piece.color == "w":
                label.setStyleSheet("background-color: lightblue; border: 2px solid darkblue; color: white; font-weight: bold;")
            else:
                label.setStyleSheet("background-color: darkred; border: 2px solid maroon; color: white; font-weight: bold;")
            
            label.clicked.connect(self.on_piece_click)
            label.show()
            self.piece_labels[piece_name] = (label, (row, col))
            print(f"Label for {piece.name} created at grid ({row}, {col})")

    def on_piece_click(self):
        """Handle click events on the pieces."""
        sender = self.sender()
        piece_name = None

        # Find which piece was clicked
        for name, (label, _) in self.piece_labels.items():
            if label == sender:
                piece_name = name
                break

        if piece_name:
            piece = self.game.pieces[piece_name]
            
            # Check if it's the correct player's turn
            if (self.game.current_turn == "white" and piece.color == "w") or \
               (self.game.current_turn == "black" and piece.color == "b"):
                print(f"Piece {piece_name} clicked!")
                self.selected_piece = piece_name
                self.highlight_valid_moves(piece_name)
            else:
                current_player = "White" if self.game.current_turn == "white" else "Black"
                print(f"It's {current_player}'s turn! You can't move the opponent's pieces.")
                self.status_label.setText(f"It's {current_player}'s turn!")
                # Flash the status for emphasis
                self.status_label.setStyleSheet("background-color: #FF6B6B; color: white; padding: 10px; border: 2px solid #FF0000; font-weight: bold;")
                # Reset after a moment (you could use QTimer for this, but for now this is simpler)
                QApplication.processEvents()
                import time
                time.sleep(0.5)
                self.update_status()

    def highlight_valid_moves(self, piece_name):
        """Highlight valid moves for the selected piece."""
        piece = self.game.pieces[piece_name]
        valid_moves = piece.get_valid_moves(self.game.board)
        print(f"Valid moves for {piece_name}: {valid_moves}")

        # Reset all square styles to default
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"  # Chess board colors
                self.squares[(row, col)].setStyleSheet(f"background-color: {color}; border: 1px solid #8B4513;")

        # Highlight the selected piece
        selected_row, selected_col = position_to_grid(piece.position)
        self.squares[(selected_row, selected_col)].setStyleSheet("background-color: #FFD700; border: 2px solid #FF8C00;")

        # Highlight valid moves
        for move in valid_moves:
            row, col = position_to_grid(move)
            self.squares[(row, col)].setStyleSheet("background-color: #90EE90; border: 2px solid #32CD32;")

    def on_square_click(self, row, col):
        """Handle click events on the squares."""
        if self.selected_piece:
            piece_name = self.selected_piece
            piece = self.game.pieces[piece_name]
            target_position = grid_to_position(row, col)

            if target_position in piece.get_valid_moves(self.game.board):
                self.game.move_piece(piece_name, target_position, move_type="classical")
                self.update_board()
                self.selected_piece = None
                print(f"Moved {piece_name} to {target_position}")
            else:
                print(f"Invalid move for {piece_name} to {target_position}")

    def update_board(self):
        """Update the board display based on the current game state."""
        for piece_name, (label, _) in self.piece_labels.items():
            label.deleteLater()
        self.piece_labels.clear()
        self.place_pieces()

    def run(self):
        """Run the main event loop."""
        self.show()

