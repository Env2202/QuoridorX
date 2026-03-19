# Refactor Plan: Engine/Domain Decoupling and Architecture Hardening

## 1) Refactor Goal

Execute a complex, non-trivial refactor that separates core Quoridor rules and AI orchestration from PyQt UI code, while preserving gameplay behavior and improving maintainability, testability, and delivery reliability.

Primary direction:

- Extract a headless game engine and domain model
- Reduce UI responsibilities to rendering and interaction mapping
- Consolidate AI and hint logic through one decision pipeline
- Standardize tests and quality gates

## 2) Benefits (Brief)

- **Safer changes:** Core gameplay rules become easier to modify without breaking UI paths.
- **Higher confidence:** Domain and engine become testable without Qt dependencies.
- **Faster feature delivery:** New modes (analysis/training/online) can reuse engine APIs.
- **Better performance tuning:** AI and pathfinding can be optimized in isolation.
- **Lower onboarding cost:** Clear module boundaries reduce cognitive overhead.

## 3) Delivery Phases

## Phase 0 - Baseline and Refactor Contract

### Objective

Create a stable baseline and define explicit architectural boundaries before moving code.

### Implementation Scope

- Record baseline behavior for:
  - move legality
  - wall legality
  - turn switching
  - game-end detection
- Add an architecture note documenting:
  - current coupling hotspots
  - target boundaries (UI vs engine vs domain)
  - migration constraints
- Define canonical data contracts for board state and actions.

### Acceptance Criteria

- Existing tests pass before any structural migration.
- Baseline metrics are captured (test runtime and representative AI timing).
- Architecture contract doc exists and identifies target modules and ownership.
- No user-visible gameplay behavior changes in this phase.

### Suggested LLM Prompt

```text
Analyze this QuoridorX repository and produce a refactor baseline report for engine/domain decoupling.

Deliver:
1) Current architecture map and coupling hotspots
2) Canonical data contracts proposal for board state and actions
3) Baseline behavior checklist and measurable metrics to track regressions
4) A migration contract with explicit "do not break" constraints

Constraints:
- Do not change runtime behavior
- Keep recommendations incremental and file-specific
```

---

## Phase 1 - Canonical Domain Model and State Normalization

### Objective

Introduce normalized, UI-agnostic domain data structures and adapt existing code to consume them.

### Implementation Scope

- Add domain models for:
  - `BoardState`
  - `PlayerState`
  - `Action` (move/wall/skip)
  - normalized wall/blocked-road representation
- Move simulation-only entities out of mixed files into dedicated domain modules.
- Create adapters from current UI/game objects to domain models.
- Remove representation drift across helpers (path, valid moves, wall helpers).

### Acceptance Criteria

- Domain objects contain no Qt/PyQt references.
- A single wall and blocked-road representation is used across core logic.
- Adapters are tested for valid and invalid transformations.
- Existing move/wall legality tests still pass without behavior drift.

### Suggested LLM Prompt

```text
Implement Phase 1 in QuoridorX: add a canonical domain model layer and normalize state representations.

Tasks:
1) Create BoardState, PlayerState, Action models
2) Standardize wall and blocked-road representation across helpers
3) Add adapters from current runtime objects to domain models
4) Refactor usage points with minimal behavior change
5) Add tests for adapter correctness and normalization invariants

Requirements:
- No Qt types in domain modules
- Preserve gameplay behavior
- Keep refactor incremental and reviewable
```

---

## Phase 2 - Headless Game Engine Extraction (Strangler Pattern)

### Objective

Move turn flow and rules orchestration into a headless engine while keeping current UI functional.

### Implementation Scope

- Implement `GameEngine` APIs:
  - `start_game`
  - `get_legal_actions`
  - `apply_action`
  - `is_terminal`
- Relocate turn switching and game-end resolution into engine services.
- Keep UI running via compatibility adapters that call the engine.
- Add event/result DTOs for UI consumption.

### Acceptance Criteria

- UI no longer mutates core rules state directly.
- Engine can run and be tested without Qt.
- Existing gameplay flows (human vs human, human vs bot) still work through UI.
- Integration tests assert parity between legacy behavior and engine behavior.

### Suggested LLM Prompt

```text
Implement Phase 2 in QuoridorX: extract a headless GameEngine while preserving current UI behavior.

Deliver:
1) Engine APIs for start_game, get_legal_actions, apply_action, is_terminal
2) Turn and terminal-state logic moved out of UI orchestration
3) Compatibility adapter so existing UI still functions
4) Integration tests that verify behavior parity with pre-refactor flow

Constraints:
- No breaking changes to user-visible gameplay
- Avoid large-bang rewrite; use strangler migration
```

---

## Phase 3 - AI and Hint Pipeline Unification

### Objective

Create one reusable AI decision pipeline used by bot turns and player hints.

### Implementation Scope

- Introduce a single AI entrypoint (for example `choose_action(state, config)`).
- Consolidate duplicated minimax orchestration and move ordering logic.
- Move hint decision logic out of UI rendering classes.
- Add deterministic execution controls (seed/config) for reproducibility.

### Acceptance Criteria

- Bot turns and hint generation both call the same AI decision API.
- UI modules contain presentation-only hint rendering, no search orchestration.
- Repeated calls with same state/config produce deterministic outputs.
- AI latency is stable or improved against baseline budget.

### Suggested LLM Prompt

```text
Implement Phase 3 in QuoridorX: unify bot and hint decision logic into one AI pipeline.

Tasks:
1) Add a single choose_action API that supports bot and hint contexts
2) Remove duplicated minimax/move-ordering orchestration from UI code
3) Keep rendering separate from decision-making
4) Add deterministic controls and tests for repeatability
5) Verify latency does not regress compared to baseline

Requirements:
- Backward-compatible behavior
- Clear separation between decision and presentation layers
```

---

## Phase 4 - UI Decomposition and Interaction Boundary Cleanup

### Objective

Split overloaded scene/window classes into focused UI components.

### Implementation Scope

- Decompose current scene responsibilities into:
  - board renderer
  - wall input handler
  - overlay/hint presenter
  - UI-to-engine interaction mapper
- Replace fragile layout index lookups with explicit widget references.
- Standardize UI event handling and error messaging.

### Acceptance Criteria

- Monolithic scene class size and responsibility are significantly reduced.
- UI event handlers do not perform core rules validation directly.
- Widget access uses stable references instead of magic indices.
- UI smoke tests cover core interactions without engine mutation leaks.

### Suggested LLM Prompt

```text
Implement Phase 4 in QuoridorX: decompose the UI layer and clean interaction boundaries.

Deliver:
1) Split scene/window responsibilities into focused components
2) Replace index-based widget access with explicit references
3) Ensure UI handlers delegate gameplay decisions to engine APIs
4) Add/update UI smoke tests for movement, wall placement, and hints

Constraints:
- Keep UX behavior consistent
- Avoid introducing new coupling to engine internals
```

---

## Phase 5 - Test Architecture Overhaul and Invariant Coverage

### Objective

Restructure tests by layer and add invariant-focused coverage for long-term refactor safety.

### Implementation Scope

- Reorganize tests into:
  - `tests/domain`
  - `tests/engine`
  - `tests/ui_adapter`
  - `tests/integration`
- Centralize shared fixtures/factories and remove duplicated mocks.
- Add invariant tests (including property-style tests where practical):
  - legal moves never cross blocked roads
  - walls cannot fully block all paths
  - engine transitions preserve board consistency

### Acceptance Criteria

- Clear marker-based test selection works (`unit`, `integration`, etc.).
- Duplicate mock scaffolding is replaced by shared fixtures/factories.
- Critical invariants are codified and passing.
- Coverage thresholds for domain/engine are defined and enforced.

### Suggested LLM Prompt

```text
Implement Phase 5 in QuoridorX: overhaul test architecture and add invariant coverage.

Tasks:
1) Reorganize tests by architectural layer
2) Consolidate duplicated mocks into shared fixtures/factories
3) Add invariant tests for legal moves, wall legality, and state transitions
4) Enforce meaningful coverage targets for domain and engine modules

Constraints:
- Preserve existing useful tests
- Improve maintainability and execution clarity
```

---

## Phase 6 - Tooling, CI, and Release Pipeline Hardening

### Objective

Make quality checks mandatory and delivery workflows reproducible.

### Implementation Scope

- Align local and CI commands (pytest-first flow, consistent check targets).
- Enforce lint/format/type checks in CI.
- Improve container workflow:
  - source-first Docker build
  - optional commit-based mode as parameter
  - `.dockerignore` hygiene
- Document release build steps for executable packaging.

### Acceptance Criteria

- CI blocks merges on failed quality checks.
- `make check` mirrors CI quality gates.
- Docker build is reproducible from local source.
- Release workflow is documented and reproducible by another developer.

### Suggested LLM Prompt

```text
Implement Phase 6 in QuoridorX: harden tooling, CI, and release workflows.

Deliver:
1) CI pipeline for lint, format, tests, and coverage gates
2) Local commands aligned with CI checks
3) Improved Docker build flow with source-first reproducibility
4) Documented executable release process

Requirements:
- Keep contributor workflow simple
- Fail fast on quality issues
```

## 4) Cross-Phase Done Criteria

- Core game logic is independently testable without PyQt.
- UI delegates rules decisions to engine APIs.
- Bot and hint logic share a single AI decision pipeline.
- Test suite is layered, deterministic, and coverage-gated.
- CI and local workflows are aligned and reproducible.

## 5) Suggested Execution Order

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Phase 6

