# SPEC v1: todo-list-cli MVP

A command-line todo list, Scala 3, pure functional core with Cats (Effect) at the edge.

## Settled choices

- Commands: `add`, `list`, `done`, `remove`. No other commands in this spec.
- Store: a single YAML file, `todo.yaml`, in the current working directory. No database, no config file, no alternate path.
- `just check` (scalafmt check, compile with `-Werror`, tests) is the one test gate. A CI workflow file that runs `just check` lands with the first code milestone (M1).
- Output is plain text: no color, no table layout, no Markdown formatting — in `list` output, error messages, and anywhere else the CLI prints.

## M1: Scala and sbt setup (Status: PENDING)

Project scaffolding only: no todo logic yet. Establishes the build and the CI gate every later milestone runs against.

**Acceptance Criteria:**
- `sbt compile` succeeds on a clean checkout.
- `build.sbt` sets `scalaVersion` to a 3.x release.
- `.scalafmt.conf` exists and `sbt scalafmtCheckAll` runs against real source (not a no-op on an empty tree).
- `just check` completes successfully (scalafmt check, `-Werror` compile, test run) with zero source files or a trivial placeholder test.
- A CI workflow file (e.g. `.github/workflows/ci.yml`) exists and invokes `just check` on push and pull request.

## M2: Cats hello world (Status: PENDING)

Wires a pure-FP entry point: an `IOApp` that runs a greeting program built from `cats-effect`, proving the effect-at-the-edge shape before any todo logic exists.

**Acceptance Criteria:**
- `cats-effect` is a declared dependency in `build.sbt`.
- The application's `main` extends `cats.effect.IOApp` (or `IOApp.Simple`); the program is an `IO` value, not a bare `println` inside `main`.
- The greeting text is produced by a pure function (`String => String` or `() => String`) separate from the `IO` that prints it.
- A test calls the pure greeting function directly and asserts its return value, without capturing stdout.
- `just check` passes with this test included.

## M3: Create and read todos (Status: PENDING)

Introduces the `Todo` domain model and the `add` and `list` commands, backed by `todo.yaml`.

**Acceptance Criteria:**
- A `Todo` case class exists with at least an id, a title, and a done flag, constructed only through validated, total constructors (no thrown exceptions for bad input).
- `add <title>` with a non-empty title appends a new todo with a fresh, unique id to `todo.yaml`, creating the file if it does not exist.
- `add` with an empty or blank title is rejected: the todo is not written, and the command reports which field was invalid.
- `list` with no `todo.yaml` present prints an empty list (no error, no stack trace).
- `list` prints each stored todo's id, title, and done status as plain text — no color, no table, no Markdown.
- A round-trip test encodes a set of `Todo` values to YAML, decodes them back, and asserts the result equals the original set.
- A test running `add "buy milk"` then `list` shows `buy milk` in the `list` output.

## M4: Updates (Status: PENDING)

Adds the `done` and `remove` commands, mutating existing entries in `todo.yaml`.

**Acceptance Criteria:**
- `done <id>` for an id present in `todo.yaml` sets that todo's done flag and leaves every other stored field unchanged.
- `done <id>` applied twice to the same id succeeds both times and leaves the todo done (idempotent, no error, no duplicate entry).
- `remove <id>` for an id present in `todo.yaml` deletes that entry and leaves every other stored todo unchanged.
- `done <id>` or `remove <id>` for an id absent from the store makes no change to `todo.yaml`, reports the missing id by value, exits non-zero, and prints no stack trace.
- `list` after `done <id>` renders that todo's done status distinctly from a not-done todo, in plain text only.
- A test covers `add` → `done` → `list` showing the done state, and a separate test covers `add` → `remove` → `list` showing the todo absent.
