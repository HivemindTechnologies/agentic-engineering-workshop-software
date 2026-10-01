# v1: Todo List CLI — MVP

A command-line todo list. Scala 3, pure functional core, Cats Effect at the edge. One YAML file, `todo.yaml`, in the current directory, is the store. `just check` (scalafmt, compile with `-Werror`, tests) is the test gate.

Settled decisions, binding for every milestone below:

- Commands: `add`, `list`, `done`, `remove`. No other commands in this spec.
- Store: a single file, `todo.yaml`, in the process's current working directory. No other location, no config file to override it.
- Output is plain text: no color/ANSI codes, no table borders, no Markdown syntax (`**`, `#`, `|`, etc.).
- The core (domain types, store read/write, command logic) is pure: no `var`, no mutable collections, no thrown exceptions crossing module boundaries. Failures are values (e.g. `Either`, or a failed `IO`) that the CLI edge turns into a stderr message and a non-zero exit code — never a raw stack trace.
- The CI workflow file lands with the first code milestone (M1), not before.

## M1: Project scaffold and CI (Status: PENDING)

An sbt project that builds, and a CI workflow that runs the gate.

**Acceptance Criteria:**
- `sbt compile` succeeds with Scala 3 and `-Werror` enabled, with Cats Effect and a YAML library declared as dependencies in `build.sbt`.
- `just check` succeeds on a clean checkout (scalafmt check, compile with `-Werror`, test run all pass) — including on a build with zero application tests, using at least one placeholder test that exercises the build.
- A CI workflow file (e.g. `.github/workflows/ci.yml`) exists and its job runs `just check`.
- Running the CLI with no arguments, or with an unrecognized first argument, prints a usage line to stderr listing `add`, `list`, `done`, and `remove`, and exits with a non-zero code.

## M2: Domain model and YAML store (Status: PENDING)

The pure data types and the read/write of `todo.yaml`, with no command wired to them yet.

**Acceptance Criteria:**
- A `Todo` type holds an integer `id`, a non-empty `description`, and a `done` boolean; the module defining it contains no `var` and no mutable collections.
- Loading from a `todo.yaml` that does not exist yields an empty list of todos, not an error.
- Loading a `todo.yaml` that is malformed YAML yields a stderr message naming the problem and a non-zero exit, not an unhandled exception or stack trace.
- Saving a non-empty list of todos and then loading it back yields the same todos, in the same order (round-trip test).
- The on-disk shape is a top-level `todos` list, each entry carrying `id`, `description`, and `done` keys.

## M3: `add` command (Status: PENDING)

**Acceptance Criteria:**
- `add "<description>"` appends a new todo with `done = false` and persists it to `todo.yaml`; the new id is one greater than the current maximum id, or `1` when the store is empty.
- An empty or whitespace-only description is rejected: a stderr message names "description", the command exits non-zero, and `todo.yaml` is left unchanged (or absent, if it did not exist before).
- Two successive `add` calls produce two todos with distinct, increasing ids, both present in `todo.yaml` afterwards.

## M4: `list` command (Status: PENDING)

**Acceptance Criteria:**
- `list` prints one line per todo, ascending by id, formatted as `<id> [ ] <description>` for a pending todo and `<id> [x] <description>` for a done one.
- `list` against an empty or absent store prints exactly `No todos yet.` and exits 0.
- `list` output contains no ANSI escape codes, no `|` table borders, and no Markdown syntax (`**`, `#`, backticks).

## M5: `done` command (Status: PENDING)

**Acceptance Criteria:**
- `done <id>` sets that todo's `done` to `true` and persists the change; a subsequent `list` shows it marked `[x]`.
- `done <id>` for an id not present in the store prints a stderr message naming that id, exits non-zero, and leaves `todo.yaml` unchanged.
- `done <id>` for a todo that is already done exits 0 and leaves the store's content unchanged (idempotent, not an error).

## M6: `remove` command (Status: PENDING)

**Acceptance Criteria:**
- `remove <id>` deletes that todo from `todo.yaml`; the ids of the remaining todos are unchanged.
- `remove <id>` for an id not present in the store prints a stderr message naming that id, exits non-zero, and leaves `todo.yaml` unchanged.
- Removing the last remaining todo leaves the store such that a subsequent `list` prints `No todos yet.`.
