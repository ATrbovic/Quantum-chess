import unittest

from qiskit.quantum_info import Statevector, partial_trace

from quantum_logic import (
    QuantumRegister, apply_superposition, initialize_circuit, measure_circuit,
    simulate_probabilistic_outcome,
)


class QuantumLogicTests(unittest.TestCase):
    def test_qubit_budget_validation(self):
        for invalid in (0, 11, 32, -1, 1.5, True, "10"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                initialize_circuit(invalid)
        self.assertEqual(initialize_circuit(10).num_qubits, 10)

    def test_hadamard_interference(self):
        circuit = initialize_circuit(1)
        apply_superposition(circuit, 0)
        probabilities = Statevector.from_instruction(circuit).probabilities()
        self.assertAlmostEqual(probabilities[0], 0.5)
        self.assertAlmostEqual(probabilities[1], 0.5)
        apply_superposition(circuit, 0)
        self.assertEqual(measure_circuit(circuit, [0], seed=7), "0")

    def test_bell_state_is_entangled(self):
        register = QuantumRegister(2)
        register.split("control")
        register.split("target", control="control")
        probabilities = register.probabilities()
        self.assertEqual(set(probabilities), {"00", "11"})
        self.assertAlmostEqual(probabilities["00"], 0.5)
        # A subsystem of this pure joint state is mixed: this checks genuine
        # entanglement rather than merely checking that CX was appended.
        reduced = partial_trace(Statevector.from_instruction(register.circuit), [1])
        self.assertAlmostEqual(reduced.purity().real, 0.5)

    def test_ten_qubit_ghz_sampling_and_reuse(self):
        register = QuantumRegister(10, seed=42)
        register.split("0")
        for i in range(1, 10):
            register.split(str(i), control="0")
        probabilities = register.probabilities()
        self.assertEqual(set(probabilities), {"0" * 10, "1" * 10})
        self.assertAlmostEqual(probabilities["1" * 10], 0.5)
        with self.assertRaises(ValueError):
            register.split("overflow")
        outcomes = register.measure_all()
        self.assertEqual(len(outcomes), 10)
        self.assertEqual(len(set(outcomes.values())), 1)
        self.assertEqual(register.active_qubits, 0)
        self.assertEqual(register.measure_all(), {})
        self.assertEqual(register.split("reused"), 0)

    def test_measurement_bit_order_and_no_circuit_mutation(self):
        circuit = initialize_circuit(10)
        circuit.x(9)
        original = circuit.copy()
        self.assertEqual(measure_circuit(circuit, [9, 2], seed=1), "01")
        self.assertEqual(measure_circuit(circuit, [2, 9], seed=1), "10")
        self.assertEqual(simulate_probabilistic_outcome(circuit, 9, seed=1), {"1": 1.0})
        self.assertEqual(circuit, original)
        for indices in ([], [0, 0], [-1], [10]):
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                measure_circuit(circuit, indices)

    def test_seed_reproduces_sequence_without_repeating_each_draw(self):
        def sequence():
            register = QuantumRegister(1, seed=42)
            outcomes = []
            for _ in range(20):
                register.split("piece")
                outcomes.append(register.measure_all()["piece"])
            return outcomes
        first = sequence()
        self.assertEqual(first, sequence())
        self.assertEqual(set(first), {0, 1})

    def test_bad_allocations_leave_state_unchanged(self):
        register = QuantumRegister(2)
        register.split("piece")
        before = register.circuit.copy()
        for owner, control in (("piece", None), ("other", "missing")):
            with self.assertRaises(ValueError):
                register.split(owner, control)
        self.assertEqual(register.circuit, before)
        self.assertEqual(register.active_qubits, 1)


if __name__ == "__main__":
    unittest.main()
