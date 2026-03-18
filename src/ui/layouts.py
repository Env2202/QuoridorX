from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLCDNumber, QLabel, QWidget, QSizePolicy

from helpers.resource_helper import resource_path

FIXED_WIDTH = 200  # Set a fixed width for all layouts

def create_start_buttons_layout(game):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Example usage for loading icons with resource_path
    two_players_button = QPushButton("  1 vs 1")
    two_players_icon = QIcon(QPixmap(resource_path('resources/images/icons/two_players.svg')))
    two_players_button.setIcon(two_players_icon)
    two_players_button.clicked.connect(game.start_game)
    two_players_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    versus_ai_button = QPushButton("  vs AI")
    versus_ai_icon = QIcon(QPixmap(resource_path('resources/images/icons/ai.svg')))
    versus_ai_button.setIcon(versus_ai_icon)
    versus_ai_button.clicked.connect(game.select_difficulty)
    versus_ai_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # Add widgets to layout
    layout.addWidget(two_players_button)
    layout.addWidget(versus_ai_button)

    # Make sure the layout expands to fill the entire height
    layout.addStretch(1)

    show_rules_button = QPushButton("  Rules")
    show_rules_button.clicked.connect(game.show_rules)
    layout.setAlignment(show_rules_button, Qt.AlignmentFlag.AlignBottom)
    layout.addWidget(show_rules_button)

    # Create a QWidget to contain the layout and set the fixed width
    container = QWidget()
    container.setLayout(layout)
    container.setFixedWidth(FIXED_WIDTH)
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    return container

def create_ai_difficulty_layout(game):

    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    easy_button = QPushButton("Easy")
    easy_button.clicked.connect(lambda: game.start_game(vs_bot=True, difficulty="easy"))
    easy_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    easy_button.setStyleSheet("color: lightgreen; border: 2px solid lightgreen;")

    medium_button = QPushButton("Medium")
    medium_button.clicked.connect(lambda: game.start_game(vs_bot=True, difficulty="medium"))
    medium_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    medium_button.setStyleSheet("color: yellow; border: 2px solid yellow;")

    hard_button = QPushButton("Hard")
    hard_button.clicked.connect(lambda: game.start_game(vs_bot=True, difficulty="hard"))
    hard_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    hard_button.setStyleSheet("color: orange; border: 2px solid orange;")

    impossible_button = QPushButton("Impossible")
    impossible_button.clicked.connect(lambda: game.start_game(vs_bot=True, difficulty="impossible"))
    impossible_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    impossible_button.setStyleSheet("background-color:black; color: red; border: 2px solid red;")

    main_menu_button = QPushButton("Main Menu")
    main_menu_button.clicked.connect(game.end_game)
    main_menu_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    layout.addWidget(easy_button)
    layout.addWidget(medium_button)
    layout.addWidget(hard_button)
    layout.addWidget(impossible_button)

    layout.addStretch(1)

    layout.addWidget(main_menu_button)

    # Create a QWidget to contain the layout and set the fixed width
    container = QWidget()
    container.setLayout(layout)
    container.setFixedWidth(FIXED_WIDTH)
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    return container

def create_game_items_layout(game):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # Main Menu button (will expand to full width)
    exit_button = QPushButton("Main Menu")
    exit_button.clicked.connect(game.end_game)
    exit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(exit_button)

    # Walls label (centered)
    walls_label = QLabel("Walls:")
    walls_label.setStyleSheet("font-size: 16px; color: lightgray;")
    walls_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(walls_label)
    layout.setAlignment(walls_label, Qt.AlignmentFlag.AlignHCenter)

    # Blue player's LCD display (centered)
    blue_lcd_number = QLCDNumber()
    blue_lcd_number.setFixedSize(100, 100)
    blue_lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
    blue_lcd_number.setDigitCount(2)
    blue_lcd_number.display(10)
    blue_lcd_number.setStyleSheet("color: cyan;")
    blue_lcd_number.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(blue_lcd_number)
    layout.setAlignment(blue_lcd_number, Qt.AlignmentFlag.AlignHCenter)

    # Red player's LCD display (centered)
    red_lcd_number = QLCDNumber()
    red_lcd_number.setFixedSize(100, 100)
    red_lcd_number.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
    red_lcd_number.setDigitCount(2)
    red_lcd_number.display(10)
    red_lcd_number.setStyleSheet("color: red;")
    red_lcd_number.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(red_lcd_number)
    layout.setAlignment(red_lcd_number, Qt.AlignmentFlag.AlignHCenter)

    # Add a spacer/stretch so the content expands to fill the remaining space
    layout.addStretch(1)

    show_rules_button = QPushButton("  Rules")
    show_rules_button.clicked.connect(game.show_rules)
    layout.setAlignment(show_rules_button, Qt.AlignmentFlag.AlignBottom)
    layout.addWidget(show_rules_button)

    # Create a QWidget to contain the layout and set the fixed width
    container = QWidget()
    container.setLayout(layout)
    container.setFixedWidth(FIXED_WIDTH)
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    return container

def create_win_buttons_layout(game):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    exit_button = QPushButton("Exit")
    exit_button.clicked.connect(game.end_game)
    exit_button.setStyleSheet("border: 2px solid red; color: lightcoral;")
    exit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(exit_button)

    restart_button = QPushButton("Restart")
    restart_button.clicked.connect(game.restart_game)
    restart_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout.addWidget(restart_button)

    # Add a spacer/stretch to expand the layout to fill the height
    layout.addStretch(1)

    # Create a QWidget to contain the layout and set the fixed width
    container = QWidget()
    container.setLayout(layout)
    container.setFixedWidth(FIXED_WIDTH)
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    return container
