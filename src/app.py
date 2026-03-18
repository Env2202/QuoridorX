import sys
import os
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from game_window import GameWindow

DEBUG = False

if not DEBUG:
    sys.stdout = open(os.devnull, 'w')

def main():

    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    app = QApplication(sys.argv)
    game_window = GameWindow()
    apply_stylesheet(app, theme='dark_teal.xml')
    game_window.show()
    game_window.center_window()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
