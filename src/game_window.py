import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QGraphicsView, QMainWindow, QWidget, QHBoxLayout

from bot.bot import Bot
from helpers.path_helper import clear_cache
from helpers.resource_helper import resource_path
from ui.layouts import create_start_buttons_layout, create_game_items_layout, create_win_buttons_layout, \
    create_ai_difficulty_layout
from classes.grid_scene import GridScene
from classes.player import Player
from classes.turn_manager import TurnManager

#Enable AI vs AI
AIvsAI=False
TESTING_DIFFICULTY='easy'

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuoridorX")
        icon_path=resource_path('resources/images/icons/quoridor.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addSpacing(20)

        # Turn Manager
        self.turn_manager = TurnManager(self,'blue')

        # Create the QGraphicsView
        self.window_size = 700
        self.grid_size = 9
        self.cell_size = (self.window_size - 100) // 9

        self.scene = GridScene(game=self)
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(self.window_size, self.window_size)
        self.view.setSceneRect(0, 0, self.window_size - 100, self.window_size - 100)  # Set scene size to fit 9x9 grid

        # Add widgets to layout
        self.layout.addWidget(self.view)

        # Create a container widget for the starting game buttons
        self.start_buttons_container = create_start_buttons_layout(self)
        self.layout.addWidget(self.start_buttons_container)

        # Create a container widget for the difficulty buttons (Hidden by default)
        self.difficulty_buttons_container = create_ai_difficulty_layout(self)
        self.layout.addWidget(self.difficulty_buttons_container)
        self.difficulty_buttons_container.hide()

        # Create a container widget for the game items (Hidden by default)
        self.game_items_container = create_game_items_layout(self)
        self.layout.addWidget(self.game_items_container)
        self.game_items_container.hide()

        # Create a container widget for the win buttons (Hidden by default)
        self.win_buttons_container = create_win_buttons_layout(self)
        self.layout.addWidget(self.win_buttons_container)
        self.win_buttons_container.hide()

        # Initialize players to None
        self.blue_player = None
        self.red_player = None
        self.vs_bot = False
        self.bot_difficulty = None

    def center_window(self):
        """Center the window on the screen using QStyle::alignedRect."""
        # Get the primary screen
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        # Use QStyle::alignedRect to calculate the centered geometry
        center_rect = QApplication.style().alignedRect(
            Qt.LayoutDirection.LeftToRight,
            Qt.AlignmentFlag.AlignCenter,
            self.size(),
            available_geometry
        )

        # Set the geometry of the window to the centered geometry
        self.setGeometry(center_rect)

    def select_difficulty(self):
        """Show the difficulty buttons to select the AI difficulty."""
        self.start_buttons_container.hide()
        self.difficulty_buttons_container.show()

    def start_game(self, vs_bot=False,difficulty=None):
        """Start or Restart the game with the option to play vs a bot."""
        # Remove the current scene and create a new one
        self.scene = GridScene(game=self)
        self.view.setScene(self.scene)

        # Register scene in the turn manager
        self.turn_manager.register_scene(self.scene)
        self.turn_manager.move_history = []

        # Show the during-game buttons
        self.difficulty_buttons_container.hide()
        self.start_buttons_container.hide()
        self.win_buttons_container.hide()
        self.game_items_container.show()

        # Clear the pathfinding cache
        clear_cache()

        blue_player_image_path = resource_path('resources/images/blue_player.png')

        if vs_bot:
            if difficulty == 'easy':
                red_player_image_path = resource_path('resources/images/easy_bot.png')
            elif difficulty == 'medium':
                red_player_image_path = resource_path('resources/images/medium_bot.png')
            elif difficulty == 'hard':
                red_player_image_path = resource_path('resources/images/hard_bot.png')
            elif difficulty == 'impossible':
                red_player_image_path = resource_path('resources/images/impossible_bot.png')
        else:
            red_player_image_path = resource_path('resources/images/red_player.png')

        # Define player settings for blue and red players (human players)
        blue_player_settings = {
            "image_path": blue_player_image_path,
            "cell_size": self.cell_size,
            "row": 4,
            "col": 0,
            "goal_col": 8,
            "color": "blue",
            "available_walls": 10
        }

        red_player_settings = {
            "image_path": red_player_image_path,
            "cell_size": self.cell_size,
            "row": 4,
            "col": 8,
            "goal_col": 0,
            "color": "red",
            "available_walls": 10
        }

        # Add the blue player (human)
        self.blue_player = Player(blue_player_settings, game=self)

        # If playing vs bot, initialize the red player as a bot
        if vs_bot:
            # Initialize red player as a bot
            print("Bot created")
            self.vs_bot = True
            self.bot_difficulty = difficulty
            self.red_player = Bot(red_player_settings, game=self,difficulty=difficulty)

            #AI VS
            if AIvsAI:
                self.blue_player= Bot(blue_player_settings, game=self,difficulty=TESTING_DIFFICULTY)
        else:
            # Initialize red player as a human player
            self.vs_bot = False
            self.bot_difficulty = None
            self.red_player = Player(red_player_settings, game=self)

        # Add players to the scene
        self.scene.blue_player = self.blue_player
        self.scene.red_player = self.red_player
        self.scene.addItem(self.blue_player)
        self.scene.addItem(self.red_player)
        self.turn_manager.reset_turn()

        # Register players in the turn manager
        self.turn_manager.register_players(self.red_player, self.blue_player)
        self.update_wall_count()

    def restart_game(self):
        """Restart the game with the same settings."""
        self.start_game(vs_bot=self.vs_bot,difficulty=self.bot_difficulty)

    def change_turn(self, color):
        """Change the turn label to the given color."""
        if color == 'blue':
            self.view.setStyleSheet("border: 2px solid blue;")
        else:
            self.view.setStyleSheet("border: 2px solid red;")

    def end_game(self):
        """End the game and show the start buttons."""
        bot_worker = getattr(self.turn_manager.red_player, 'bot_worker', None)
        if bot_worker and bot_worker.isRunning():
            print("Stopping bot worker")
            bot_worker.stop()
            bot_worker.wait()
        self.vs_bot = False
        self.difficulty=None
        self.difficulty_buttons_container.hide()
        self.game_items_container.hide()
        self.win_buttons_container.hide()
        self.start_buttons_container.show()
        self.scene = GridScene(game=self)
        self.view.setScene(self.scene)
        self.view.setStyleSheet("")

    def win_game(self, player):
        """End the game and show the start buttons."""
        self.game_items_container.hide()
        self.start_buttons_container.hide()
        self.scene.create_overlay_label(f"{player.color.capitalize()} player wins!")
        self.win_buttons_container.show()

    def draw_game(self):
        """End the game and show the start buttons."""
        self.game_items_container.hide()
        self.start_buttons_container.hide()
        self.scene.create_overlay_label("Draw by repetition.")
        self.win_buttons_container.show()

    def update_wall_count(self):
        """Update the wall count for the given player color."""
        if self.red_player is None or self.blue_player is None:
            return
        self.game_items_container.layout().itemAt(2).widget().display(self.blue_player.available_walls)
        self.game_items_container.layout().itemAt(3).widget().display(self.red_player.available_walls)

    def show_rules(self):
        self.scene.toggle_rules()
