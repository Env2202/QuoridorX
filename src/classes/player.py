from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem, QStyle
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QPixmap, QColor
from helpers.grid_helpers import grid_to_scene, scene_to_grid  # Importing helper functions

class Player(QGraphicsRectItem):
    def __init__(self, player_settings, game):
        super().__init__()

        # Extract settings from the player_settings dictionary
        self.cell_size = player_settings.get("cell_size")
        self.scene_ref = game.scene
        self.color = player_settings.get("color")
        self.turn_manager = game.turn_manager

        # Player's grid position
        self.row = player_settings.get("row")  # Row in the grid
        self.col = player_settings.get("col")  # Column in the grid
        self.goal_col = player_settings.get("goal_col")  # Goal column for the player


        self.valid_moves = {}  # Dictionary to store valid moves
        self.available_walls = player_settings.get("available_walls", 10)  # Default to 10 walls

        self.won=False

        # Create player and set its initial scene position based on row/col
        self.create_player(player_settings.get("image_path"), self.cell_size)
        self.setPos(grid_to_scene(self.row, self.col, self.cell_size))  # Use helper function

    def paint(self, painter, option, widget=None):
        # Remove automatic border painted when selected
        option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, option, widget)

    def create_player(self, image_path, cell_size):
        """Create the visual representation of the player."""
        offset = 20  # Offset to make the player smaller than the grid cell
        self.setRect(offset // 2, offset // 2, cell_size - offset, cell_size - offset)

        # Set a transparent border for the player rectangle
        pen = QPen(QColor(0, 0, 0, 0))  # Set transparent border
        self.setPen(pen)

        self.set_flags(False)  # Disable movement by default

        # Create the pixmap (image) and scale it to fit within the rectangle
        self.pixmap_item = QGraphicsPixmapItem(self)
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(cell_size - offset, cell_size - offset)
        self.pixmap_item.setPixmap(pixmap)
        self.pixmap_item.setOffset(offset / 2, offset / 2)  # Center the pixmap within the rectangle

    def set_flags(self, flag):
        """Enable or disable movement and selection of the player."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, flag)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, flag)
        if flag:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def on_turn(self):
        """Called when it's this player's turn."""

        # Get valid moves from the scene
        self.valid_moves = self.scene_ref.get_valid_moves(self)
        if not self.valid_moves and self.available_walls == 0:
            self.turn_manager.switch_turn(('skip',))
            return
        # Allow the player to move
        self.scene_ref.enable_mouse_events()
        self.set_flags(True)
        self.scene_ref.clear_possible_moves()
        self.scene_ref.highlight_possible_moves(self)

    def on_end_turn(self):
        """Called when the player's turn ends."""
        self.set_flags(False)  # Disable movement

    def mousePressEvent(self, event):
        """Handle the mouse press event on the player."""
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle the mouse release event and snap player to grid if valid."""
        if event.button() == Qt.MouseButton.LeftButton:
            current_pos = self.pos()
            new_row, new_col = scene_to_grid(current_pos, self.cell_size)
            self.move_player(new_row, new_col)
        super().mouseReleaseEvent(event)

    def move_player(self,new_row,new_col):
        # Check if the new position has not changed
        if new_row == self.row and new_col == self.col:
            # Position hasn't changed, snap back to original position
            self.setPos(grid_to_scene(self.row, self.col, self.cell_size))
        else:
            # Check if the new position is valid
            if self.is_position_valid(new_row, new_col):
                #Disable key pressing for the rest of the turn
                self.scene_ref.keyPressed=True
                # Update player's position to the new grid position
                self.row, self.col = new_row, new_col
                self.setPos(grid_to_scene(new_row, new_col, self.cell_size))

                if self.col == self.goal_col:
                    self.won = True
                    self.scene_ref.clear_possible_moves()
                    self.turn_manager.win_game(self)
                else:
                    move= ('move',(new_row,new_col))
                    self.turn_manager.switch_turn(move)  # End the turn after moving
            else:
                # Undo the drag by reverting to the initial position
                self.setPos(grid_to_scene(self.row, self.col, self.cell_size))

    def is_position_valid(self, row, col):
        """Check if the target grid position (row, col) is valid."""
        return any(new_row == row and new_col == col for new_row, new_col in self.valid_moves.values())