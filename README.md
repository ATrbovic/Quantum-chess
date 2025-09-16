# Quantum Chess

Quantum Chess is a Python-based chess engine and GUI that integrates quantum mechanics principles into traditional chess. The game allows players to perform quantum moves such as superposition and entanglement, making for a unique and educational chess experience.

## Features
- Classical chess gameplay with all standard rules
- Quantum moves: superposition, entanglement, and measurement
- PyQt5-based graphical user interface
- Asynchronous quantum simulation using Qiskit
- Move validation and basic game loop

## Requirements
- Python 3.9+
- PyQt5
- Qiskit
- (Optional) Other dependencies listed in your environment

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/ATrbovic/Quantum-chess.git
   cd Quantum-chess
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install PyQt5 qiskit
   ```
4. Run the main program:
   ```bash
   python main.py
   ```

## Project Structure
- `main.py` - Main entry point
- `game.py` - Game logic and quantum operations
- `gui.py` - Graphical user interface
- `pieces.py` - Chess piece definitions
- `quantum_logic.py` - Quantum circuit logic
- `utils.py` - Utility functions
- `test_*.py` - Test scripts

## License
MIT License
