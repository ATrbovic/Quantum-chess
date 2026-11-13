import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from game import QuantumChessGame
from gui import ChessGUI
from utils import position_to_grid


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.game = QuantumChessGame(seed=42)
        self.window = ChessGUI(self.game)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def click(self, square):
        self.window.squares[position_to_grid(square)].click()
        self.app.processEvents()

    def test_split_entangle_measure_and_status(self):
        self.window.move_mode.setCurrentIndex(1)
        self.click("e2")
        self.click("e4")
        self.assertEqual(self.game.active_qubits, 1)
        self.assertIn("Black's turn", self.window.status_label.text())
        self.assertEqual(self.window.squares[position_to_grid("e2")].text(), "♙0")
        self.assertEqual(self.window.squares[position_to_grid("e4")].text(), "♙1")
        self.window.move_mode.setCurrentIndex(0)
        self.click("a7")
        self.click("a6")
        self.window.move_mode.setCurrentIndex(2)
        self.assertEqual(self.window.control_piece.currentData(), "w_pawn5")
        self.click("d2")
        self.click("d4")
        self.assertEqual(self.game.active_qubits, 2)
        self.window.measure_button.click()
        self.assertEqual(self.game.active_qubits, 0)
        self.assertEqual(self.game.last_measurement["w_pawn4"], self.game.last_measurement["w_pawn5"])
        self.assertIn("White's turn", self.window.status_label.text())
        self.assertIn("Qubits 0/10", self.window.status_label.text())
        self.assertFalse(self.window.measure_button.isEnabled())

    def test_capture_by_clicking_an_opponents_piece(self):
        for source, target in (("e2", "e4"), ("d7", "d5"), ("e4", "d5")):
            self.click(source)
            self.click(target)
        self.assertNotIn("b_pawn4", self.game.pieces)
        self.assertEqual(self.game.pieces["w_pawn5"].position, "d5")
        self.assertIn("Black's turn", self.window.status_label.text())

    def test_rejected_move_is_visible_and_keeps_turn(self):
        self.click("a2")
        self.click("a5")
        self.assertEqual(self.game.current_turn, "white")
        self.assertIn("cannot move", self.window.message_label.text())
        self.assertEqual(self.game.pieces["w_pawn1"].position, "a2")


if __name__ == "__main__":
    unittest.main()
