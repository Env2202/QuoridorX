from helpers.path_helper import bfs_pathfinder
from helpers.valid_moves_helper import get_valid_moves_helper
from helpers.wall_helpers import get_blocked_roads

def minimax(game_state, depth, alpha, beta, maximizing_player_color, current_player_color, nodes_examined, difficulty, move_sequence=None):
    # Increment the node counter
    nodes_examined['count'] += 1
    if move_sequence is None:
        move_sequence = []  # Initialize move sequence

    opponent_color = game_state.get_opponent_color(current_player_color)

    # Terminal condition: if max depth is reached or the game is over
    if depth == 0 or game_over(game_state):
        return evaluate(game_state, maximizing_player_color,depth), move_sequence

    current_player = game_state.get_player_by_color(current_player_color)
    opponent_player = game_state.get_player_by_color(opponent_color)

    ordered_moves = get_by_difficulty(game_state, current_player, opponent_player, depth, difficulty)

    #INVALID LINE
    if not ordered_moves:
        return float('-inf'), move_sequence

    if current_player_color == maximizing_player_color:
        max_eval = float('-inf')
        best_sequence = None

        for type, move in ordered_moves:
            new_game_state = game_state.simulate_move_or_wall(type, move, current_player)

            eval_score, child_sequence = minimax(
                new_game_state,
                depth - 1,
                alpha,
                beta,
                maximizing_player_color,
                opponent_color,
                nodes_examined,
                difficulty=difficulty,
                move_sequence= move_sequence + [(type, move)]
            )

            if eval_score > max_eval:
                max_eval = eval_score
                best_sequence = child_sequence

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cut-off

        return max_eval, best_sequence

    else:
        min_eval = float('inf')
        best_sequence = None

        for type, move in ordered_moves:
            new_game_state = game_state.simulate_move_or_wall(type, move, current_player)

            eval_score, child_sequence = minimax(
                new_game_state,
                depth - 1,
                alpha,
                beta,
                maximizing_player_color,
                opponent_color,
                nodes_examined,
                difficulty=difficulty,
                move_sequence=move_sequence + [(type, move)]
            )

            if eval_score < min_eval:
                min_eval = eval_score
                best_sequence = child_sequence

            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cut-off

        return min_eval, best_sequence

def game_over(game_state):
    red_player = game_state.red_player
    blue_player = game_state.blue_player
    return (red_player.col == red_player.goal_col) or (blue_player.col == blue_player.goal_col)

# === Heuristic Function ===

def evaluate(game_state, maximizing_player_color,depth=0):
    maximizing_player = game_state.get_player_by_color(maximizing_player_color)
    minimizing_player = game_state.get_player_by_color(game_state.get_opponent_color(maximizing_player_color))

    # Use BFS to find the shortest path
    max_distance_path = bfs_pathfinder(start=(maximizing_player.row, maximizing_player.col),
                                       goal_col=maximizing_player.goal_col,
                                       grid_size=game_state.grid_size,
                                       blocked_roads=game_state.current_blocked_roads)
    min_distance_path = bfs_pathfinder(start=(minimizing_player.row, minimizing_player.col),
                                       goal_col=minimizing_player.goal_col,
                                       grid_size=game_state.grid_size,
                                       blocked_roads=game_state.current_blocked_roads)

    # INVALID LINE:
    if max_distance_path is None or min_distance_path is None:
        return float('-inf')

    max_distance = len(max_distance_path)
    min_distance = len(min_distance_path)

    # Check for terminal states
    if maximizing_player.col == maximizing_player.goal_col:
        return float('inf')  # Maximizing player wins

    # Heuristic value is the difference in path lengths
    advantage_on_wall = (maximizing_player.available_walls-minimizing_player.available_walls)*1
    proximity_weight = 0.3 * 1/(max_distance)
    # proximity_weight = 0

    if minimizing_player.col == minimizing_player.goal_col:
        # The opponent has won, but the bot should still strive to minimize its distance to the goal
        # Or surviving as long as possible
        # Return a negative value proportional to the bot's distance, with an added penalty
        penalty = 1000  # A large penalty to prioritize winning states over losing
        depth_penalty = 50 * depth
        return min_distance - max_distance + advantage_on_wall + proximity_weight - penalty - depth_penalty


    evaluation = min_distance - max_distance + advantage_on_wall + proximity_weight
    return evaluation

def get_intelligent_moves(game_state, player, grid_size, blocked_roads,available_walls):
    """Return intelligent moves and other moves for the bot."""
    opponent_color = game_state.get_opponent_color(player.color)
    opponent_player = game_state.get_player_by_color(opponent_color)

    # Dictionary to store intelligent moves and other moves
    intelligent_moves = []
    other_moves = []

    # PLAYER MOVES
    valid_moves = get_valid_moves_helper(player, opponent_player, grid_size, blocked_roads)
    if not valid_moves and available_walls<=0:
        intelligent_moves.append(('skip', (player.row, player.col)))
        return intelligent_moves, other_moves

    shortest_path = bfs_pathfinder(
        start=(player.row, player.col),
        goal_col=player.goal_col,
        grid_size=grid_size,
        blocked_roads=blocked_roads
    )

    opponent_shortest_path = bfs_pathfinder(
        start=(opponent_player.row, opponent_player.col),
        goal_col=opponent_player.goal_col,
        grid_size=grid_size,
        blocked_roads=blocked_roads
    )

    # If no path exists for the maximizing player, assign a high penalty
    if opponent_shortest_path is None:
        return None, None
    if shortest_path is None:
        return None, None

    for direction, move in valid_moves.items():
        if move in shortest_path:
            intelligent_moves.append((direction,move))
        else:
            other_moves.append((direction,move))
    if available_walls<=0:
        return intelligent_moves, other_moves

    #WALL MOVES

    for wall in game_state.valid_walls:
        # Check if the wall blocks the opponent's shortest path
        blocks_path = False

        # Extract the blocked roads for the current wall placement
        for blocked_road in get_blocked_roads(wall):
            # Convert blocked_road to a tuple if it's not already
            road_segment = tuple(blocked_road)

            # Now we need to check if the road_segment is part of any consecutive segment
            # on the opponent's shortest path.
            for i in range(len(opponent_shortest_path) - 1):
                path_segment = (opponent_shortest_path[i], opponent_shortest_path[i + 1])

                # Check if the current blocked road matches this path segment (in either order)
                if road_segment == path_segment or road_segment == path_segment[::-1]:
                    blocks_path = True
                    break

        if blocks_path:
            # Add to intelligent wall moves
            intelligent_moves.append(('wall', wall))
        else:
            # Wall is not an intelligent move, add to other moves
            other_moves.append(('wall', wall))

    return intelligent_moves, other_moves

def get_by_difficulty(game_state, player, opponent_player, depth, difficulty):
    ordered_moves = None
    if difficulty == 'impossible':
        # BOT: Considers wall placements
        if depth == 6:
            intelligent_moves, other_moves = get_intelligent_moves(game_state, player, game_state.grid_size,
                                                                   game_state.current_blocked_roads,
                                                                   player.available_walls)
            # INVALID LINE:
            if not intelligent_moves and not other_moves:
                return None

            ordered_moves = intelligent_moves + other_moves
        elif depth == 5:
            intelligent_moves, other_moves = get_intelligent_moves(game_state, player, game_state.grid_size,
                                                                   game_state.current_blocked_roads,
                                                                   player.available_walls)
            # INVALID LINE:
            if not intelligent_moves and not other_moves:
                return None
            ordered_moves = intelligent_moves[:10] + other_moves[:2]
        else:
            # BOT: Doesn't consider wall placements
            valid_moves = get_valid_moves_helper(player, opponent_player,
                                                 game_state.grid_size, game_state.current_blocked_roads)
            ordered_moves = valid_moves.items()

    elif difficulty == 'hard':
        # BOT: Considers wall placements
        if depth == 6:
            intelligent_moves, other_moves = get_intelligent_moves(game_state, player, game_state.grid_size,
                                                                   game_state.current_blocked_roads,
                                                                   player.available_walls)

            # INVALID LINE:
            if not intelligent_moves and not other_moves:
                return None
            ordered_moves = intelligent_moves

        else:
            # BOT: Doesn't consider wall placements
            valid_moves = get_valid_moves_helper(player, opponent_player,
                                                 game_state.grid_size, game_state.current_blocked_roads)
            ordered_moves = valid_moves.items()

    elif difficulty == 'medium':
        # BOT: Doesn't consider wall placements
        valid_moves = get_valid_moves_helper(player, opponent_player,
                                             game_state.grid_size, game_state.current_blocked_roads)
        ordered_moves = valid_moves.items()

    elif difficulty == 'easy':
        # BOT: Doesn't consider wall placements
        valid_moves = get_valid_moves_helper(player, opponent_player,
                                             game_state.grid_size, game_state.current_blocked_roads)
        ordered_moves = valid_moves.items()

    else:
        return None

    return ordered_moves