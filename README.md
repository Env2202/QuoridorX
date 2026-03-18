# QuoridorX - A PyQt6-Powered Quoridor Game

QuoridorX is a desktop implementation of the classic **Quoridor** board game built using **PyQt6**. The game features two modes of play: **1v1 multiplayer** or **player vs bot**, with adjustable AI difficulty levels ranging from *easy* to *impossible*. QuoridorX offers an intuitive user interface, smooth gameplay, and robust AI for solo play, making it an ideal game for both casual players and competitive strategists.

## 🎮 Features

### 1. **Two Modes of Play**
   - **Multiplayer Mode (1v1)**: Play against another human player locally on the same device.
   - **Single Player Mode (vs AI)**: Challenge yourself against the bot with four different AI difficulty levels (easy, medium, hard, and impossible).

### 2. **AI-Driven Opponent**
   - **Intelligent Pathfinding**: The AI leverages algorithms like BFS (Breadth-First Search) and DFS (Depth-First Search) to calculate optimal moves and paths.
   - **Minimax Algorithm with Alpha-Beta Pruning**: The AI's decision-making is powered by the minimax algorithm with alpha-beta pruning, allowing it to plan strategically and anticipate player moves, especially in the harder difficulties.
   - **Difficulty Levels**: The AI adapts to different levels of challenge, from simple and predictable moves at the easiest difficulty to complex, tactical gameplay at the "impossible" level, where wall placements and move predictions are optimized.

### 3. **Smooth User Interface**
   - The game interface is built using **PyQt6**, offering a visually appealing and responsive experience.
   - Players are represented with distinctive avatars, and the game provides real-time visual feedback like turn indicators and wall counts.
   - Features a **9x9 grid** where players can move their pawns and strategically place walls to block the opponent’s path.

### 4. **Wall Placement Mechanics**
   - Each player has 10 walls to strategically place on the board to hinder the opponent's progress.
   - Intelligent wall placements are essential in higher difficulties, where the AI prioritizes blocking the player’s shortest path and finding the most advantageous moves.

### 5. **Game Flow and Turn Management**
   - The game ensures smooth management of turns and game states, including visual effects for active players and winner announcements.
   - The bot adapts to changing situations, with its moves dynamically adjusting based on the board configuration and player's actions.

### 6. **Pathfinding Optimizations**
   - The game features optimized pathfinding with caching to speed up gameplay, reducing the need for repetitive calculations, especially when walls are placed or removed.

## 💻 Technologies

- **PyQt6**: For creating the main user interface, including the window layout, buttons, and grid-based game board.
- **Python**: Core logic for gameplay, AI algorithms, and pathfinding.
- **BFS & DFS Pathfinding Algorithms**: Efficient pathfinding for both player and AI movements.
- **Minimax Algorithm with Alpha-Beta Pruning**: AI decision-making for optimal moves in competitive play.
- **QGraphicsView & QGraphicsScene**: Used to render and manage game items (players, walls) on the board.
- **Custom Bot Integration**: Bot implementation with varying difficulty based on pathfinding, decision-making, and strategy.

## 🚀 How to Play

1. **Start the Game**: Choose between 1v1 multiplayer or play against the bot.
2. **Select AI Difficulty**: If you choose to play against the bot, you can select the difficulty (Easy, Medium, Hard, or Impossible).
3. **Gameplay**: Move your pawn across the 9x9 board, aiming to reach the opposite side while blocking your opponent with walls.
4. **Win the Game**: The first player to reach the opposite side of the board wins!

## 🛠️ Installation for Development Version

To play the development version, follow the instructions below:

1. Clone the repository:
   ```bash
   git clone https://github.com/MatteoPapa/QuoridorX.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   cd src
   python app.py
   ```

### ⚙️ Makefile-based Setup (Recommended)

This repository includes a root `Makefile` to simplify setup, testing, and common development tasks.

1. Bootstrap environment and install runtime dependencies:
   ```bash
   make bootstrap
   ```
2. (Optional) Install development tooling from `requirements-dev.txt`:
   ```bash
   make install-dev
   ```
3. Run the game:
   ```bash
   make run
   ```
4. Run tests:
   ```bash
   make test
   ```
5. Run full quality checks before opening a PR:
   ```bash
   make check
   ```

Useful targets:

- `make help` - List available commands
- `make info` - Print environment configuration
- `make activate-linux` - Print Linux/macOS virtual environment activation command
- `make activate-windows` - Print Windows PowerShell and CMD activation commands
- `make lint` - Run optional lint checks if linters are installed
- `make check` - Run lint + tests (recommended before PR)
- `make format` - Run optional formatter if installed
- `make clean` - Remove Python cache files
- `make deep-clean` - Remove cache files and virtual environment

> Note: `make` cannot keep a shell activated after the command exits. Use the printed activation command in your terminal if you want to activate the virtual environment manually.

## 📦 Standalone Executable Release

We also offer a **standalone executable** version for Windows. This version requires no additional setup—just download and play!

### 🔥 **Download the Standalone Version**

You can download the latest version of QuoridorX as an executable from the [Releases](https://github.com/MatteoPapa/QuoridorX/releases) section.

- **Version**: `v1.0.0`
- **Platform**: Windows
- **File**: `QuoridorX.exe`

### 🎮 **Features of the Standalone Version**

- **No Python Setup Required**: Simply download and run the game—no need to install Python or dependencies.
- **Full Functionality**: Enjoy all the features of QuoridorX, including 1v1 multiplayer, AI opponents with adjustable difficulty, and smooth gameplay.
- **Lightweight and Portable**: The executable version is lightweight, making it easy to download and run on any Windows machine.

### 📝 **How to Install and Play**

1. **Download the executable**: Go to the [Releases](https://github.com/MatteoPapa/QuoridorX/releases) page and download `QuoridorX.exe`.
2. **Run the game**: Double-click the `QuoridorX.exe` file to launch the game.
3. **Enjoy**: Start playing immediately—no installation required!

### 📦 **Release Notes - v1.0.0**

- **First release of QuoridorX as a standalone executable.**
- Includes the full feature set:
  - 1v1 multiplayer mode.
  - Player vs. Bot with 4 difficulty levels: Easy, Medium, Hard, Impossible.
  - AI powered by pathfinding algorithms and Minimax with alpha-beta pruning.
  - Smooth PyQt6-based user interface with turn indicators and wall counts.

### Known Issues
- Currently, the standalone version is available only for Windows. Stay tuned for future releases on other platforms!

## 👥 Contributions

Contributions are welcome! Feel free to open issues or submit pull requests to contribute new features, improvements, or bug fixes.

## 🛠️ Development

To contribute, simply fork the repository, create your feature branch, and submit a pull request. We appreciate any contributions to improve the game.

## 💬 Support

If you encounter any issues or have any questions, feel free to reach out via the [Issues](https://github.com/MatteoPapa/QuoridorX/issues) page.

---

**Enjoy playing QuoridorX!** 🎉

