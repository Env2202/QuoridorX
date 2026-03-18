from PyQt6.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsTextItem, QLabel, \
    QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QColor, QFont
from helpers.grid_helpers import grid_to_scene, scene_to_grid
from helpers.wall_helpers import order_walls, get_blocked_roads, is_valid_wall

class GridScene(QGraphicsScene):
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.grid_size = game.grid_size
        self.cell_size = game.cell_size
        self.turn_manager = game.turn_manager

        # Set up pens and colors
        self.pen_wall = QPen(Qt.GlobalColor.white, 1)
        self.pen_grid_lines = QPen(QColor(0, 0, 0, 80), 1)
        self.grid_color = QColor(60, 60, 60, 255)

        # Draw the grid
        self.draw_grid()

        self.mouse_events_enabled = True
        self.keyPressed=False

        # Initialize players
        self.red_player = None
        self.blue_player = None

        # Wall preview and positions
        self.wall_preview = None
        self.start_pos = None
        self.start_row = None
        self.start_col = None
        self.end_row = None
        self.end_col = None
        self.possible_wall_destinations = None
        self.forbidden_walls = []
        self.placed_walls = []
        self.current_blocked_roads = []

        # Create and set up rules container overlay
        self.rules_container = self.create_rules_overlay()
        proxy_widget = self.addWidget(self.rules_container)
        self.center_rules_container()
        proxy_widget.setZValue(10)  # Ensure the rules are on top of everything
        self.rules_container.hide()

    def draw_grid(self):
        """Draw the grid."""
        # Set the scene size based on grid size and cell size
        self.setSceneRect(0, 0, self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        # Draw background (only of the grid)
        background= self.addRect(0, 0, self.grid_size * self.cell_size, self.grid_size * self.cell_size, QPen(Qt.GlobalColor.black), self.grid_color)
        background.setZValue(-5)
        # Draw grid lines
        for i in range(self.grid_size + 1):
            self.addLine(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, self.pen_grid_lines)  # Vertical
            self.addLine(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, self.pen_grid_lines)  # Horizontal

    # === Movement Management ===

    def get_valid_moves(self, player):
        self.game_state=self.turn_manager.game_state
        if self.game_state:
            valid_moves=self.game_state.get_valid_moves(player)
            return valid_moves

    # === Movement Graphics ===

    def highlight_possible_moves(self, player):
        """Draw all valid moves based on player position."""
        valid_moves = player.valid_moves
        ellipse_size = 10
        offset = (self.cell_size // 2) - ellipse_size // 2

        # Set pen and brush based on player color
        if player.color == "red":
            ellipse_pen = QPen(Qt.GlobalColor.red)
            ellipse_brush = Qt.GlobalColor.red
        else:
            ellipse_pen = QPen(Qt.GlobalColor.blue)
            ellipse_brush = Qt.GlobalColor.blue

        # Draw ellipses for each valid move
        for row, col in valid_moves.values():
            scene_pos = grid_to_scene(row, col, self.cell_size)  # Use helper function to convert grid to scene
            ellipse = self.addEllipse(scene_pos.x() + offset, scene_pos.y() + offset, ellipse_size, ellipse_size, ellipse_pen)
            ellipse.setBrush(ellipse_brush)
            ellipse.setZValue(-1)  # Ensure ellipses are below the player

    def clear_possible_moves(self):
        """Remove all ellipses representing possible moves."""
        ellipses_to_remove = [item for item in self.items() if isinstance(item, QGraphicsEllipseItem)]
        for ellipse in ellipses_to_remove:
            self.removeItem(ellipse)

    # === Mouse Events ===

    def disable_mouse_events(self):
        """Disable mouse event handling."""
        self.mouse_events_enabled = False

    def enable_mouse_events(self):
        """Enable mouse event handling."""
        self.mouse_events_enabled = True

    def keyPressEvent(self, event):
        if not self.mouse_events_enabled:
            return
        # Get the current player
        current_player = self.game.turn_manager.get_current_player()
        # Skip key events if the current player is a bot
        if hasattr(current_player, 'is_bot') and current_player.is_bot:
            print("Bot's turn, skipping key event")
            return
        if self.keyPressed:
            return

        # Get valid moves for the current player
        valid_moves = current_player.valid_moves  # {'up': (3, 1), 'down': (5, 1), 'left': (4, 0), 'right': (4, 2)}

        # Define key-to-direction mapping
        key_direction_map = {
            Qt.Key.Key_Up: 'up',
            Qt.Key.Key_Down: 'down',
            Qt.Key.Key_Left: 'left',
            Qt.Key.Key_Right: 'right'
        }

        # Check if the key pressed corresponds to a direction
        direction = key_direction_map.get(event.key(), None)
        if direction and direction in valid_moves:
            # Get the new row and column from valid_moves
            new_row, new_col = valid_moves[direction]
            self.keyPressed = True
            self.removeItem(self.wall_preview)
            # Call the move_player method to move the player
            current_player.move_player(new_row, new_col)

    def mousePressEvent(self, event):
        """Handle right-click mouse events for starting a wall preview."""
        if not self.mouse_events_enabled:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.start_wall_preview(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events during wall preview."""
        if not self.mouse_events_enabled:
            return
        if event.buttons() == Qt.MouseButton.RightButton and self.wall_preview:
            closest_pos = None
            min_distance = float('inf')

            # Get possible positions to check
            to_check = self.possible_wall_destinations + [(self.start_row, self.start_col)]

            for pos in filter(None, to_check):  # Skip None values
                pos_scene = grid_to_scene(*pos, self.cell_size)
                distance = (event.scenePos() - pos_scene).manhattanLength()
                if distance < min_distance:
                    min_distance = distance
                    closest_pos = pos

            if closest_pos:
                self.end_row, self.end_col = closest_pos
                start_pos = grid_to_scene(self.start_row, self.start_col, self.cell_size)
                end_pos = grid_to_scene(self.end_row, self.end_col, self.cell_size)
                self.update_wall_preview(start_pos, end_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle right-click mouse release for finalizing wall placement."""
        if not self.mouse_events_enabled:
            return
        if event.button() == Qt.MouseButton.RightButton and self.wall_preview:
            self.add_wall()
        else:
            super().mouseReleaseEvent(event)

    # === Wall Management ===

    def calculate_possible_wall_destinations(self, start_row, start_col):
        """Calculate possible wall placements based on starting row and column,
           ensuring the new wall doesn't overlap or traverse the middle of existing walls."""

        # Define possible positions
        up_pos = (start_row - 2, start_col)
        down_pos = (start_row + 2, start_col)
        left_pos = (start_row, start_col - 2)
        right_pos = (start_row, start_col + 2)

        self.game_state=self.turn_manager.game_state
        self.forbidden_walls= self.game_state.forbidden_walls

        # Validate and check each possible wall position
        self.possible_wall_destinations = []
        if is_valid_wall((start_row, start_col), up_pos, self.grid_size, self.placed_walls,forbidden_walls=self.forbidden_walls):
            self.possible_wall_destinations.append(up_pos)
        if is_valid_wall((start_row, start_col), down_pos, self.grid_size, self.placed_walls,forbidden_walls=self.forbidden_walls):
            self.possible_wall_destinations.append(down_pos)
        if is_valid_wall((start_row, start_col), left_pos, self.grid_size, self.placed_walls,forbidden_walls=self.forbidden_walls):
            self.possible_wall_destinations.append(left_pos)
        if is_valid_wall((start_row, start_col), right_pos, self.grid_size, self.placed_walls,forbidden_walls=self.forbidden_walls):
            self.possible_wall_destinations.append(right_pos)

    def add_wall(self, custom_start=None, custom_end=None):
        """Add the wall to the scene, update player's available walls, and render the wall if custom positions are provided."""
        # Use custom positions if provided, otherwise use the object's default start and end positions
        start_row, start_col = custom_start if custom_start else (self.start_row, self.start_col)
        end_row, end_col = custom_end if custom_end else (self.end_row, self.end_col)

        # Check if the wall is being placed at the start position
        if (end_row, end_col) == (start_row, start_col):
            self.removeItem(self.wall_preview)
        else:
            # Logic for placing the wall
            wall = order_walls([(start_row, start_col), (end_row, end_col)])
            self.placed_walls.append(wall)
            self.current_blocked_roads.extend(get_blocked_roads(wall))
            self.turn_manager.get_current_player().available_walls -= 1
            self.game.update_wall_count()
            move = ('wall',wall)
            # Check if custom start and end positions were provided and render the wall if true
            if custom_start and custom_end:
                start_pos = grid_to_scene(start_row, start_col, self.cell_size)
                end_pos = grid_to_scene(end_row, end_col, self.cell_size)
                self.render_wall(start_pos, end_pos)
            self.turn_manager.switch_turn(move)

        # Clear wall preview and reset positions
        self.wall_preview = None
        self.start_pos = None
        self.possible_wall_destinations = None

    def render_wall(self, start_pos, end_pos):
            """Render a permanent wall on the scene from start to end positions."""
            wall_item = QGraphicsRectItem()

            # Calculate the rectangle for the wall
            rect_x = min(start_pos.x(), end_pos.x())
            rect_y = min(start_pos.y(), end_pos.y())
            rect_width = abs(end_pos.x() - start_pos.x())
            rect_height = abs(end_pos.y() - start_pos.y())

            # Wall thickness
            wall_thickness = 4  # Adjust thickness as needed

            if rect_width > rect_height:
                rect_height = wall_thickness
            else:
                rect_width = wall_thickness

            # Set wall dimensions
            wall_item.setRect(rect_x, rect_y, rect_width, rect_height)

            # Set the wall's appearance (pen and brush)
            wall_item.setPen(self.pen_wall)
            if self.turn_manager.get_current_player().color == "red":
                wall_item.setBrush(Qt.GlobalColor.red)
            else:
                wall_item.setBrush(Qt.GlobalColor.blue)

            # Add the wall item to the scene
            self.addItem(wall_item)

    # === Wall Graphics ===

    def start_wall_preview(self, event):
        """Start the wall preview process on right-click event."""
        current_player = self.turn_manager.get_current_player()

        # Check if the current player has walls left to place
        if current_player.available_walls <= 0:
            print("No walls available")
            return

        # Get the scene position and grid coordinates
        scene_pos = event.scenePos()
        self.start_row, self.start_col = scene_to_grid(scene_pos, self.cell_size)
        self.end_row, self.end_col = self.start_row, self.start_col  # Initialize end position

        # Create the wall preview graphic
        self.wall_preview = QGraphicsRectItem()
        self.calculate_possible_wall_destinations(self.start_row, self.start_col)

        # Set pen and add to scene
        self.wall_preview.setPen(self.pen_wall)
        self.addItem(self.wall_preview)

        # Convert grid position to scene position and update wall preview
        self.start_pos = grid_to_scene(self.start_row, self.start_col, self.cell_size)
        self.update_wall_preview(self.start_pos, self.start_pos)

    def update_wall_preview(self, start_pos, end_pos):
        """Adjust the size and position of the wall preview."""
        rect_x = min(start_pos.x(), end_pos.x())
        rect_y = min(start_pos.y(), end_pos.y())
        rect_width = abs(end_pos.x() - start_pos.x())
        rect_height = abs(end_pos.y() - start_pos.y())

        # Wall thickness
        wall_thickness = 4  # Customize this value to change the thickness

        if rect_width > rect_height:
            rect_height = wall_thickness
        else:
            rect_width = wall_thickness

        self.wall_preview.setRect(rect_x, rect_y, rect_width, rect_height)
        self.wall_preview.setPen(self.pen_wall)
        if self.turn_manager.get_current_player().color == "red":
            self.wall_preview.setBrush(Qt.GlobalColor.red)
        else:
            self.wall_preview.setBrush(Qt.GlobalColor.blue)

    # === Overlays (Game Over and Rules) ===

    def create_overlay_label(self, text, font_size=24, opacity=0.75):
        """Create an overlay label in the center of the scene with the given text."""

        # Remove any existing overlay if needed
        self.clear_overlay()

        # Create a background rectangle for the text
        scene_rect = self.sceneRect()
        rect_width, rect_height = 300, 100  # Dimensions of the label background
        background = QGraphicsRectItem(
            (scene_rect.width() - rect_width) / 2,
            (scene_rect.height() - rect_height) / 2,
            rect_width, rect_height
        )
        background.setBrush(QColor(0, 0, 0, int(255 * opacity)))  # Semi-transparent black background

        # Create the text item
        text_item = QGraphicsTextItem(text)
        text_item.setDefaultTextColor(Qt.GlobalColor.white)  # White text
        text_item.setFont(QFont('Arial', font_size, QFont.Weight.Bold))  # Set the font and size

        # Center the text item within the background
        text_bounds = text_item.boundingRect()
        text_item.setPos(
            (scene_rect.width() - text_bounds.width()) / 2,
            (scene_rect.height() - text_bounds.height()) / 2
        )

        # Add both the background and the text to the scene
        self.addItem(background)
        self.addItem(text_item)

        # Keep track of them to remove later if needed
        self.overlay_items = [background, text_item]

    def clear_overlay(self):
        """Remove any overlay text and background from the scene."""
        if hasattr(self, 'overlay_items'):
            for item in self.overlay_items:
                self.removeItem(item)
            self.overlay_items = []

    def create_rules_overlay(self):
        # Create the rules text
        rules_text = (
            """
            <h2 style="text-align: center;">Quoridor Rules</h2>
            <p>The goal of Quoridor is to get your pawn to the opposite side of the board before your opponent does. You can move your pawn and place walls to block your opponent’s path.</p>

            <h4>Objective</h4>
            <p>Be the first player to move your pawn to the other side of the board.</p>

            <h4>Your Turn</h4>
            <p>On your turn, you can do one of two things:</p>
            <ul>
              <li>Move your pawn one space in any direction (up, down, left, or right).</li>
              <li>Place a wall to slow down your opponent.</li>
            </ul>

            <h4>Moving Your Pawn</h4>
            <p>Pawns move one square at a time. If your opponent’s pawn is right next to yours, you can jump over them—unless there’s a wall in the way.</p>

            <h4>Placing a Wall</h4>
            <p>Each player has 10 walls. To place a wall, <strong>right-click on the board, then drag</strong> to position it. Walls block paths, but you cannot block a player completely from reaching the other side.</p>

            <h4>Winning the Game</h4>
            <p>The first player to reach the opposite side of the board wins.</p>
            """
        )

        self.rules_label = QLabel(rules_text)
        self.rules_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 30px;
                border: 2px solid white;
            }
            """
        )

        # Set QLabel properties
        self.rules_label.setWordWrap(True)
        self.rules_label.setTextFormat(Qt.TextFormat.RichText)

        # Explicitly set a fixed width for the rules label to ensure proper wrapping
        fixed_width = int(self.sceneRect().width() * 0.9)  # 90% of the scene width
        self.rules_label.setFixedWidth(fixed_width)

        # Create a layout and add the QLabel to it
        layout = QVBoxLayout()
        layout.addWidget(self.rules_label)
        container = QWidget()
        container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        container.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Adjust container size based on the label
        container.adjustSize()

        return container

    def center_rules_container(self):
        """Centers the rules_container in the scene."""
        # Get the scene dimensions
        scene_rect = self.sceneRect()
        scene_width = scene_rect.width()
        scene_height = scene_rect.height()

        # Ensure that the container has adjusted to its content size
        self.rules_container.adjustSize()

        # Get the container's size
        container_width = self.rules_container.width()
        container_height = self.rules_container.height()

        # Calculate the position to center the container in the scene
        x_pos = (scene_width - container_width) / 2
        y_pos = (scene_height - container_height) / 2

        # Set the position of the container manually
        self.rules_container.move(int(x_pos), int(y_pos))

    def toggle_rules(self):
        if self.rules_container.isHidden():
            self.rules_container.show()
        else:
            self.rules_container.hide()


