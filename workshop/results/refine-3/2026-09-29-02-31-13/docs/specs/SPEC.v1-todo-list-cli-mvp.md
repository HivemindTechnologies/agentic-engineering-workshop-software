# SPEC.v1 — Todo list CLI MVP

A command-line todo list, Scala 3, pure functional core with Cats (and Cats Effect
for the IO boundary — see M2). `just check` (scalafmt, `sbt compile` with
`-Werror`, `sbt test`) is the test gate for every milestone.

## Settled decisions

- Commands: `add`, `list`, `done`, `remove`. No other commands in this spec.
- Storage: a single file, `todos.yaml`, in the current working directory,
  read and written with `org.virtuslab::scala-yaml`. No database, no other
  format.
- Output: plain text only. No ANSI color, no table layout, no Markdown
  syntax, in any command's output.
- CI: a workflow file that runs `just check` lands with the first milestone
  that adds Scala code (M1).

## M1: Scala and sbt setup (Status: PENDING)

Bare project skeleton: sbt with Scala 3, the project's dependencies
declared, and CI wired to the existing `just check` gate. No todo-list
behavior yet — that starts in M2.

Dependencies added: `org.typelevel::cats-core`, `org.typelevel::cats-effect`
(the IO boundary needed to keep command handlers pure — see M2),
`org.virtuslab::scala-yaml`, and `org.scalameta::munit` (test scope).

**Acceptance Criteria:**
- `build.sbt` sets `scalaVersion` to a 3.3.x (LTS) release.
- `build.sbt` declares `cats-core`, `cats-effect`, `scala-yaml` as compile
  dependencies and `munit` as a test dependency.
- `sbt compile` succeeds with no source files beyond a placeholder
  `Main.scala` containing an empty entry point.
- A CI workflow file (`.github/workflows/*.yml`) runs `just check` on push
  and on pull request.
- `just check` passes (scalafmt clean, compile with `-Werror`, at least one
  placeholder test green).

## M2: Cats hello world (Status: PENDING)

Wires the effect boundary the rest of the CLI builds on: an `IOApp` entry
point that runs one pure function and prints its result. Establishes the
pattern — pure logic in plain functions, `IO` only at the edge — before any
todo-list logic exists.

**Acceptance Criteria:**
- `Main` extends `cats.effect.IOApp` (or `IOApp.Simple`) and its `run`
  delegates to a pure, non-`IO` function to compute the greeting text.
- Running the built app (`sbt run`) prints the greeting to stdout and exits
  0.
- The pure greeting function has a `munit` test asserting its return value,
  independent of `IO` and of stdout.
- `just check` passes.

## M3: Create and read todos (Status: PENDING)

Implements `add` and `list` against `todos.yaml`, using `scala-yaml` for
encoding and decoding. A todo has an id, its text, and a `done` flag
(`false` for every todo created here — `done` stays unused until M4).

**Acceptance Criteria:**
- `add "<text>"` appends one new todo (fresh unique id, given text,
  `done = false`) to `todos.yaml` in the current directory, creating the
  file if it does not exist.
- `list` prints one line per todo, in the order stored, as plain text with
  no ANSI codes, no table characters, and no Markdown syntax (e.g. a
  `[ ]`/`[x]` marker followed by the id and text — exact wording is an
  implementation detail).
- `list` run against a directory with no `todos.yaml` prints no todo lines
  and exits 0 (it does not create the file or raise an error).
- A todo added by one process invocation is present in the output of a
  `list` run as a separate, later process invocation against the same
  directory (persistence across restarts, not just in-memory state).
- A round-trip test encodes a list of todos with `scala-yaml`, writes it,
  reads it back, and asserts the decoded list equals the original.
- `just check` passes.

## M4: Updates (Status: PENDING)

Implements `done` and `remove`, completing the command set.

**Acceptance Criteria:**
- `done <id>` sets the `done` flag to `true` for the todo with that id and
  persists the change to `todos.yaml`; a subsequent `list` shows that todo
  as done and every other todo unchanged, in the same order.
- `remove <id>` deletes the todo with that id from `todos.yaml`; a
  subsequent `list` no longer includes it, and every remaining todo is
  unchanged, in the same order.
- `done <id>` or `remove <id>` for an id not present in `todos.yaml` leaves
  the file's contents unchanged and exits with a non-zero status.
- `just check` passes.
