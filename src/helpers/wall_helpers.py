from helpers.path_helper import bfs_pathfinder, bfs_pathfinder_cell_to_cell, dfs_path_exists


def get_blocked_roads(wall):
    # Extract start and end points from the wall
    wall_start, wall_end = wall[0], wall[1]

    # Add blocked roads based on wall orientation
    if wall_start[1] == wall_end[1]:  # Vertical wall
        eventual_blocks = [[(wall_start[0], wall_start[1] - 1), (wall_start[0], wall_start[1])],
                           [(wall_end[0] - 1, wall_end[1] - 1), (wall_end[0] - 1, wall_end[1])]]

    elif wall_start[0] == wall_end[0]:  # Horizontal wall
        eventual_blocks = [
            [(wall_start[0] - 1, wall_start[1]), (wall_start[0], wall_start[1])],
            [(wall_end[0] - 1, wall_end[1] - 1), (wall_end[0], wall_end[1] - 1)]
        ]
    else:
        print("How did you get here?")
        return None

    return eventual_blocks

def order_walls(wall):
    # Extract start and end points from the wall
    wall_start, wall_end = wall[0], wall[1]

    ordered_wall=[(wall_start[0], wall_start[1]), (wall_end[0], wall_end[1])]
    #Order the wall coordinates from left to right and top to bottom
    if wall_start[0] > wall_end[0] or wall_start[1] > wall_end[1]:
        ordered_wall=[(wall_end[0], wall_end[1]), (wall_start[0], wall_start[1])]
    return ordered_wall

def is_wall_within_bounds(wall, grid_size):
    (row1, col1), (row2, col2) = wall
    return 0 <= row1 <= grid_size and 0 <= col1 <= grid_size and \
        0 <= row2 <= grid_size and 0 <= col2 <= grid_size

def walls_intersect(start1, end1, start2, end2):
    """Check if two walls intersect each other."""
    # Middle Intersection
    middle1 = ((start1[0] + end1[0]) / 2, (start1[1] + end1[1]) / 2)
    middle2 = ((start2[0] + end2[0]) / 2, (start2[1] + end2[1]) / 2)

    if middle1 == middle2:
        return True

    if start1 == middle2 and (middle1 == start2 or middle1 == end2):
        return True

    if end1 == middle2 and (middle1 == start2 or middle1 == end2):
        return True

    return False

def is_valid_wall(start, end, grid_size, placed_walls,forbidden_walls):
    """Check if the wall placement is within bounds and doesn't overlap or intersect with another wall's middle."""
    # Check if the wall is within grid bounds
    if not is_wall_within_bounds((start, end), grid_size):
        return False

    # Check if the wall is placed on the border of the grid
    if start[0] == 0 and end[0] == 0:
        return False
    if start[0] == grid_size and end[0] == grid_size:
        return False
    if start[1] == 0 and end[1] == 0:
        return False
    if start[1] == grid_size and end[1] == grid_size:
        return False

    # Check if a wall already exists in this position
    if [(start, end)] in placed_walls or [(end, start)] in placed_walls:
        return False

    # Check if the proposed wall crosses the middle of any existing walls
    for wall_start, wall_end in placed_walls:
        if walls_intersect(start, end, wall_start, wall_end):
            return False

    # Check if the proposed wall is a forbidden wall
    if [start, end] in forbidden_walls or [end, start] in forbidden_walls:
        return False

    return True

# Define a global cache to store results
find_forbidden_walls_cache = {}

# Helper function to convert list of blocked roads and placed walls into a hashable format
def hashable_walls(walls):
    return tuple(frozenset(wall) for wall in walls)

def hashable_blocked_roads(blocked_roads):
    return tuple(frozenset(road) for road in blocked_roads)

def find_forbidden_walls_new(grid_size, placed_walls, current_blocked_roads, red_player_pos, blue_player_pos, red_goal_col, blue_goal_col):
    """
    Find the walls that cannot be placed because they would block either player from reaching their goal.
    This version reduces the number of BFS calls by reusing shortest paths and only analyzes walls
    that share a common point with two walls, or one wall and one grid border.
    """
    global count
    # Convert placed_walls and current_blocked_roads to hashable structures to create a cache key
    placed_walls_hashable = hashable_walls(placed_walls)
    current_blocked_roads_hashable = hashable_blocked_roads(current_blocked_roads)

    # Create a tuple that represents the cache key
    cache_key = (grid_size, placed_walls_hashable, current_blocked_roads_hashable, red_player_pos, blue_player_pos, red_goal_col, blue_goal_col)

    # Check if the result is already in the cache
    if cache_key in find_forbidden_walls_cache:
        return find_forbidden_walls_cache[cache_key]

    # If not in the cache, compute the result
    forbidden_walls = []

    # Perform BFS for both players to find the initial shortest path without hypothetical walls
    blue_shortest_path = bfs_pathfinder(blue_player_pos, blue_goal_col, grid_size, current_blocked_roads)
    red_shortest_path = bfs_pathfinder(red_player_pos, red_goal_col, grid_size, current_blocked_roads)

    # Helper function to check if the hypothetical wall shares a common point with two other walls or one wall and a grid border
    def shares_common_point_with_two(hypothetical_wall, placed_walls, grid_size):
        wall_start, wall_end = hypothetical_wall

        # Calculate the middle point of the hypothetical wall
        middle_point = ((wall_start[0] + wall_end[0]) / 2, (wall_start[1] + wall_end[1]) / 2)

        shared_point_count = 0

        # Helper function to check if a point is on the grid border
        def is_border(point):
            return point[0] == 0 or point[0] == grid_size or point[1] == 0 or point[1] == grid_size

        # Check against all placed walls for shared points
        for placed_wall in placed_walls:
            placed_start, placed_end = placed_wall
            placed_middle = ((placed_start[0] + placed_end[0]) / 2, (placed_start[1] + placed_end[1]) / 2)

            # Check if any of the start, middle, or end points match with placed walls
            if (wall_start == placed_start or wall_start == placed_end or wall_start == placed_middle or
                wall_end == placed_start or wall_end == placed_end or wall_end == placed_middle or
                middle_point == placed_start or middle_point == placed_end or middle_point == placed_middle):
                shared_point_count += 1

            # If we have already found two shared points, we can return early
            if shared_point_count == 2:
                return True

        # Check if the wall touches a grid border
        if is_border(wall_start) or is_border(wall_end) or is_border(middle_point):
            shared_point_count += 1

        return shared_point_count == 2

    # Helper function to check if the hypothetical wall intersects the player's current shortest path
    def wall_blocks_path(hypothetical_wall, player_shortest_path):

        try:
            # Get the roads blocked by the hypothetical wall
            blocked_roads = get_blocked_roads(hypothetical_wall)

            # Check if any of the blocked roads intersect with the player's shortest path
            for blocked_road in blocked_roads:
                road_segment = tuple(blocked_road)

                # Iterate over the segments of the player's path
                for i in range(len(player_shortest_path) - 1):
                    path_segment = (player_shortest_path[i], player_shortest_path[i + 1])

                    # Check if the road segment matches the path segment in either direction
                    if road_segment == path_segment or road_segment == path_segment[::-1]:
                        return True

        except Exception as e:
            # Catch and print the exception message
            # print(f"An error occurred: {str(e)}")
            # print("Current blocked roads:", current_blocked_roads)
            # print("WALL THAT CRASHED:", hypothetical_wall)
            return False

        # If no intersections are found, return False
        return False

    # Loop through the grid to simulate placement of both horizontal and vertical walls
    for row in range(grid_size):
        for col in range(grid_size):
            for wall_type in ["horizontal", "vertical"]:
                if wall_type == "horizontal":
                    hypothetical_wall = order_walls([(row, col), (row, col + 2)])
                else:
                    hypothetical_wall = order_walls([(row, col), (row + 2, col)])

                # Check if the wall shares a common point with two walls or one wall and a grid border
                if (hypothetical_wall not in placed_walls
                        and is_wall_within_bounds(hypothetical_wall, grid_size)
                        and shares_common_point_with_two(hypothetical_wall, placed_walls, grid_size)):
                    # First, check if the wall intersects the blue or red player's shortest path
                    blue_path_blocked = wall_blocks_path(hypothetical_wall, blue_shortest_path)
                    red_path_blocked = wall_blocks_path(hypothetical_wall, red_shortest_path)

                    # If the wall intersects the shortest path, check if it completely blocks the player
                    if blue_path_blocked:
                        # Rerun BFS for the blue player with the hypothetical wall added
                        blocked_roads = get_blocked_roads(hypothetical_wall)
                        current_plus_hypothetical = current_blocked_roads + blocked_roads
                        can_circumvent_wall=True

                        #Check if we can circumvent the wall
                        for blocked_road in blocked_roads:
                            start=blocked_road[0]
                            end=blocked_road[1]
                            if not bfs_pathfinder_cell_to_cell(start,end,grid_size,current_plus_hypothetical):
                                can_circumvent_wall=False
                                break

                        #Let's check if another path
                        if not can_circumvent_wall:
                            if not dfs_path_exists(blue_player_pos, blue_goal_col, grid_size, current_plus_hypothetical):
                                forbidden_walls.append(hypothetical_wall)
                                continue  # Skip further checks if already blocked

                    if red_path_blocked:
                        # Rerun BFS for the red player with the hypothetical wall added
                        blocked_roads = get_blocked_roads(hypothetical_wall)
                        current_plus_hypothetical = current_blocked_roads + blocked_roads
                        can_circumvent_wall = True

                        # Check if we can circumvent the wall
                        for blocked_road in blocked_roads:
                            start = blocked_road[0]
                            end = blocked_road[1]
                            if not bfs_pathfinder_cell_to_cell(start, end, grid_size, current_plus_hypothetical):
                                can_circumvent_wall = False
                                break

                        # Let's check if another path exists
                        if not can_circumvent_wall:
                            if not dfs_path_exists(red_player_pos, red_goal_col, grid_size, current_plus_hypothetical):
                                forbidden_walls.append(hypothetical_wall)

    # Store the result in the cache before returning
    find_forbidden_walls_cache[cache_key] = forbidden_walls
    return forbidden_walls

def find_valid_walls(grid_size, placed_walls, forbidden_walls):
    """
    Find the valid walls that can be placed on the grid.
    """
    valid_walls = []

    # Loop through the grid and check for possible wall placements
    for row in range(grid_size):
        for col in range(grid_size):
            # Check for horizontal walls
            horizontal_wall = order_walls([(row, col), (row, col + 2)])
            if is_valid_wall(horizontal_wall[0], horizontal_wall[1], grid_size, placed_walls,forbidden_walls):
                valid_walls.append(horizontal_wall)

            # Check for vertical walls
            vertical_wall = order_walls([(row, col), (row + 2, col)])
            if is_valid_wall(vertical_wall[0], vertical_wall[1], grid_size, placed_walls,forbidden_walls):
                valid_walls.append(vertical_wall)

    return valid_walls
