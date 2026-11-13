"""Run the desktop game or its terminal interface."""

import argparse
import sys

from game import QuantumChessGame


def main():
    parser = argparse.ArgumentParser(description="Quantum chess with local Qiskit simulation")
    parser.add_argument("--qubits", type=int, choices=range(1, 11), default=10,
                        metavar="1-10", help="maximum active quantum choices (default: 10)")
    parser.add_argument("--cli", action="store_true", help="use the terminal interface")
    parser.add_argument("--seed", type=int, help="reproduce a measurement sequence for debugging")
    args = parser.parse_args()
    game = QuantumChessGame(args.qubits, seed=args.seed)
    if args.cli:
        game.start_game()
        return 0
    from PyQt5.QtWidgets import QApplication
    from gui import ChessGUI

    app = QApplication(sys.argv[:1])
    gui = ChessGUI(game)
    gui.run()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
