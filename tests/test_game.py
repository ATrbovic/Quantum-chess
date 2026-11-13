import unittest

from game import QuantumChessGame
from pieces import QuantumChessPiece


def custom_game(spec):
    game = QuantumChessGame(seed=42)
    game.pieces = {name: QuantumChessPiece(kind, None, position, color)
                   for name, kind, position, color in spec}
    game._rebuild_board()
    return game


class GameTests(unittest.TestCase):
    def test_all_32_pieces_start_classical(self):
        game = QuantumChessGame()
        self.assertEqual(len(game.pieces), 32)
        self.assertEqual(game.qc.num_qubits, 10)
        self.assertEqual(game.active_qubits, 0)
        self.assertTrue(all(piece.qubit_index is None for piece in game.pieces.values()))

    def test_ten_live_branches_reject_eleventh_and_measure_atomically(self):
        game = QuantumChessGame(seed=42)
        for i, file in enumerate("abcde", 1):
            self.assertTrue(game.move_piece(f"w_pawn{i}", f"{file}3", "superposition"), game.last_message)
            self.assertTrue(game.move_piece(f"b_pawn{i}", f"{file}6", "superposition"), game.last_message)
        self.assertEqual(game.active_qubits, 10)
        before = game.qc.copy()
        self.assertFalse(game.move_piece("w_pawn6", "f3", "superposition"))
        self.assertEqual(game.qc, before)
        self.assertEqual(game.current_turn, "white")
        self.assertEqual(game.pieces["w_pawn6"].position, "f2")
        self.assertTrue(game.measure_board())
        self.assertEqual(game.active_qubits, 0)
        self.assertEqual(len(game.pieces), 32)
        self.assertEqual(sum(p is not None for row in game.board for p in row), 32)
        for name, bit in game.last_measurement.items():
            color, pawn = name.split("_")
            file = "abcdefgh"[int(pawn[4:]) - 1]
            rank = (2 + bit) if color == "w" else (7 - bit)
            self.assertEqual(game.pieces[name].position, f"{file}{rank}")
        positions = {name: p.position for name, p in game.pieces.items()}
        self.assertFalse(game.measure_board())
        self.assertEqual(positions, {name: p.position for name, p in game.pieces.items()})
        self.assertEqual(game.current_turn, "black")
        self.assertTrue(game.move_piece("b_pawn6", "f6", "superposition"))
        self.assertEqual(game.pieces["b_pawn6"].qubit_index, 0)

    def test_correlated_moves_resolve_to_matching_branches(self):
        seen = set()
        for seed in range(8):
            game = QuantumChessGame(seed=seed)
            self.assertTrue(game.move_piece("w_pawn5", "e4", "superposition"))
            self.assertTrue(game.move_piece("b_pawn1", "a6"))
            self.assertTrue(game.move_piece("w_pawn4", "d4", "entangle", "w_pawn5"))
            self.assertTrue(game.measure_board())
            self.assertEqual(game.last_measurement["w_pawn5"], game.last_measurement["w_pawn4"])
            bit = game.last_measurement["w_pawn5"]
            seen.add(bit)
            self.assertEqual(game.pieces["w_pawn5"].position, "e4" if bit else "e2")
            self.assertEqual(game.pieces["w_pawn4"].position, "d4" if bit else "d2")
        self.assertEqual(seen, {0, 1})

    def test_failed_moves_preserve_board_turn_and_circuit(self):
        game = QuantumChessGame()
        for name, target, mode, control in (
            ("w_pawn1", "a5", "classical", None),
            ("b_pawn1", "a6", "classical", None),
            ("w_pawn1", "a3", "entangle", "missing"),
            ("w_pawn1", "a9", "superposition", None),
            ("missing", "a3", "classical", None),
            ("w_pawn1", "a3", "unknown", None),
        ):
            with self.subTest(name=name, target=target, mode=mode):
                self.assertFalse(game.move_piece(name, target, mode, control))
                self.assertEqual(game.current_turn, "white")
                self.assertEqual(game.active_qubits, 0)
                self.assertEqual(game.pieces["w_pawn1"].position, "a2")
                self.assertEqual(len(game.qc.data), 0)

    def test_split_squares_reserved_and_piece_cannot_move_again(self):
        game = QuantumChessGame()
        self.assertTrue(game.move_piece("w_pawn1", "a3", "superposition"))
        self.assertIs(game.board[6][0], game.board[5][0])
        self.assertTrue(game.move_piece("b_pawn1", "a6"))
        self.assertFalse(game.move_piece("w_pawn1", "a4"))
        self.assertFalse(game.move_piece("w_rook1", "a2"))
        self.assertEqual(game.active_qubits, 1)

    def test_capture_removes_attacker_during_king_safety_validation(self):
        game = custom_game([
            ("w_king", "King", "e1", "w"), ("b_king", "King", "a8", "b"),
            ("b_rook", "Rook", "e2", "b"),
        ])
        self.assertTrue(game.is_king_in_check("white"))
        self.assertTrue(game.move_piece("w_king", "e2"), game.last_message)
        self.assertNotIn("b_rook", game.pieces)
        self.assertFalse(game.is_king_in_check("white"))

    def test_quantum_move_cannot_expose_king_in_one_branch(self):
        game = custom_game([
            ("w_king", "King", "e1", "w"), ("b_king", "King", "a8", "b"),
            ("w_rook", "Rook", "e2", "w"), ("b_rook", "Rook", "e8", "b"),
        ])
        self.assertFalse(game.move_piece("w_rook", "f2", "superposition"))
        self.assertEqual(game.active_qubits, 0)

    def test_king_safety_checks_existing_split_branches(self):
        game = custom_game([
            ("w_king", "King", "e1", "w"), ("b_king", "King", "a8", "b"),
            ("w_knight", "Knight", "g1", "w"), ("b_rook", "Rook", "d8", "b"),
        ])
        self.assertTrue(game.move_piece("w_knight", "f3"))
        self.assertTrue(game.move_piece("b_rook", "e8", "superposition"))
        # e2 is attacked only when the black rook resolves to e8.
        self.assertFalse(game.move_piece("w_king", "e2"))
        self.assertTrue(game.move_piece("w_king", "f1"))

    def test_capture_split_piece_requires_measurement(self):
        game = custom_game([
            ("w_king", "King", "h1", "w"), ("b_king", "King", "h8", "b"),
            ("w_pawn", "Pawn", "b2", "w"), ("b_rook", "Rook", "a3", "b"),
        ])
        self.assertTrue(game.move_piece("w_pawn", "b3", "superposition"))
        self.assertFalse(game.move_piece("b_rook", "b3"))
        self.assertIn("w_pawn", game.pieces)
        self.assertEqual(game.active_qubits, 1)

    def test_pawn_attack_geometry_and_promotion(self):
        game = custom_game([
            ("w_king", "King", "e4", "w"), ("b_king", "King", "h8", "b"),
            ("b_pawn", "Pawn", "d5", "b"), ("w_pawn", "Pawn", "a7", "w"),
        ])
        self.assertTrue(game.is_king_in_check("white"))
        self.assertFalse(game.move_piece("w_pawn", "a8"))
        self.assertTrue(game.move_piece("w_king", "d4"))
        game.current_turn = "white"
        self.assertFalse(game.move_piece("w_pawn", "a8", "superposition"))
        self.assertTrue(game.move_piece("w_pawn", "a8"))
        self.assertEqual(game.pieces["w_pawn"].name, "Queen")

    def test_smaller_budget_is_enforced(self):
        game = QuantumChessGame(num_qubits=1)
        self.assertTrue(game.move_piece("w_pawn1", "a3", "superposition"))
        self.assertFalse(game.move_piece("b_pawn1", "a6", "superposition"))
        self.assertTrue(game.move_piece("b_pawn1", "a6"))

    def test_measurement_cannot_forfeit_turn_while_in_check(self):
        game = custom_game([
            ("w_king", "King", "e1", "w"), ("b_king", "King", "a8", "b"),
            ("w_knight", "Knight", "g1", "w"), ("b_rook", "Rook", "d8", "b"),
        ])
        self.assertTrue(game.move_piece("w_knight", "f3"))
        self.assertTrue(game.move_piece("b_rook", "e8", "superposition"))
        before = game.qc.copy()
        self.assertFalse(game.measure_board())
        self.assertEqual(game.current_turn, "white")
        self.assertEqual(game.qc, before)
        self.assertEqual(game.active_qubits, 1)


if __name__ == "__main__":
    unittest.main()
