def position_to_grid(position):
    """Convert a chess position (e.g., 'e2') to grid coordinates (row, col)."""
    col = ord(position[0]) - ord('a')
    row = 8 - int(position[1])
    return row, col

def grid_to_position(row, col):
    """Convert grid coordinates (row, col) to a chess position (e.g., 'e2')."""
    return f"{chr(col + ord('a'))}{8 - row}"
