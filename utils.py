def position_to_grid(position):
    """Convert validated algebraic notation to a board index."""
    if (not isinstance(position, str) or len(position) != 2
            or position[0] not in "abcdefgh" or position[1] not in "12345678"):
        raise ValueError("Use a square from a1 to h8.")
    return 8 - int(position[1]), ord(position[0]) - ord("a")


def grid_to_position(row, col):
    if not (0 <= row < 8 and 0 <= col < 8):
        raise ValueError("Square is outside the board.")
    return f"{chr(col + ord('a'))}{8 - row}"
