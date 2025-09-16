from game import QuantumChessGame
from gui import ChessGUI
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QPushButton


def main():
    game = QuantumChessGame()
    gui = ChessGUI(game)
    gui.run()

    
if __name__ == "__main__":
    app = QApplication([])
    game = QuantumChessGame()
    gui = ChessGUI(game)
    gui.run()
    app.exec_()