"""Bounded local quantum simulation using Qiskit's V2 statevector sampler."""

from numbers import Integral

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

MAX_QUBITS = 10


def initialize_circuit(num_qubits=MAX_QUBITS):
    if (isinstance(num_qubits, bool) or not isinstance(num_qubits, Integral)
            or not 1 <= num_qubits <= MAX_QUBITS):
        raise ValueError("Qubit count must be an integer from 1 to 10.")
    return QuantumCircuit(int(num_qubits))


def apply_superposition(qc, qubit_index):
    qc.h(qubit_index)
    return qc


def entangle_pieces(qc, control, target):
    qc.cx(control, target)
    return qc


def _measurement_circuit(qc, qubit_indices):
    indices = list(qubit_indices)
    if not indices or len(set(indices)) != len(indices):
        raise ValueError("Select at least one distinct qubit to measure.")
    if any(isinstance(i, bool) or not isinstance(i, Integral)
           or not 0 <= i < qc.num_qubits for i in indices):
        raise ValueError("Measurement index is outside the circuit.")
    if qc.num_clbits or any(item.operation.name in {"measure", "reset"} for item in qc.data):
        raise ValueError("Provide a quantum preparation circuit without measurements or resets.")
    measured = QuantumCircuit(qc.num_qubits)
    measured.compose(qc, qubits=range(qc.num_qubits), inplace=True)
    register = ClassicalRegister(len(indices), "meas")
    measured.add_register(register)
    for bit, qubit in enumerate(indices):
        measured.measure(qubit, register[bit])
    return measured


def measure_circuit(qc, qubit_indices, *, seed=None):
    """Sample once. Rightmost output bit corresponds to qubit_indices[0]."""
    measured = _measurement_circuit(qc, qubit_indices)
    result = StatevectorSampler(seed=seed).run([measured], shots=1).result()
    return result[0].data.meas.get_bitstrings()[0]


def simulate_probabilistic_outcome(qc, qubit_index, *, shots=1024, seed=None):
    """Return sampled frequencies without mutating the input circuit."""
    if isinstance(shots, bool) or not isinstance(shots, Integral) or shots < 1:
        raise ValueError("Shots must be a positive integer.")
    measured = _measurement_circuit(qc, [qubit_index])
    result = StatevectorSampler(seed=seed).run([measured], shots=shots).result()
    return {bits: count / shots
            for bits, count in result[0].data.meas.get_counts().items()}


class QuantumRegister:
    """Preserve coherent branches until a joint measurement resolves all of them.

    A slot starts in |0>. H creates an independent choice; CX from an existing
    branch creates a correlated choice. All slots are reusable after resolution.
    """

    def __init__(self, num_qubits=MAX_QUBITS, seed=None):
        self.circuit = initialize_circuit(num_qubits)
        self.num_qubits = self.circuit.num_qubits
        self.allocations = {}
        self.sampler = StatevectorSampler(seed=np.random.default_rng(seed))

    @property
    def active_qubits(self):
        return len(self.allocations)

    def split(self, owner, control=None):
        if owner in self.allocations:
            raise ValueError("Measure this piece before splitting it again.")
        if control is not None and control not in self.allocations:
            raise ValueError("Choose an already split piece as the entanglement control.")
        if self.active_qubits == self.num_qubits:
            raise ValueError("All qubits are in use. Measure the board to free them.")
        used = set(self.allocations.values())
        index = next(i for i in range(self.num_qubits) if i not in used)
        if control is None:
            apply_superposition(self.circuit, index)
        else:
            entangle_pieces(self.circuit, self.allocations[control], index)
        self.allocations[owner] = index
        return index

    def probabilities(self):
        """Exact joint distribution in Qiskit's little-endian bit order."""
        return Statevector.from_instruction(self.circuit).probabilities_dict()

    def measure_all(self):
        if not self.allocations:
            return {}
        owners = list(self.allocations)
        indices = [self.allocations[owner] for owner in owners]
        measured = _measurement_circuit(self.circuit, indices)
        result = self.sampler.run([measured], shots=1).result()
        bitstring = result[0].data.meas.get_bitstrings()[0]
        outcomes = {owner: int(bit) for owner, bit in zip(owners, reversed(bitstring))}
        # The caller commits these outcomes to the board. Old branches cannot
        # reroll: after joint collapse, all slots return to their initial state.
        self.circuit = initialize_circuit(self.num_qubits)
        self.allocations.clear()
        return outcomes
