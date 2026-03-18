# Feature Plan: Online Ranked Multiplayer + Spectator + Replay System

## 1) Feature Definition

Implement a full online multiplayer stack for QuoridorX with:

- Real-time 1v1 online matches
- Matchmaking (casual and ranked queue)
- Elo-style rating updates
- Spectator mode (read-only live board view)
- Server-authored replay files for post-game playback

This is intentionally high-complexity and touches networking, protocol design, deterministic game state, backend orchestration, client synchronization, and observability.

## 2) Why This Feature Is Valuable

- Expands game scope from local-only to global online play
- Increases replayability and retention through ranked ladder
- Enables asynchronous growth loops (share replay, watch others)
- Creates a foundation for tournaments and anti-cheat tooling

## 3) Non-Goals (Initial Version)

- No voice chat
- No social graph/friend list
- No cross-platform mobile client
- No rollback netcode (turn-based protocol avoids this)

## 4) Current-State Constraints in This Repo

Existing app is a local PyQt6 game with in-process turn management and AI:

- UI/game loop in `src/game_window.py` and `src/classes/grid_scene.py`
- Turn/state logic in `src/classes/turn_manager.py` and `src/classes/game_state.py`
- Rule validation via helpers in `src/helpers/`

Online mode requires extracting deterministic game rules from UI-driven control flow so a backend can be source-of-truth.

## 5) Target Architecture

### 5.1 Components

- **Game Client (existing app + online module)**
  - Adds websocket session manager
  - Sends player intents (move/wall/ready/forfeit)
  - Renders server-authoritative state deltas

- **Gateway/API service**
  - Auth/session bootstrap
  - Matchmaking queue endpoints
  - Replay metadata and profile endpoints

- **Realtime Match Service**
  - Manages match rooms over websocket
  - Validates and applies turns with deterministic engine
  - Publishes events to players + spectators

- **Game Rules Engine (shared library or server module)**
  - Pure deterministic validators:
    - legal moves
    - legal wall placements
    - win/draw conditions
  - Produces normalized state snapshots and hash

- **Data Store**
  - PostgreSQL for players/matches/ratings/replays metadata
  - Object store (or compressed DB blob) for replay event streams

### 5.2 Trust Model

- Server is authoritative for all game outcomes.
- Client sends intents only; never final state.
- Every turn is validated server-side before commit.

## 6) Protocol and State Model

### 6.1 Session Lifecycle

1. Client authenticates and obtains short-lived session token.
2. Client joins queue (`casual` or `ranked`).
3. Matchmaker forms pair and allocates `match_id`.
4. Clients connect websocket to match room.
5. Server emits `match_start` with initial state and clocks.
6. Per turn:
   - active player sends intent
   - server validates intent + turn ownership
   - server commits event and broadcasts delta
7. On game end:
   - result persisted
   - ranking update performed
   - replay finalized

### 6.2 Event-Driven Contracts

All packets include:

- `type` (event name)
- `match_id`
- `seq` (monotonic server sequence)
- `ts` (server timestamp)

Core events:

- `match_start`
- `state_sync`
- `intent_ack`
- `intent_reject` (with reason code)
- `turn_applied`
- `clock_update`
- `match_end`
- `spectator_joined`
- `replay_ready`

### 6.3 Deterministic State

State payload minimally includes:

- board size
- player positions
- walls placed
- blocked roads representation
- wall counts
- current turn
- move history tail for repetition detection
- terminal status
- state hash (e.g., SHA-256 canonical JSON)

Canonical serialization is required to guarantee replay consistency and debugging reliability.

## 7) Game Engine Refactor Plan (Core Technical Dependency)

### 7.1 Extract pure domain engine

Create new module `src/domain/` with no PyQt dependency:

- `engine_state.py` - immutable or controlled-mutation game state
- `engine_rules.py` - move/wall legality, draw/win checks
- `engine_apply.py` - apply action -> next state (+ event)
- `engine_serialize.py` - canonical state/event serialization

### 7.2 Adapter layers

- Existing UI continues rendering but consumes domain state.
- `TurnManager` becomes orchestration wrapper for local mode.
- Bot logic evaluates domain state objects directly.

### 7.3 Parity verification

Build golden tests comparing current behavior and new domain engine over predefined move scripts.

## 8) Backend Data Model (Conceptual)

### 8.1 Tables

- `players(id, display_name, created_at, rating, rating_deviation, status)`
- `match_queue_entries(id, player_id, queue_type, enqueued_at)`
- `matches(id, mode, created_at, started_at, ended_at, winner_id, result_type, version)`
- `match_participants(match_id, player_id, color, rating_before, rating_after)`
- `match_events(match_id, seq, actor_id, event_type, payload_json, state_hash, created_at)`
- `replays(id, match_id, storage_uri, checksum, duration_ms, created_at)`

### 8.2 Idempotency + consistency

- Unique `(match_id, seq)` index
- Transaction per accepted turn:
  1) validate current sequence
  2) append event
  3) update current state pointer/hash

## 9) Matchmaking and Ranking

### 9.1 Matchmaking strategy

- Separate pools: `casual`, `ranked`
- Window expansion over queue time:
  - initially tight rating delta
  - relax constraints every N seconds

### 9.2 Rating updates

- Start with Elo baseline:
  - configurable K-factor by games played
  - anti-farming guardrails (same-opponent diminishing impact)
- Future upgrade path: Glicko-2

## 10) Spectator and Replay

### 10.1 Spectator mode

- Spectators receive read-only event stream
- No intent channel permitted
- Optional delay buffer (e.g., +5 seconds) for anti-stream-sniping

### 10.2 Replay generation

- Persist normalized event log + initial seed/state
- Replay player reconstructs state by deterministic event application
- UI controls: play/pause/step/seek

## 11) Reliability, Security, and Anti-Cheat

- Authoritative server validation for every turn
- Sequence number validation to reject stale/reordered intents
- Match-level rate limiting (prevent websocket flooding)
- Signed session tokens with short expiration
- Structured reason codes for rejected actions
- Audit trail: state hash per applied turn

## 12) Observability

Metrics:

- queue wait time p50/p95
- match completion rate
- reconnect frequency
- intent rejection rate by reason
- turn processing latency

Logging/Tracing:

- correlation id per match
- structured event logs with `match_id`, `seq`, `actor_id`
- distributed trace around validate->apply->persist->broadcast

## 13) Testing Strategy

### 13.1 Domain engine

- Unit tests for:
  - movement and jump rules
  - wall legality and forbidden-wall logic
  - win/draw detection
- Property/fuzz tests:
  - random legal action sequences never produce unreachable goals

### 13.2 Protocol

- Contract tests for websocket schemas
- Out-of-order packet simulation
- Duplicate intent/idempotency checks

### 13.3 Integration/E2E

- two clients + server full match flow
- reconnect mid-match and state resync
- spectator join mid-game
- replay fidelity: replay final hash equals match final hash

## 14) Delivery Milestones

### Milestone 1: Domain decoupling (2-3 weeks)

- Extract pure game engine from UI
- Add golden parity tests
- Keep local mode behavior unchanged

### Milestone 2: Realtime backend MVP (3-4 weeks)

- Match service + websocket protocol
- Casual queue only
- Authoritative move validation

### Milestone 3: Ranked and persistence (2-3 weeks)

- Elo updates + profile endpoints
- Match history + replay storage

### Milestone 4: Spectator + replay UI (2-3 weeks)

- live spectator read-only mode
- replay browser and playback controls

### Milestone 5: Hardening (2 weeks)

- load tests
- anti-abuse controls
- observability dashboards and alerting

## 15) Risks and Mitigations

- **Risk:** nondeterminism between client/server engines  
  **Mitigation:** single shared engine codepath and state hash checks.

- **Risk:** protocol drift across versions  
  **Mitigation:** versioned message schema and compatibility gates.

- **Risk:** complex wall validation performance under scale  
  **Mitigation:** memoization, precomputed adjacency maps, profiling budgets.

- **Risk:** poor matchmaking in low-population hours  
  **Mitigation:** dynamic widening constraints and optional bot backfill in casual.

## 16) Suggested Initial File/Module Additions

- `src/domain/engine_state.py`
- `src/domain/engine_rules.py`
- `src/domain/engine_apply.py`
- `src/network/client_session.py`
- `src/network/protocol.py`
- `src/replay/replay_player.py`
- `docs/protocol/match-events.md`
- `docs/architecture/online-mode.md`

## 17) Definition of Done (v1)

- Players can complete stable online casual and ranked matches.
- All moves/walls are server-validated.
- Ratings update and persist after ranked games.
- Spectators can watch live matches without affecting gameplay.
- Replay playback reproduces final state hash exactly.
- Monitoring dashboards show healthy queue and match SLOs.
