# QuoridorX Repository Overview (Detailed)

## Project Snapshot

QuoridorX is a desktop implementation of the Quoridor board game built with Python and PyQt6.  
It supports:

- Local human vs human play (`1 vs 1`)
- Human vs AI play (`easy`, `medium`, `hard`, `impossible`)
- Interactive board movement and wall placement
- Pathfinding-based move validation and rule enforcement
- Minimax-based AI decision making with alpha-beta pruning

The project is lightweight and mostly self-contained in `src/`, with static assets in `resources/`.

## Tech Stack

- Language: Python
- UI Framework: PyQt6
- Theme: `qt-material` (`dark_teal.xml`)
- Rendering model: `QGraphicsScene` + `QGraphicsView`
- AI/Search:
  - BFS shortest-path search
  - DFS reachability checks
  - Minimax with alpha-beta pruning
- Distribution support: PyInstaller-compatible resource resolution via `sys._MEIPASS`

## Top-Level Structure

- `README.md` - end-user/project documentation and startup instructions
- `requirements.txt` - runtime dependencies (`PyQt6`, `qt-material`)
- `LICENSE` - license text
- `resources/` - image and icon assets
- `src/` - application code

## Source Code Map (`src/`)

### Entry + App Shell

- `src/app.py`
  - Application entry point.
  - Creates `QApplication`, applies theme, opens `GameWindow`.
  - Contains a `DEBUG` flag that suppresses stdout when disabled.

- `src/game_window.py`
  - Main orchestrator window (`QMainWindow`).
  - Creates board view, side panel widgets, game lifecycle actions.
  - Coordinates scene reset/start/end behavior and player instantiation.

### Core Domain Classes

- `src/classes/player.py`
  - Base player entity and UI item (`QGraphicsRectItem`).
  - Handles turn activation, valid moves, drag/drop movement, win detection.

- `src/classes/turn_manager.py`
  - Controls turn order, transition, and game-state refresh each turn.
  - Performs draw detection using repeated move patterns.
  - Calls win/draw end-state UI hooks.

- `src/classes/game_state.py`
  - Snapshot-like model rebuilt each turn from current scene/player state.
  - Computes shortest paths and wall legality context.
  - Supports simulation (`simulate_move_or_wall`) for AI search.

- `src/classes/grid_scene.py`
  - Board renderer + interaction layer (`QGraphicsScene`).
  - Handles:
    - Grid drawing
    - Move highlighting
    - Keyboard/mouse movement
    - Right-click drag wall preview and placement
    - Overlay UI (rules panel, win/draw messages)

### AI Layer

- `src/bot/bot.py`
  - `Bot` class extends `Player`.
  - Starts asynchronous AI thinking via worker thread.
  - Applies selected move/wall result back to scene/player APIs.

- `src/bot/bot_worker.py`
  - `QThread` worker performing move search.
  - Chooses move ordering by difficulty, runs minimax, emits selected action.
  - Supports skip action when no legal progress is available.

- `src/bot/bot_helper.py`
  - Core algorithms:
    - `minimax(...)` with alpha-beta pruning
    - `evaluate(...)` heuristic based on shortest-path deltas and wall advantage
    - intelligent move ordering logic (`get_intelligent_moves`, `get_by_difficulty`)

### Helper Utilities

- `src/helpers/path_helper.py`
  - BFS shortest path to goal column
  - DFS reachability checks
  - Additional BFS cell-to-cell utility
  - Path cache with pruning behavior

- `src/helpers/valid_moves_helper.py`
  - Movement generation with jump-over-opponent behavior.
  - Includes wall-aware adjustment when an adjacent opponent blocks direct jump.

- `src/helpers/wall_helpers.py`
  - Wall geometry and validity checks
  - Blocked-edge generation from wall placement
  - Forbidden-wall discovery (ensures neither player is fully blocked from goal)
  - Valid-wall generation for AI analysis and gameplay constraints

- `src/helpers/grid_helpers.py`
  - Conversion between grid coordinates and scene coordinates.

- `src/helpers/resource_helper.py`
  - Unified asset path resolver for:
    - Development execution
    - Bundled PyInstaller execution

### UI Layout Factories

- `src/ui/layouts.py`
  - Builds reusable side-panel containers for:
    - Start menu buttons
    - AI difficulty selection
    - In-game controls + wall counters
    - Post-game actions (restart/exit)

## Resource Layout (`resources/`)

- `resources/images/`
  - Pawn/bot avatars (`blue_player.png`, `red_player.png`, `easy_bot.png`, etc.)
  - Icons in `resources/images/icons/` (mode toggles, app icon)

Assets are loaded through `resource_path(...)` so both dev and packaged builds can find files correctly.

## Runtime Game Flow

1. `app.py` launches `GameWindow`.
2. User chooses mode:
   - local 1v1
   - vs AI + difficulty
3. `GameWindow.start_game(...)`:
   - creates fresh `GridScene`
   - creates `Player` / `Bot` instances
   - resets turn manager and cache
4. `TurnManager.start_turn()` builds a fresh `GameState`.
5. Current actor:
   - Human: valid moves highlighted; keyboard/drag movement enabled.
   - Bot: `BotWorker` thread computes best action.
6. Move or wall action is applied.
7. Turn switches, with:
   - draw-pattern check
   - win-condition check
   - updated wall counters and board indicators.

## Rule/Logic Enforcement Highlights

- Movement legality comes from `GameState.get_valid_moves(...)` + helper logic.
- Wall placement checks:
  - bounds
  - intersection/collision constraints
  - forbidden configurations that would block all routes to goal
- Win condition: player reaches target goal column.
- Draw condition: repeated pair patterns over recent move history.

## AI Behavior by Difficulty

- Easy:
  - restricted subset of "intelligent" moves
  - lower effective tactical depth/quality
- Medium:
  - broader intelligent move set
- Hard / Impossible:
  - includes wall tactics and deeper candidate sets
  - uses minimax + alpha-beta with broader ordering

General AI heuristic priorities:

- shorten own path to goal
- lengthen opponent path
- account for wall count advantage
- prefer stronger tactical sequence from evaluated tree

## Build, Run, and Packaging Notes

- Install:
  - `pip install -r requirements.txt`
- Run:
  - `cd src`
  - `python app.py`
- Packaging:
  - Code supports PyInstaller pathing via `_MEIPASS`.
  - Repository hints at packaged `.exe` release in docs.

## Current Repository Characteristics

- No formal test suite is present in the repo currently.
- No explicit linter/formatter configuration files are present.
- Architecture is straightforward and modular for a small desktop game:
  - UI + orchestration in window/scene
  - pure logic helpers for movement/walls/pathing
  - separate async worker for AI compute

## Practical Extension Points

If you plan to evolve this repository, the cleanest extension points are:

- Add tests around helper modules (`path_helper`, `valid_moves_helper`, `wall_helpers`) first.
- Expand AI by improving evaluation weights and transposition caching.
- Add game persistence (save/load state) by serializing `GameState` + wall/player data.
- Add profiling hooks around minimax depth and move ordering costs.
- Introduce packaging automation (build script or CI release pipeline).
