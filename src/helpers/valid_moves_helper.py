def get_valid_moves_helper(player, other_player, grid_size, current_blocked_roads):
    """
    Return a dictionary of valid moves based on player row and column.
    Args:
        player: The player object whose valid moves we are calculating.
        other_player: The opposing player object (used to check if they are near).
        grid_size: Size of the grid (an integer representing the width and height).
        current_blocked_roads: List of blocked roads represented as tuples [(pos1, pos2), (pos2, pos1)].

    Returns:
        Dictionary format: {'up': (row, col), 'down': (row, col), 'left': (row, col), 'right': (row, col)}
    """

    # Base directions for normal movement (1 cell in each direction)
    directions = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0)
    }

    # Check if the other player is near
    other_player_position = where_is_other_player(player, other_player)

    # If the other player is near, modify the specific direction to allow 2 cells away
    if other_player_position:
        if other_player_position == 'up':
            directions['up'] = (0, -2)  # Allow move two cells up
        elif other_player_position == 'down':
            directions['down'] = (0, 2)  # Allow move two cells down
        elif other_player_position == 'left':
            directions['left'] = (-2, 0)  # Allow move two cells left
        elif other_player_position == 'right':
            directions['right'] = (2, 0)  # Allow move two cells right
        directions = is_there_a_wall(player, other_player_position, directions, current_blocked_roads)

    valid_moves = {}

    # Calculate the valid moves based on current grid position
    for direction, (dcol, drow) in directions.items():
        new_row = player.row + drow
        new_col = player.col + dcol

        # Check if the move is within the grid bounds
        if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
            # Check if the move is not blocked by a wall
            if [(player.row, player.col), (new_row, new_col)] not in current_blocked_roads and \
                    [(new_row, new_col), (player.row, player.col)] not in current_blocked_roads:
                valid_moves[direction] = (new_row, new_col)

    # If no valid moves are found, return None
    return valid_moves


def where_is_other_player(player, other_player):
    """
    Determine the relative position of the other player (up, down, left, or right) if they are near.
    """

    if abs(player.row - other_player.row) + abs(player.col - other_player.col) == 1:
        if player.row == other_player.row:
            return "left" if player.col > other_player.col else "right"
        if player.col == other_player.col:
            return "up" if player.row > other_player.row else "down"

    return None


def is_there_a_wall(player, other_player_position, directions, current_blocked_roads):
    """
    Adjust directions if a wall is blocking the path of the player.
    """

    position_change = {
        'up': (-1, 0),
        'down': (1, 0),
        'left': (0, -1),
        'right': (0, 1)
    }

    if other_player_position in position_change:
        row_change, col_change = position_change[other_player_position]

        blocked_roads = [
            [(player.row, player.col), (player.row + row_change, player.col + col_change)],
            [(player.row + row_change, player.col + col_change), (player.row, player.col)],
            [(player.row + row_change, player.col + col_change),
             (player.row + 2 * row_change, player.col + 2 * col_change)],
            [(player.row + 2 * row_change, player.col + 2 * col_change),
             (player.row + row_change, player.col + col_change)]
        ]

        if any(road in current_blocked_roads for road in blocked_roads):
            directions.pop(other_player_position)

    return directions
