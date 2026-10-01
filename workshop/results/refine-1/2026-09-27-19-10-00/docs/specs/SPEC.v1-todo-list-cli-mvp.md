# SPEC v1 — Todo List CLI MVP

Status: draft
Scope: first shippable milestone of the CLI; supersedes nothing (greenfield)

## 1. Objective

A command-line todo list, Scala 3, pure functional core with Cats Effect confined to the
edges. Three things matter more than feature breadth for v1:

1. **Simple setup** — clone, `just check`, done. No external services, no daemons, no DB.
2. **CI-integrable** — the whole test suite is deterministic, hermetic (temp dirs only,
   no network, no shared state), and fast enough to run on every push.
3. **Well-set-up test infrastructure** — pure core is property-tested, effectful shell is
   tested with real (temp-file) IO, renderers are golden-tested. New milestones add tests
   in the same shape, no infra invented per-feature.

Secondary but binding requirements:

- Output is colored and structured in a terminal, and degrades to plain text when not
  attached to a TTY or when `NO_COLOR` is set.
- The store is a single YAML file, directly human-editable — no proprietary format, no
  binary state.
- The same in-memory representation can be rendered as terminal ANSI output or as rich
  text (Markdown) for interfacing outside the terminal (piping into docs, chat, etc.).

## 2. Non-goals (v1)

Explicitly deferred, so scope creep has somewhere to be written down instead of into code:

- Multi-user / multi-device sync, remote or DB-backed storage.
- Recurring tasks, reminders, notifications.
- Interactive TUI (curses-style); v1 is argument-in, text-out.
- In-place editing via `$EDITOR`.
- Undo/history, soft-delete/trash.
- Concurrent access to the store file (single-user, single-process assumption).

## 3. Architecture

Four layers, each with a distinct testing strategy. Dependencies point one direction only
(`cli` → `render` + `store` → `domain`; nothing depends back on `cli`).

```
domain   pure model + pure logic, zero IO, zero cats-effect          (property tests)
store    YAML codec + file read/write algebra, cats-effect Sync/IO   (temp-file + fake tests)
render   StyledDoc AST + renderers (Ansi / Markdown / Plain)         (golden tests)
cli      arg parsing (decline) + program wiring, cats-effect IO      (munit-cats-effect)
```

### 3.1 `domain`

- `Todo`, `TodoId`, `Status` (`Open`, `Done`), `Priority` (`Low`, `Medium`, `High`).
- All operations (`filter`, `sortByPriority`, `markDone`, …) are total, pure functions
  over immutable case classes/enums. No exceptions; invalid input is a value
  (`Either`/`Option`), never a thrown error.
- No knowledge of YAML, ANSI, or the file system. This layer is the thing that stays
  correct while everything around it changes.

### 3.2 `store`

- `TodoStore[F[_]]` algebra: `load: F[Either[StoreError, List[Todo]]]`,
  `save(List[Todo]): F[Either[StoreError, Unit]]`.
- `FileTodoStore` interprets the algebra over `cats.effect.IO` using a single YAML file.
- YAML encoding/decoding via typeclass-driven codecs (circe + circe-yaml), not manual
  string building. Parse failures become a typed `StoreError`, never a runtime exception
  crossing into `cli`.
- Schema carries a top-level `version` field from day one (see §5) so hand-edits and
  future migrations don't silently corrupt data.

### 3.3 `render`

- A small `StyledDoc` AST (`Plain`, `Styled(text, style)`, `Line`, `Concat`) — output is
  built as data, not by concatenating ANSI escape strings inline.
- Renderers are pure functions `StyledDoc => String`:
  - `AnsiRenderer` — colored terminal output.
  - `MarkdownRenderer` — rich text for piping/export (`--format md`).
  - `PlainRenderer` — no styling, used when `NO_COLOR` is set or stdout isn't a TTY.
- Because renderers are pure `String`-in/`String`-out functions over the same AST, they're
  tested with golden fixtures — no terminal emulation needed.

### 3.4 `cli`

- Argument parsing via `decline` (composable, functional, testable without touching
  `IO.unsafeRunSync` in unit tests — a `Command[CliOp]` parses to a value first).
- `Main` composes: parse args → `TodoStore.load` → apply pure `domain` op → render via
  `render` → `TodoStore.save` (if mutating) → write to console.
- This is the only layer allowed to touch `System.exit`, `Console`, or the real
  filesystem path resolution.

## 4. CLI surface (v1)

```
todo add <title> [--priority low|medium|high] [--tag <tag>]...
todo list [--status open|done|all] [--priority <p>] [--tag <tag>] [--format table|md|yaml] [--plain]
todo done <id>
todo remove <id>
todo show <id>
```

- Default store path: `./todos.yaml`, overridable via `--file <path>` or `TODO_FILE` env
  var — resolved once, in `cli`, never inferred deeper in the stack.
- Exit codes: `0` success, `1` user error (bad args, not found), `2` store error
  (unreadable/corrupt YAML) — distinct codes so CI scripts can branch on failure kind.
- `--plain` (or `NO_COLOR=1`, or non-TTY stdout) forces `PlainRenderer`.

## 5. YAML store format

```yaml
version: 1
todos:
  - id: 3fbf1a2c
    title: "Write the SPEC"
    status: done
    priority: high
    tags: [docs, planning]
    createdAt: "2026-09-27T10:00:00Z"
    completedAt: "2026-09-27T14:30:00Z"
  - id: 9a01e7d4
    title: "Wire FileTodoStore"
    status: open
    priority: medium
    tags: []
    createdAt: "2026-09-27T10:05:00Z"
    completedAt: null
```

- Field order and key names are stable — this is the "interface directly with YAML"
  contract: a user (or another tool) can hand-edit this file between CLI runs.
- Unknown top-level keys are preserved-or-rejected explicitly (decide in M2; default
  leaning: reject with a clear `StoreError`, since silent data loss on round-trip is
  worse than a loud failure).
- `id` is a short stable identifier (e.g. first 8 hex chars of a UUID), not a mutable
  array index — hand-edits and concurrent `list` output must keep referring to the same
  todo.

## 6. Dependencies

Kept deliberately small — "simple setup" is a requirement, not an aspiration.

| Purpose            | Library                              |
|---------------------|--------------------------------------|
| Effects             | `org.typelevel::cats-effect`         |
| Core FP             | `org.typelevel::cats-core`           |
| CLI parsing         | `com.monovore::decline`              |
| CLI + IO glue       | `com.monovore::decline-effect`       |
| YAML codec          | `io.circe::circe-yaml`, `circe-core`, `circe-generic` (semiauto) |
| Unit/integration tests | `org.scalameta::munit`, `org.typelevel::munit-cats-effect-3` |
| Property tests      | `org.scalameta::munit-scalacheck`    |

No custom ANSI library dependency — `AnsiRenderer` emits standard SGR escape codes
directly from `StyledDoc`; it's a small enough surface (bold/color/reset) that owning it
avoids an extra dependency for something the golden tests pin down anyway.

## 7. Testing strategy

Mirrors the layering in §3, matching the existing `just check` gate (scalafmt, `-Werror`
compile, tests — no separate coverage/lint tool introduced in v1):

- **`domain`**: `munit-scalacheck` property tests. Example properties: sorting by
  priority is stable and total; `markDone` is idempotent; every generated `Todo` survives
  a `toYaml → fromYaml` round-trip unchanged.
- **`store`**: two tiers —
  - Fast, no-IO tests against the codec directly (`Json`/YAML string ⇄ `Todo`), covering
    malformed input and version mismatches.
  - `munit-cats-effect` integration tests against real temp files (`Files.createTempFile`
    cleaned up in `FunFixture`) — proves the `Sync`/`IO` wiring, not just the codec.
- **`render`**: pure `String`-equality tests against fixed `StyledDoc` inputs, one fixture
  set per renderer (Ansi/Markdown/Plain), stored as small literal expected strings —
  golden files only if fixtures grow unwieldy, not by default.
- **`cli`**: `decline`'s parser is tested by feeding `Array[String]` into
  `Command#parse` and asserting on the parsed `CliOp`, without running `IO`. End-to-end
  wiring gets a handful of `munit-cats-effect` tests that run `Main`'s program against a
  temp store file and assert on stdout + resulting file contents.
- No test depends on real time, real network, or shared global state — a requirement for
  CI determinism, not just a nicety.

## 8. CI integration

- `just check` remains the single gate referenced in `CLAUDE.md` — CI runs exactly that,
  nothing bespoke to the pipeline.
- GitHub Actions: one job, Temurin JDK (LTS), sbt/coursier cache keyed on
  `build.sbt`/`project/*.sbt`, then `just check`. No matrix in v1 — add JDK/OS matrix only
  if a real portability need shows up.
- Because `store` tests use temp files and `cli` tests use `decline` parsing (not a real
  subprocess), the suite needs no sandboxing beyond what CI already gives a job — no
  Docker-in-CI, no fixture servers.

## 9. Milestones (one per commit, per project convention)

1. **M0 — Skeleton**: `build.sbt`, Scala 3 LTS, empty `Main` compiling under `-Werror`,
   GitHub Actions workflow running `just check`. Green CI on a no-op program is the goal.
2. **M1 — Domain**: `Todo`/`Status`/`Priority` + pure ops, scalacheck property tests.
3. **M2 — Store**: YAML codec (round-trip tested) + `FileTodoStore` over temp files,
   versioned schema, typed `StoreError`.
4. **M3 — CLI wiring**: `decline` command parsing + `add`/`list`/`done`/`remove`/`show`
   against the store, parser unit tests + a first end-to-end `munit-cats-effect` test.
5. **M4 — Terminal rendering**: `StyledDoc` + `AnsiRenderer`, `NO_COLOR`/TTY detection,
   `PlainRenderer` fallback, golden-style tests per renderer.
6. **M5 — Rich text export**: `MarkdownRenderer` + `--format md|yaml|table`, tests
   covering the same fixtures as M4 for parity across renderers.
7. **M6 — Polish**: exit codes finalized, error messages reviewed for clarity, `README`
   usage section, CI badge.

## 10. Open questions (resolve before or during the milestone noted)

- **M2**: reject-vs-preserve unknown YAML keys on load — leaning reject; confirm before
  writing the codec.
- **M3**: should `remove` require confirmation, or is `id`-only removal fine for a
  single-user local tool? Leaning no confirmation (scriptability > guard-rail) but worth
  a deliberate call, not a default.
- **M4**: exact color mapping (priority → color, status → color/icon) — needs a decision
  but is low-risk to change later since it's isolated in `AnsiRenderer`.
