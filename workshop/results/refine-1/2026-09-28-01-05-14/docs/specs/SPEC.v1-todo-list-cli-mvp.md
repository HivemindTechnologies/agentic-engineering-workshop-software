# SPEC v1 — todo-list-cli MVP

| | |
|---|---|
| Status | Draft |
| Scope | v1 / MVP |
| Author | isaias.b@gmx.de |
| Date | 2026-09-28 |

## 1. Objective

A single-binary, single-file command-line todo list, written in Scala 3 with a
pure functional core and Cats Effect at the edge (per `CLAUDE.md`). The MVP
optimizes for three things, in order:

1. **Simple setup** — clone, `just check`, done. No config files, no daemons,
   no external services.
2. **CI-friendliness** — deterministic output, non-zero exit codes on error,
   color that degrades cleanly in non-TTY environments (CI logs, pipes).
3. **A well-factored test pyramid** — pure core logic tested without effects,
   a thin effectful shell tested with `IO`, and a handful of end-to-end CLI
   tests, all runnable through the one gate: `just check`.

The store is a single YAML file. Reading that file back out — either as
colored terminal output or as raw YAML — is a first-class, direct feature,
not an afterthought.

## 2. Goals

- Track tasks with a title and an open/done status in one YAML file per
  directory.
- `add`, `list`, `done`, `rm` as the core verbs.
- Colored, aligned, human-readable output by default.
- A `--format yaml` escape hatch on read commands that emits the same data
  as machine-parseable YAML, for piping into `yq`, other scripts, or CI logs.
- Configuration is exclusively CLI arguments. No environment variables, no
  config files, no XDG dirs, no `$HOME`-anything.
- The store file defaults to `./todo.yaml` (the process's current working
  directory), overridable with an explicit `--file` / `-f <path>` flag.
- Writing commands (`add`) create the store file if it is missing.
- Reading commands (`list`) fail loudly and specifically if the store file
  (default or explicit) does not exist, rather than silently returning empty
  output.
- CLI parse errors (missing arguments, unknown flags) produce a clear,
  single-purpose error message and a non-zero exit code — never a stack
  trace.

## 3. Non-goals (explicitly out of scope for v1)

- Due dates, reminders, priorities, tags, sub-tasks, projects/lists.
- Multi-user sync, locking, remote storage, or any network I/O.
- Config files or environment variables of any kind (see Goals — this is a
  hard constraint, not a placeholder for "later").
- Editing an existing task's title (delete + re-add covers it in v1).
- Importing arbitrary/foreign YAML into the store (the store's own YAML is
  the only YAML it reads back).
- An interactive/TUI mode.
- Id reuse after deletion.

These are candidates for a v2 spec, not silently-dropped requirements.

## 4. CLI surface

Global option, valid on every subcommand:

| Flag | Default | Meaning |
|---|---|---|
| `--file, -f <path>` | `./todo.yaml` | Path to the store file. |
| `--color <auto\|always\|never>` | `auto` | Color mode for rendered output. `auto` colors only when stdout is a TTY. |
| `--help, -h` | — | Usage for the command. |
| `--version` | — | Print the CLI version and exit. |

Subcommands:

| Command | Args | Effect |
|---|---|---|
| `todo add <title>` | required `<title>` | Appends a new open task. Creates the store file if absent. |
| `todo list [--status <open\|done\|all>] [--format <rich\|yaml>]` | — | Lists tasks. `--status` defaults to `open`. `--format` defaults to `rich`. Fails if the store file does not exist. |
| `todo done <id>` | required `<id>` | Marks the task `<id>` as done, stamping `completedAt`. Fails if the store file or the id does not exist. |
| `todo rm <id>` | required `<id>` | Removes task `<id>`. Fails if the store file or the id does not exist. |

No subcommand implies `list` with defaults; running `todo` alone prints
top-level help instead (explicit is better than a surprising default view).

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | User error: missing store file, unknown task id, malformed store YAML, invalid argument value. |
| `2` | CLI usage error: missing/unknown flag or argument (raised by the argument parser before any command logic runs). |

Every non-zero exit writes a single-line, human-readable message to
`stderr` — no stack traces escape `main`.

## 5. Configuration

CLI arguments only, per Goals. Concretely, this means:

- No `TODO_FILE`, `NO_COLOR`, `TODO_*` or any other environment variable is
  ever read.
- Color mode is resolved from `--color` plus a TTY check on `stdout`
  (`java.io.Console` / `System.console() != null`, or an equivalent isatty
  check) — never from `NO_COLOR` or `CLICOLOR` env vars, since that would
  reintroduce environment-based configuration through the back door.
- There is no config file discovery (no `.todorc`, no `~/.config/todo`). The
  only path resolution rule is: `--file` if given, else `./todo.yaml`.

## 6. Store format

One YAML document per store file, schema versioned so the file is
self-describing without needing external config:

```yaml
version: 1
nextId: 3
tasks:
  - id: 1
    title: "Write the v1 spec"
    status: done
    createdAt: "2026-09-28T09:00:00Z"
    completedAt: "2026-09-28T10:15:00Z"
  - id: 2
    title: "Implement the YAML codec"
    status: open
    createdAt: "2026-09-28T09:05:00Z"
    completedAt: null
```

- `nextId` is an explicit counter, not derived by scanning `tasks` for the
  max id. This keeps id assignment pure, deterministic, and independent of
  deletions (ids are never reused within a store's lifetime).
- Timestamps are UTC ISO-8601 (`Instant.toString`).
- `status` is the two-value enum `open | done`; `completedAt` is `null`
  until the task is marked done.
- Writes are atomic: render the new document to a sibling temp file in the
  same directory, then move it over the target path, so a crash mid-write
  never leaves a truncated or partially-written store.

## 7. Output rendering

### Rich (default)

```
$ todo list --status all
  1  ✓  Write the v1 spec            done     2026-09-28
  2  ○  Implement the YAML codec     open     2026-09-28
```

- `✓` done rows render in green, `○` open rows in yellow, the id column
  dimmed. Column widths are computed from the widest cell so output stays
  aligned regardless of title length.
- Colors are ANSI SGR codes applied only when the resolved color mode
  (§5) is "on"; with color off, the same aligned columns render with plain
  glyphs, so `--color never` output stays diffable and CI-log-safe.

### YAML (`--format yaml`)

```
$ todo list --status all --format yaml
tasks:
  - id: 1
    title: "Write the v1 spec"
    status: done
    createdAt: "2026-09-28T09:00:00Z"
    completedAt: "2026-09-28T10:15:00Z"
  - id: 2
    title: "Implement the YAML codec"
    status: open
    createdAt: "2026-09-28T09:05:00Z"
    completedAt: null
```

This is the filtered *view* (respecting `--status`), not necessarily the
full store — it omits `version`/`nextId` since a view is not a store. It
uses the same field names and shapes as the store schema so it composes
directly with `yq`/`grep`/other YAML tooling without any translation step.
`--format yaml` never applies color, regardless of `--color`.

## 8. Error handling

| Situation | Command(s) | Behavior |
|---|---|---|
| Store file missing | `list`, `done`, `rm` | `stderr`: `` Error: no todo file at <path>. Run `todo add <title>` to create one, or pass --file <path>. `` Exit `1`. |
| Store file missing | `add` | Created transparently; no message, task is added. |
| Store file exists but fails to parse | any | `stderr`: `` Error: <path> is not a valid todo store: <parser detail>. `` Exit `1`. |
| Unknown task id | `done`, `rm` | `stderr`: `` Error: no task with id <id> in <path>. `` Exit `1`. |
| Missing/invalid argument (e.g. `todo done` with no id, non-numeric id) | any | Parser-generated usage error to `stderr`, exit `2`. |

## 9. Architecture

Matches `CLAUDE.md`'s "pure functional core, Cats Effect at the edge":

```
core/    — pure, effect-free: Task, TodoList, id assignment, status
           transitions, YAML codec (encode/decode), rich-text rendering.
           Tested with plain munit, no IO involved.
effects/ — Cats Effect shell: read/write the store file (atomic write via
           temp file + move), TTY detection, stdout/stderr writes.
           Tested with munit-cats-effect against real temp directories.
cli/     — argument parsing (global --file/--color plus subcommands),
           wiring parsed args to core + effects, exit code mapping.
           Tested end-to-end by invoking the parsed program against a
           temp directory and asserting on stdout/stderr/exit code.
```

Suggested (swappable) dependencies, chosen to keep setup simple:

- `decline` — CLI argument parsing, cats-friendly, no extra runtime.
- `circe` + `circe-yaml` — store codec.
- `cats-effect` (`IOApp`) — the app entry point and file I/O.
- `fansi` or hand-rolled ANSI codes — rich-text coloring; deliberately not
  a heavier terminal UI library, since v1 needs neither cursor control nor
  interactivity.

Core types are immutable case classes; every operation (add/complete/remove)
is a pure function `TodoList => TodoList` (or `Either[DomainError, TodoList]`
for id-not-found cases), independent of how the list was loaded or will be
persisted.

## 10. Testing strategy

- **Core (`core/`)**: plain `munit` tests, no effects — codec round-trips
  (encode then decode is identity), id assignment/increment, status
  transitions, rich-text rendering against fixed inputs (golden strings).
- **Effects (`effects/`)**: `munit-cats-effect` tests against a real
  filesystem, scoped to a fresh temp directory per test (`Files.createTempDirectory`
  wrapped as a `Resource`, cleaned up on completion) — never the process's
  actual working directory, and never shared state across tests. Covers:
  missing-file error path, atomic-write-survives-partial-failure, TTY vs
  non-TTY color resolution.
- **CLI (`cli/`)**: black-box tests that build argv, run the parsed program
  against a temp directory via an explicit `--file`, and assert on stdout,
  stderr, and exit code — covering the full command table in §4 and the
  full error table in §8.
- Property-based tests (`munit-scalacheck`) for the codec and id-assignment
  logic, since both are pure and total.

All of the above run under `sbt test`, which is one of the three checks
`just check` runs (alongside `scalafmtCheckAll` and `-Werror` compilation) —
no separate CI-only test command.

## 11. CI integration

A single job is enough for v1:

```yaml
# .github/workflows/ci.yml (sketch)
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: coursier/setup-action@v1
        with: { jvm: temurin:17 }
      - run: just check
```

Since color defaults to `auto` and CI runners are non-TTY, CI logs stay
plain-glyph by default with no flags or env vars needed on the CI side —
directly exercising the same "no environment configuration" path used
locally.

## 12. Suggested milestones (one per commit, per project convention)

1. Project scaffold: `build.sbt`, module layout (`core`/`effects`/`cli`),
   CI workflow, `just check` green on an empty skeleton.
2. `core`: `Task`/`TodoList` model + YAML codec, fully unit-tested.
3. `effects`: store read/write (including atomic write, missing-file
   handling), tested against temp directories.
4. `cli`: argument parsing skeleton (global flags, `--help`/`--version`),
   no subcommand logic yet.
5. `add` end-to-end, including auto-create-on-write.
6. `list` end-to-end: rich rendering + `--format yaml`, `--status` filter.
7. `done` / `rm` end-to-end.
8. Error-path hardening across §8's table; exit-code audit.
9. README usage docs + `--help` text polish; tag v1.

## 13. Open questions for v2

- Multiple lists/projects per directory vs. one file per directory.
- Editing a task's title in place.
- Whether YAML output should ever represent the *whole* store (including
  `version`/`nextId`) for a future `export`/backup use case.
