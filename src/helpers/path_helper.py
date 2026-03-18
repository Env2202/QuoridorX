from collections import deque

# Global cache dictionary
cache = {}

def bfs_pathfinder(start, goal_col, grid_size, blocked_roads):
    """
    Perform a BFS to find the shortest path to the goal column.
    This version includes a cache mechanism to avoid recalculating previously analyzed paths.
    """

    # Convert blocked_roads to a tuple of tuples to make it hashable
    blocked_roads_tuple = tuple(tuple(sorted(road)) for road in blocked_roads)

    # Create a cache key that uniquely identifies the scenario
    cache_key = (start, goal_col, blocked_roads_tuple)

    # Check if the path has already been analyzed and is in the cache
    if cache_key in cache:
        return cache[cache_key]['path']

    # Initialize BFS with starting position
    queue = deque([(start, [])])
    visited = {start}

    # Preprocess blocked roads for faster lookup
    blocked_set = set()
    for road in blocked_roads:
        blocked_set.add(frozenset(road))

    # Direction vectors for up, down, left, right
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # (row_change, col_change)

    while queue:
        (current_row, current_col), path = queue.popleft()

        # Check if we've reached the goal column
        if current_col == goal_col:
            # Save the result in the cache
            cached_path = path + [(current_row, current_col)]
            cache[cache_key] = {'exists': True, 'path': cached_path}
            return cached_path  # Return the shortest path

        # Explore neighbors
        for drow, dcol in directions:
            new_row, new_col = current_row + drow, current_col + dcol
            new_position = (new_row, new_col)

            # Check if the new position is within the grid bounds
            if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
                # Check if the path between current and new positions is not blocked
                edge = frozenset([(current_row, current_col), new_position])
                if edge not in blocked_set:
                    if new_position not in visited:
                        visited.add(new_position)
                        queue.append((new_position, path + [(current_row, current_col)]))

    # If no path found, save the result in cache
    cache[cache_key] = {'exists': False, 'path': None}
    return None  # No path found

def dfs_path_exists(start, goal_col, grid_size, blocked_roads):
    """
    Perform a DFS to check if a path exists to the goal column.
    This version includes a cache mechanism to avoid recalculating previously analyzed paths.
    """

    # Convert blocked_roads to a tuple of tuples to make it hashable
    blocked_roads_tuple = tuple(tuple(sorted(road)) for road in blocked_roads)

    # Create a cache key that uniquely identifies the scenario
    cache_key = ('dfs', start, goal_col, blocked_roads_tuple)

    # Check if the path has already been analyzed and is in the cache
    if cache_key in cache:
        return cache[cache_key]

    # Initialize DFS with starting position
    stack = [start]
    visited = {start}

    # Preprocess blocked roads for faster lookup
    blocked_set = set()
    for road in blocked_roads:
        # Road is a tuple of two positions
        blocked_set.add(frozenset(road))

    # Direction vectors for up, down, left, right
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # (row_change, col_change)

    while stack:
        current_row, current_col = stack.pop()

        # Check if we've reached the goal column
        if current_col == goal_col:
            # Save the result in cache
            cache[cache_key] = True
            return True

        # Explore neighbors
        for drow, dcol in directions:
            new_row, new_col = current_row + drow, current_col + dcol
            new_position = (new_row, new_col)

            # Check if the new position is within the grid bounds
            if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
                # Check if the path between current and new positions is not blocked
                edge = frozenset([(current_row, current_col), new_position])
                if edge not in blocked_set and new_position not in visited:
                    visited.add(new_position)
                    stack.append(new_position)

    # Save the result in cache
    cache[cache_key] = False
    return False  # No path found

def bfs_pathfinder_cell_to_cell(start, goal, grid_size, blocked_roads, find_shortest_path=False):
    """
    Performs BFS to find a path from start to goal on a grid of given size,
    considering blocked roads (walls).
    """

    # Define movement directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (delta_row, delta_col)

    # Initialize visited set and queue for BFS
    visited = set()
    queue = deque()

    # Enqueue the starting position
    queue.append((start, [start]))  # Each element is a tuple: (current_position, path_so_far)
    visited.add(start)

    # Convert blocked_roads to a set of frozensets for faster lookup
    blocked_roads_set = set(frozenset(road) for road in blocked_roads)

    while queue:
        current_pos, path = queue.popleft()

        # Check if we've reached the goal
        if current_pos == goal:
            if find_shortest_path:
                return path  # Return the path from start to goal
            else:
                return True  # Path exists

        current_row, current_col = current_pos

        # Explore neighboring cells
        for delta_row, delta_col in directions:
            neighbor_row = current_row + delta_row
            neighbor_col = current_col + delta_col
            neighbor_pos = (neighbor_row, neighbor_col)

            # Check if neighbor is within grid bounds
            if 0 <= neighbor_row < grid_size and 0 <= neighbor_col < grid_size:
                # Check if the move between current_pos and neighbor_pos is not blocked
                road = frozenset({current_pos, neighbor_pos})
                if road not in blocked_roads_set and neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    queue.append((neighbor_pos, path + [neighbor_pos] if find_shortest_path else None))

    # If we exhaust the queue without reaching the goal
    if find_shortest_path:
        return []  # No path exists
    else:
        return False  # No path exists

def is_path_blocked(pos1, pos2, blocked_roads):
    """
    Check if the path between two positions is blocked by a wall.
    """
    return [pos1, pos2] in blocked_roads or [pos2, pos1] in blocked_roads

def clear_cache():
    """
    Clear the cache of stored paths, keeping the first 1000 entries.
    """
    global cache

    if len(cache) > 1000:
        # Create a new cache dictionary with the first 1000 items
        cache = dict(list(cache.items())[:1000])
