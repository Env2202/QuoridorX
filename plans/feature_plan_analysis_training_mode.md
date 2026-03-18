# Feature Plan: Analysis & Training Mode (Move Browser + Engine Hints)

## 1) Feature Definition

Add a dedicated local-only `Analysis` mode that allows players to load a completed or in-progress game, navigate move-by-move, request AI suggestions at any position, and visualize candidate move hints directly on the board.

Core capabilities:

- New `Analysis` entry point from the main menu
- Load source:
  - Last played game
  - Saved game record file
- Move navigation:
  - first / previous / next / last
  - jump to move index
  - synchronized move list + board
- AI insight at current position:
  - top `N` candidate moves
  - evaluation values
  - board overlays for suggested pawn moves and wall placements
- Fully local execution using existing QuoridorX minimax engine

## 2) Why This Feature Is Valuable

- Increases player retention through self-improvement loops
- Makes AI decisions transparent and educational
- Reuses existing engine investment for post-game learning
- Establishes a foundation for future coach mode / puzzle mode

## 3) Non-Goals (Initial Release)

- No cloud sync or online analysis service
- No opening book or neural-network evaluation
- No persistent analysis cache database
- No multi-line variation tree editing (single mainline browsing only)

## 4) Assumptions and Constraints

- Existing local game logic and AI already operate deterministically for legal actions
- UI stack is PyQt6 and currently owns substantial game flow
- Analysis mode should not mutate active gameplay session state
- Analysis calculations must not block UI interactions

## 5) Architecture Overview

### 5.1 Main Components

- **Game Record Layer**
  - Versioned JSON schema
  - Encode/decode move list and metadata
  - Reconstruct board state at any ply index

- **Analysis Session Model**
  - In-memory immutable-like session object:
    - loaded record
    - current move index
    - derived board state
    - latest analysis result

- **Analysis UI**
  - Board widget reuse
  - Move list widget
  - Navigation toolbar and analysis controls
  - Status + cancel affordances

- **Evaluation Service**
  - Adapter around minimax engine
  - Returns top `N` ranked candidates with score and metadata
  - Usable in non-playing mode context

- **Hint Renderer**
  - Visual overlays for candidate pawn targets and wall suggestions
  - Optional score-based styling

### 5.2 Data Flow (High Level)

1. User opens Analysis mode and loads game record.
2. Session computes board state at selected move index.
3. Board and move list update in sync.
4. User requests suggestion.
5. Worker thread runs engine evaluation for current state.
6. UI receives result, updates suggestion panel, and draws board hints.

## 6) Delivery Phases (LLM-Sized Chunks)

## Phase 0 - Discovery and Baseline Mapping

### Objective

Map existing engine, turn manager, and board rendering seams to minimize risky refactoring.

### Implementation Scope

- Identify authoritative sources for:
  - board state
  - move representation
  - move application
  - AI search invocation
- Write a brief technical note with:
  - current module boundaries
  - extension points
  - known coupling hotspots

### Acceptance Criteria

- A concrete mapping doc exists with file/module references and call paths.
- Team agrees on where new analysis modules will live.
- No runtime behavior changes introduced.

### Suggested LLM Prompt

```text
You are working in a PyQt6 Quoridor project. Analyze the codebase and produce a concise architecture note for implementing an Analysis Mode.

Deliver:
1) Current move representation and where moves are applied
2) How board state is stored and read for rendering
3) Where minimax AI is invoked and expected inputs/outputs
4) Recommended insertion points for:
   - game record serialization
   - non-playing evaluation API
   - analysis UI module
5) Risks from existing coupling and specific refactor suggestions

Constraints:
- Do not change runtime behavior
- Keep recommendations incremental
```

---

## Phase 1 - Game Record Serialization and Position Reconstruction

### Objective

Create a versioned game record format and deterministic board reconstruction API.

### Implementation Scope

- Add `GameRecord` JSON schema (v1) with:
  - metadata (version, created_at, source)
  - initial setup
  - ordered move log
  - optional result metadata
- Implement encode/decode utilities
- Implement API:
  - `reconstruct_state(record, move_index) -> board_state`
- Handle both pawn moves and wall placements

### Suggested Module Additions

- `src/analysis/record_schema.py`
- `src/analysis/record_io.py`
- `src/analysis/reconstruct.py`

### Acceptance Criteria

- Record schema is versioned and documented.
- Any legal game sequence can be round-tripped:
  - runtime game -> record JSON -> runtime state
- Reconstruction works for all indices:
  - `0`, middle, final
- Invalid record data produces clear validation errors.
- Automated tests pass for encode/decode and reconstruction.

### Suggested LLM Prompt

```text
Implement Phase 1 for Analysis Mode in this QuoridorX repository.

Tasks:
1) Add a versioned GameRecord v1 schema in Python (JSON-compatible)
2) Add encode/decode helpers with strict validation
3) Add reconstruct_state(record, move_index) to rebuild board state deterministically
4) Support both pawn and wall moves
5) Add tests:
   - round-trip encode/decode
   - reconstruct at index 0, mid-game, and final move
   - invalid input handling

Requirements:
- Keep changes local and backward compatible
- Reuse existing move legality/apply logic where possible
- Return explicit error messages for malformed records
```

---

## Phase 2 - Analysis Mode Shell UI (Load + Navigate + Sync)

### Objective

Deliver an analysis-specific UI flow with move browsing and board synchronization.

### Implementation Scope

- Add main menu entry for `Analysis`
- Create analysis screen/window with:
  - board view
  - move list
  - controls: first/prev/next/last/go-to-index/request suggestion
- Wire signals/slots:
  - selecting move list row updates board
  - nav buttons update list selection and board
- Add load options:
  - from file
  - from last played game

### Suggested Module Additions

- `src/analysis/analysis_window.py`
- `src/analysis/analysis_controller.py`
- `src/analysis/analysis_session.py`

### Acceptance Criteria

- Analysis mode is reachable from main menu.
- A valid game can be loaded from both source options.
- Move list and board remain synchronized in both interaction directions.
- Navigation controls correctly clamp to valid bounds.
- No mutation of active normal gameplay state occurs while analyzing.

### Suggested LLM Prompt

```text
Implement Phase 2 Analysis UI for QuoridorX.

Build:
1) Main menu entry point to launch Analysis mode
2) Analysis window or stacked widget with:
   - board view (reuse existing board widget)
   - move list widget
   - nav controls: first/prev/next/last/go-to/request suggestion
3) Controller/session wiring so move list and board stay synchronized
4) Load game from:
   - saved record file
   - last played game

Constraints:
- Do not regress existing gameplay mode
- Keep UI responsive and modular
- Prefer clear signal/slot flow over tightly coupled direct mutation
```

---

## Phase 3 - Engine Evaluation API (Top-N Candidates)

### Objective

Expose a reusable evaluation API for analysis context.

### Implementation Scope

- Wrap minimax engine into service function/class:
  - inputs:
    - board state
    - side to move
    - depth/options
    - `top_n`
  - outputs:
    - ordered candidate moves
    - score/evaluation per move
    - optional principal variation summary
- Ensure no side effects on live game objects
- Define stable result model for UI consumption

### Suggested Module Additions

- `src/analysis/eval_service.py`
- `src/analysis/eval_models.py`

### Acceptance Criteria

- API returns deterministic results for same state/options.
- At least top 3 move suggestions are returned when available legal moves >= 3.
- Evaluation output is consumable by UI without additional engine coupling.
- API behavior matches existing AI playing mode preferences at equivalent depth.
- Tests validate consistency and non-mutation guarantees.

### Suggested LLM Prompt

```text
Implement Phase 3: reusable minimax evaluation API for Analysis Mode.

Deliver:
1) An eval service that accepts board state, side-to-move, depth, top_n
2) Output model with ranked candidate moves and evaluation scores
3) No mutation of gameplay session objects
4) Tests for:
   - deterministic repeated call output
   - consistency with existing AI choice at same depth
   - top_n bounds and edge cases

Guidance:
- Reuse existing minimax/alpha-beta logic
- Keep API pure and UI-agnostic
```

---

## Phase 4 - Hint Visualization Layer

### Objective

Render AI suggestions as clear, non-intrusive overlays in the board view.

### Implementation Scope

- Pawn move hints:
  - highlight candidate destination tiles
- Wall move hints:
  - render ghost wall overlays at suggested placements
- Optional score mapping:
  - intensity or color scale by ranking/evaluation
- Add legend/tooltips for interpretation

### Suggested Module Additions

- `src/analysis/hint_overlay.py`
- `src/analysis/hint_presenter.py`

### Acceptance Criteria

- Top candidate pawn and wall suggestions are visually distinguishable.
- Overlays clear/reset when navigating to a different move index.
- Overlay rendering never modifies board legality/state.
- Visuals remain readable on supported themes/backgrounds.
- Basic accessibility check passes (contrast and color distinction).

### Suggested LLM Prompt

```text
Implement Phase 4 hint visualization for QuoridorX Analysis Mode.

Requirements:
1) Highlight pawn destination candidates on the board
2) Show ghost wall placements for wall move suggestions
3) Style hints by rank/evaluation (at least 2 visual levels)
4) Ensure hints clear when move index changes or analysis is rerun
5) Add minimal legend/tooltip text for user clarity

Constraints:
- Rendering must be side-effect free
- Keep existing board interactions stable
```

---

## Phase 5 - Background Analysis Execution and Cancellation

### Objective

Keep UI responsive while running minimax analysis.

### Implementation Scope

- Move analysis execution into worker thread (`QThread` or `QThreadPool`)
- Add stateful request lifecycle:
  - idle
  - running
  - canceled
  - completed
  - failed
- UI affordances:
  - `Analyzing...` status indicator
  - cancel button
  - disable conflicting controls while running (as needed)

### Suggested Module Additions

- `src/analysis/eval_worker.py`
- `src/analysis/request_state.py`

### Acceptance Criteria

- Triggering suggestion does not freeze UI during long searches.
- Cancel action reliably prevents stale result from being applied.
- Repeated requests cannot corrupt session state.
- Exceptions in worker path are surfaced as user-safe messages.
- Thread cleanup is verified on window close.

### Suggested LLM Prompt

```text
Implement Phase 5 asynchronous analysis execution for PyQt6.

Deliver:
1) Worker-thread based evaluation request pipeline
2) Request lifecycle state management
3) UI status indicator + cancel action
4) Safe handoff of results back to main thread
5) Tests (or testable hooks) for cancellation and stale-result protection

Constraints:
- No GUI thread blocking
- Prevent race conditions when users click quickly
- Keep code readable and maintainable
```

---

## Phase 6 - QA Hardening, Defaults, and UX Polish

### Objective

Finalize feature quality, consistency, and usability.

### Implementation Scope

- Add/complete tests:
  - serialization round-trip
  - reconstruction correctness
  - eval consistency with playing mode
  - navigation boundary behavior
  - async cancellation behavior
- UX improvements:
  - keyboard shortcuts for navigation
  - sensible default depth by difficulty profile
  - clear visual distinction between normal mode and analysis mode
  - empty-state and error-state messaging

### Acceptance Criteria

- Test suite covers critical analysis path and passes in CI.
- Typical analysis interactions complete without crashes or hangs.
- Default settings provide sub-second feedback for common positions (target configurable).
- Users can clearly distinguish analysis mode from active gameplay mode.
- Release checklist for feature sign-off is complete.

### Suggested LLM Prompt

```text
Implement Phase 6 quality pass for Analysis Mode.

Tasks:
1) Add/expand tests for reconstruction, eval parity, navigation, async cancellation
2) Add keyboard shortcuts for move navigation
3) Configure practical default analysis depth and expose setting if appropriate
4) Improve mode-specific UX messaging and labels
5) Fix identified defects from lint/test feedback

Outcome:
- Production-ready local Analysis Mode with stable UX
```

## 7) Cross-Phase Definition of Done

- User can open Analysis mode from main menu.
- User can load last game or file-based record.
- User can navigate full move history with synchronized board + list.
- User can request top `N` AI suggestions at any position.
- Suggestions are visualized (pawn and wall) clearly and safely.
- Analysis runs asynchronously with cancellation and no GUI freeze.
- Core tests pass for serialization, reconstruction, evaluation consistency, and UX-critical controls.

## 8) Risk Register and Mitigations

- **Risk:** Existing game state model is too UI-coupled for clean reconstruction  
  **Mitigation:** Add thin adapter layer around current apply logic before deeper refactor.

- **Risk:** Minimax runtime too slow for interactive UX  
  **Mitigation:** Depth defaults, iterative deepening option, and cancellation support.

- **Risk:** Wall hint rendering becomes visually noisy  
  **Mitigation:** cap visible candidates, add rank filters, provide legend toggle.

- **Risk:** Async race conditions cause stale overlays  
  **Mitigation:** request IDs and main-thread guard before applying results.

## 9) Suggested Implementation Order (Execution Checklist)

1. Phase 0 - discovery note
2. Phase 1 - record schema + reconstruction API
3. Phase 2 - analysis UI shell + navigation
4. Phase 3 - evaluation API
5. Phase 5 - async worker (before visual polish to keep test loop fast)
6. Phase 4 - hint rendering integration
7. Phase 6 - tests, shortcuts, defaults, polish

## 10) Suggested Files/Modules

- `src/analysis/__init__.py`
- `src/analysis/record_schema.py`
- `src/analysis/record_io.py`
- `src/analysis/reconstruct.py`
- `src/analysis/analysis_session.py`
- `src/analysis/analysis_controller.py`
- `src/analysis/analysis_window.py`
- `src/analysis/eval_models.py`
- `src/analysis/eval_service.py`
- `src/analysis/eval_worker.py`
- `src/analysis/hint_overlay.py`
- `tests/analysis/test_record_roundtrip.py`
- `tests/analysis/test_reconstruct_state.py`
- `tests/analysis/test_eval_parity.py`
- `tests/analysis/test_analysis_navigation.py`
