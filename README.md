# Quantum Chess

A Python/PyQt5 chess variant with **up to 10 active qubits**, simulated locally
using Qiskit. All 32 chess pieces remain on the board; qubits are allocated only
when a piece enters a two-position superposition.

## Run

Use Python **3.11 or newer**. Tested with Python 3.11, Qiskit 2.6.2 and PyQt5 5.15.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

The default budget is 10 qubits. To use a smaller budget or the terminal interface:

```bash
python main.py --qubits 5
python main.py --cli --qubits 10
```

`--seed 42` provides reproducible measurement sequences for debugging. Normal play
uses random outcomes. No IBM account, API key, Aer installation, or GPU is required.

## Play

Select a mode, click a piece belonging to the current player, then click a green
highlighted square. The turn indicator includes the number of active qubits.

- **Classical move:** ordinary piece movement or capture. Uses no qubits.
- **Split: stay or move:** allocates a qubit and applies a Hadamard gate. The
  piece occupies its original square on outcome **0**, or the selected destination
  on outcome **1**, each with probability 1/2. Both branches are displayed.
- **Entangled split:** first choose one of your already split pieces in the
  control dropdown. Moving a different, unsplit piece allocates a fresh qubit
  and applies CNOT from the control, producing correlated position choices.
  Both pieces resolve to matching branch numbers. This can be extended to a chain.
- **Measure board:** samples all active branches **together**, places each piece
  at its sampled position, and releases all qubits. Measurement uses a turn.
  Measuring an already resolved board does nothing and does not consume a turn.

For example:

1. White splits the pawn on e2 toward e4.
2. Black makes a classical move from a7 to a6.
3. White selects **Entangled split**, chooses `w_pawn5` as control, then splits
   the pawn on d2 toward d4.
4. Black measures the board. The two white pawns resolve to **e2 and d2**, or
   **e4 and d4**, together.

At capacity, classical moves and measurement remain available. An eleventh split
is rejected without changing the board, circuit, or turn. After measurement,
the slots can be used by any pieces, including those that previously split.

## Rules of this prototype

This is a deliberately constrained quantum chess variant:

- Both squares of a split piece are reserved and block movement until measurement.
  A split piece cannot move again or be captured before measurement.
- Split moves require an empty destination. Kings cannot split; quantum captures
  and quantum pawn promotion are not supported.
- Classical pawn promotion automatically produces a queen. Castling, en passant,
  underpromotion, automatic checkmate/stalemate detection, and draw rules are not
  implemented.
- A move must keep its own king safe in every possible quantum outcome. A player
  in check must escape with a classical move before splitting or spending a turn
  on measurement. The app rejects king captures.

These reservation rules can reject moves that would be possible under a more
permissive quantum chess ruleset. They ensure that every measured board has one
piece per square. Ten qubits encode up to ten binary position choices, not the
arbitrary positions of all pieces on the chessboard.

## How Qiskit is used

`quantum_logic.py` maintains a quantum preparation circuit with a validated width
of 1–10 qubits. It applies actual Qiskit H and CX gates and preserves the circuit
between moves. It uses `Statevector` to inspect joint probabilities for king-safety
validation and the [V2 StatevectorSampler](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler)
to sample the joint measurement. Results drive board positions, rather than only
being printed to the console.

After joint measurement, the resolved positions live in the classical board and
the circuit resets to zero. This prevents old branches from being sampled again.
The quantum model is an ideal local simulation; hardware execution and noise
models are outside the current implementation.

## Verify

```bash
python -m unittest discover -s tests -v
```

Tests cover H–H interference, Bell-state entanglement, a fully entangled 10-qubit
GHZ state, measurement bit order, coherent branch preservation, seeded sampling,
qubit reuse, the capacity limit, board resolution, captures, king safety, and
PyQt button interactions. GUI tests use Qt's offscreen platform.

## Project structure

- `main.py`: desktop/terminal entry point, qubit budget and seed options.
- `game.py`: turns, position branches, reservations, captures and king safety.
- `pieces.py`: piece movement geometry.
- `quantum_logic.py`: Qiskit circuit preparation, allocation and measurement.
- `gui.py`: board, move modes, entanglement control and measurement button.
- `utils.py`: validated square coordinate conversions.
- `tests/`: quantum, game and GUI regression tests.

## Qiskit skills for Codex

The Qiskit AI skills plugin is installed in the current user's Codex environment.
For another development environment:

```bash
codex plugin marketplace add Qiskit/skills
codex plugin add qiskit-ai-skills@qiskit
```

This developer plugin is separate from the Python Qiskit dependency installed
through `requirements.txt`.
