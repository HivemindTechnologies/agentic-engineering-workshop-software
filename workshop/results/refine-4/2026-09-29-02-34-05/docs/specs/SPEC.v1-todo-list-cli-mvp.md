# SPEC v1: Todo List CLI MVP

A command-line todo list. Scala 3, pure FP with Cats and Cats Effect, per
`docs/rules/WOW.md`. Four commands — `add`, `list`, `done`, `remove` — backed
by one file, `todos.yaml`, in the current directory, read and written with
`org.virtuslab::scala-yaml`. Output is plain text: no color, no table, no
Markdown. `just check` is the test gate.

## M1: Scala and sbt setup (Status: PENDING)

Project scaffold: Scala 3 on sbt, with Cats, Cats Effect, munit,
munit-cats-effect and munit-scalacheck, and org.virtuslab::scala-yaml on the
classpath. The CI workflow file lands here, with the first code milestone.

**Acceptance Criteria:**
- `sbt compile` succeeds with `-Werror` and zero warnings.
- `sbt scalafmtCheckAll` passes with no formatting violations.
- `sbt test` runs and passes with at least one munit test present in the tree.
- `just check` completes with exit code 0 and prints its scala/tests/warnings
  summary lines.
- A CI workflow file (e.g. `.github/workflows/check.yml`) runs `just check`
  on push and on pull request.

## M2: Cats hello world (Status: PENDING)

A minimal `IOApp` entry point proves effects run at the edge: a pure function
builds a greeting, and `IO` prints it once, at the boundary.

**Acceptance Criteria:**
- The entry point extends `IOApp` (or `IOApp.Simple`) from Cats Effect.
- Running the built CLI with no arguments prints a fixed greeting line to
  stdout and exits 0.
- A test calls the pure greeting-producing function directly and asserts its
  return value, without running the `IO` runtime.
- `just check` passes.

## M3: create and read todos (Status: PENDING)

The `add` and `list` commands, backed by `todos.yaml` in the current
directory. A todo has a unique id, assigned on creation, and non-empty text.
The store is read and written only through `org.virtuslab::scala-yaml`.

**Acceptance Criteria:**
- `add <text>` with non-blank text creates a todo with a fresh unique id, not
  marked done, and persists it to `todos.yaml`; the process exits 0.
- `add` with empty or blank text is rejected before any write: the process
  exits non-zero, the error message names the `text` field, and `todos.yaml`
  is unchanged (or not created, if it did not already exist).
- `list` against a directory with no `todos.yaml` prints no todos and exits
  0; it does not fail with an error.
- `list` prints one line per stored todo, each showing that todo's id, text,
  and whether it is done.
- `list` output contains no ANSI escape/color codes, no table-drawing
  characters (e.g. `|`, `+`, box-drawing glyphs), and no Markdown syntax
  (e.g. `#`, `*`, `` ` ``, `[ ]`-style links).
- A todo created by `add` is present in the output of a subsequent `list`
  (round-trip through the file).
- Two todos added in sequence receive different ids.

## M4: updates (Status: PENDING)

The `done` and `remove` commands, mutating todos by id.

**Acceptance Criteria:**
- `done <id>` for an id present in `todos.yaml` marks that todo done and
  persists the change; a subsequent `list` shows it as done and the process
  exits 0.
- `done <id>` for an id absent from `todos.yaml` exits non-zero, the error
  message names the given id, and `todos.yaml` is unchanged.
- `remove <id>` for an id present in `todos.yaml` deletes that todo and
  persists the change; a subsequent `list` no longer shows it, and the
  process exits 0.
- `remove <id>` for an id absent from `todos.yaml` exits non-zero, the error
  message names the given id, and `todos.yaml` is unchanged.
- `just check` passes with the full command set (`add`, `list`, `done`,
  `remove`) covered by tests.
