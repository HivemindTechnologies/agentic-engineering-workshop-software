# SPEC v1 — todo-list-cli MVP

Status: draft
Scope: first shippable milestone set. Grown spec-first, one milestone per commit (see `docs/PROMPTS.md` for the prompt that produced this spec).

## 1. Goals

- A command-line todo list, installable and runnable with a trivial setup (`sbt compile`, one binary, one file store).
- Pure functional core (domain model + operations + rendering are pure), Cats Effect only at the edges (file I/O, console, process exit).
- CI-friendly by construction: deterministic output, explicit exit codes, no hidden state, `just check` as the single gate (scalafmt, `-Werror` compile, tests).
- Rich, colored, well-structured terminal output for humans; a raw YAML output mode for scripts and other tools to consume directly.
- The on-disk store *is* the interchange format: a single human-readable YAML file, editable by hand or by other tools.

## 2. Non-goals (v1)

- No env var configuration, no config files, no XDG dirs, no `NO_COLOR` support (see §6).
- No due dates, priorities, tags, subtasks, or recurring todos. One string of text plus done/undone state.
- No multi-list / multi-project support. One store file per invocation.
- No concurrent-writer safety (locking, CRDTs). Single local user, single process at a time.
- No remote sync, no database backend.
- No interactive TUI (curses-style). Every command is a single non-interactive invocation.

These are candidates for a v2 spec, not this one.

## 3. Configuration model

Configuration is **CLI arguments only**. No environment variables are read for behavior (not even conventional ones like `NO_COLOR` or `TODO_FILE`), and there is no config file. This is a deliberate constraint, not an oversight — it keeps behavior fully determined by the invocation, which matters for CI reproducibility and for reasoning about the pure core.

Every command accepts:

| Flag | Default | Meaning |
|---|---|---|
| `-f`, `--file <path>` | `./todo.yaml` in the current working directory | Path to the store file |
| `--color <always\|auto\|never>` | `auto` | Controls ANSI color output; `auto` = colorize iff stdout is a TTY |
| `--format <text\|yaml>` | `text` | Output rendering for read commands (see §5) |
| `-h`, `--help` | — | Standard help, per command and top-level |

## 4. Store file and its lifecycle

The store is one YAML file. Default path: `todo.yaml` in the current directory. Overridable per-invocation with `--file`.

### 4.1 Create-on-write, fail-on-read

- **Write commands** (`add`, `done`, `undone`, `rm`) create the store file (with the resolved path — default or `--file`) if it does not already exist, seeded with an empty list, then apply the change. This is the *only* implicit file creation in the tool.
- **Read commands** (`list`, `show`) never create the file. If the resolved path does not exist, the command fails with a non-zero exit and a clear error naming the path it looked for and suggesting `todo add` or `--file`. An empty list and a missing file are different, meaningful states, and we don't collapse them by silently vivifying an empty store on read.
- **Missing/invalid parameters** (e.g. `add` with no text, `done` with no id, an id that doesn't parse as an integer, `--format` given an unrecognized value) are also reads-side style failures: reject with a usage error before touching the filesystem at all. Never guess.

### 4.2 File format

```yaml
version: 1
items:
  - id: 1
    text: "Write the v1 spec"
    done: true
    createdAt: "2026-09-28T09:00:00Z"
    completedAt: "2026-09-28T10:15:00Z"
  - id: 2
    text: "Wire up CI"
    done: false
    createdAt: "2026-09-28T09:05:00Z"
    completedAt: null
```

- `version` is a schema tag for forward migration; v1 readers reject files with an unrecognized `version`.
- `id` is a positive integer, assigned sequentially, never reused within a file (deleting item 2 does not make a future item reuse id 2). Stored explicitly rather than implied by array position, so hand-edits that reorder lines don't change identity.
- Timestamps are ISO-8601 UTC (`Instant`), produced by the Cats Effect `Clock` at the edge; the pure core never calls `now()` itself.
- The file is meant to be hand-editable: field order and this exact shape are part of the contract, not an implementation detail. Round-tripping (`decode andThen encode`) is byte-for-byte stable on file we ourselves wrote, and merely order/whitespace-normalizing on hand-edited files.

## 5. Commands

```
todo add <text...>            Add a new item, marked not done. Creates the store if missing.
todo done <id>                Mark an item done. Sets completedAt to now.
todo undone <id>              Mark an item not done. Clears completedAt.
todo rm <id>                  Remove an item permanently.
todo list [--all|--done|--pending]   List items (default: --all). Fails if store is missing.
todo show <id>                Show a single item in detail. Fails if store or id is missing.
```

- `<id>` refers to the item's stored `id` field, not its position in the list.
- `list` filters: `--pending` (default complement of done), `--done`, `--all`. Exactly one may be given; default is `--all`.
- Every command supports `--format` and `--color` as in §3; `add`/`done`/`undone`/`rm` print the affected item as confirmation, in the same `--format`.

### 5.1 Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Usage error (bad/missing arguments, caught before any I/O) |
| 2 | Store file not found on a read, or referenced `id` not found |
| 3 | Store file exists but fails to parse (corrupt YAML, unknown `version`) |

Stable exit codes are load-bearing for CI usage of this tool (e.g. `todo list --pending --format yaml | ...` in a script).

## 6. Output

Two orthogonal axes: `--format` (structure) and `--color` (styling), both flags, no env vars.

### 6.1 `--format text` (default): rich, colored, human-oriented

- A table: id, a checkbox-style marker (`[x]` / `[ ]`), text, relative or absolute created/completed time.
- Color (when enabled): done items dimmed with a green marker; pending items with a yellow/plain marker; errors and warnings in red, always to stderr.
- `--color auto` detects a TTY on stdout via Cats Effect / `System.console()`; redirection to a file or pipe disables color automatically without any flag. `--color always` / `--color never` override detection explicitly. We do **not** honor `NO_COLOR` or any other env var, per §3 — use `--color never`.
- Text-format rendering is still deterministic given fixed inputs (no wall-clock-dependent relative-time strings like "2 minutes ago" in v1 — print absolute timestamps — so golden-file tests are stable).

### 6.2 `--format yaml`: direct interchange

- Emits the same YAML shape as the store file (§4.2), or a single-item document for `show`, so the CLI can be piped straight into other YAML-aware tooling, or into `todo --file - `-style composition in a later version. No color codes are ever mixed into `--format yaml` output, regardless of `--color`.

## 7. Architecture

Pure-core / effectful-shell split, as required by `CLAUDE.md`:

```
src/main/scala/todo/
  domain/       Item, TodoList, pure operations (add, complete, uncomplete, remove, filter) — no IO, no Clock
  codec/        circe YAML Codec/Decoder for TodoList <-> the v1 file schema; pure
  render/       pure String renderers: rich-text table + ANSI styling, and YAML passthrough
  cli/          decline Opts parsing: raw args -> a sealed Command ADT; pure, no IO
  app/          interpreter: Command ADT -> IO, using a FileStore capability (trait) for load/save
  Main.scala    IOApp.Simple entry point: wires real file IO + Clock + Console into app/
```

- `FileStore[F[_]]` (load/save/exists) is the one effectful capability read commands and write commands depend on; production wiring uses `Sync`/`IO` over `java.nio.file`, tests use an in-memory `Ref`-backed instance. This is what makes the CLI's decision logic (create-on-write, fail-on-read, id resolution, filtering) testable without touching a real filesystem.
- The domain layer has no dependency on `cats.effect` at all — only `cats.core` (if even that; plain Scala case classes/ADTs suffice for v1).

## 8. Dependencies

- Scala 3, `sbt`.
- `cats-core`, `cats-effect` (`IOApp`).
- `decline` + `decline-effect` for CLI parsing (composable `Opts`, matches the pure-core philosophy — parsing itself is pure, only the run is effectful).
- `circe-yaml` (+ `circe-core`/`circe-generic` or manual codecs) for the store format.
- `munit` + `munit-cats-effect` for tests; `scalacheck`/`munit-scalacheck` for property tests (YAML round-trip, id-uniqueness invariants).
- `scalafmt` (already gated by `just check`).

No dependency is added for ANSI coloring beyond hand-rolled escape codes (the palette is tiny: dim, green, yellow, red) — not worth a library for v1.

## 9. Testing strategy

Matches `just check` (`scalafmt`, compile with `-Werror`, `sbt test`) as the single CI gate.

- **Domain unit tests** (`domain/`): pure functions, no effects — add/complete/uncomplete/remove/filter, id assignment/never-reused invariant, edge cases (empty list, unknown id, filtering empty results).
- **Codec property tests**: `decode(encode(list)) == list` for generated `TodoList`s (ScalaCheck); fixed hand-written YAML fixtures decode to expected domain values; unknown `version` is rejected; malformed YAML surfaces as a typed decode error, not an exception.
- **Render golden tests**: fixed `TodoList` + fixed `Instant` -> exact expected string, for both `--format text` (color on and off) and `--format yaml`. No wall-clock or locale dependence, so these are byte-stable in CI.
- **CLI parsing unit tests**: raw `List[String]` args -> expected `Command` ADT or a parse failure, for every command and flag combination in §5, including invalid ids/formats/colors (exit code 1 territory).
- **Interpreter integration tests**: full `Command -> IO[ExitCode]` using the in-memory `FileStore`, asserting the create-on-write / fail-on-read behavior from §4.1, and correct exit codes from §5.1 — all without real disk I/O.
- **End-to-end smoke test** (small number, not exhaustive): actually invoke `Main` (or run the assembled jar) against a temp directory, to catch wiring mistakes the in-memory tests can't (real file permissions, real Clock, real `System.console()` detection under `--color auto`).

## 10. CI

- GitHub Actions workflow running `just check` on push and PR (single job: checkout, set up JDK + sbt, run `just check`). This is the only required check for v1 — no matrix, no separate lint job, since `just check` already bundles format-check + `-Werror` compile + tests.
- The build must fail on any compiler warning (`-Werror`), which is enforced by `just check` already listed in `CLAUDE.md`; this spec adds no new gate, only the command needed to run it.

## 11. Milestones (one commit each)

1. Project scaffold: `build.sbt`, dependency versions, empty `Main.scala` that prints usage; `just check` passes.
2. `domain`: `Item`, `TodoList`, pure operations + unit tests.
3. `codec`: YAML schema + encode/decode + property/fixture tests.
4. `cli`: `decline` parsing for all commands/flags -> `Command` ADT + parsing tests.
5. `app`: `FileStore` capability + interpreter with create-on-write/fail-on-read semantics + in-memory-backed integration tests.
6. `render`: rich colored text renderer + YAML passthrough renderer + golden tests.
7. Wire `Main.scala` end-to-end (real `FileStore`, `Clock`, `Console`); add the smoke test.
8. `.github/workflows/ci.yml` running `just check`.

## 12. Open questions for v2

- Should `list`/`show` support `--format json` alongside `yaml`, for tools that don't want a YAML parser?
- Multiple store files / a `--file -` stdin/stdout convention for piping between `todo` invocations?
- Bulk operations (`todo done 1 2 3`, or a filter expression instead of a single id)?
