# SPEC v1: Todo List CLI MVP

A command-line todo list, written in Scala 3 as pure FP with Cats Effect. State lives
in a single YAML file, `todos.yaml`, in the current working directory, read and
written with `org.virtuslab::scala-yaml`.

## Settled decisions

- **Commands:** `add`, `list`, `done`, `remove`. No other commands are in scope for v1.
- **Storage:** one file, `todos.yaml`, in the current directory. No database, no config
  file, no alternate path.
- **Effects:** Cats Effect `IO` is the effect type for the program's entry point and for
  all file I/O; side effects are not performed outside of `IO`.
- **Tests:** ScalaTest is the test framework. `sbt test` and `just check` are the gate —
  a milestone isn't done until both are green.
- **Todo identity:** each todo has an auto-incrementing integer id, assigned on `add`,
  starting at 1. Ids are the argument `done` and `remove` take (e.g. `todo done 3`) and
  are never reused after a `remove`.
- **Output:** plain text only. No color, no table rendering, no Markdown formatting.
- **CI:** a workflow file that runs `just check` lands with the first milestone that
  has code (M1), not before.

## M1: Scala and sbt setup (Status: PENDING)

Project skeleton: `build.sbt` on Scala 3, dependencies (`cats-effect`,
`org.virtuslab::scala-yaml`, ScalaTest), scalafmt config, and CI.

**Acceptance Criteria:**
- `sbt compile` succeeds with `-Werror` and reports zero warnings.
- `sbt test` runs and exits 0 (a single trivial passing test is sufficient at this
  milestone).
- `sbt scalafmtCheckAll` passes on all committed sources.
- `just check` runs scalafmt-check, compile, and test, and exits 0.
- `build.sbt` declares Scala 3, `cats-effect`, `org.virtuslab::scala-yaml`, and
  ScalaTest as dependencies.
- A CI workflow file (e.g. `.github/workflows/check.yml`) exists and runs `just check`
  on push and pull request.

## M2: Cats hello world (Status: PENDING)

A minimal `IOApp` entry point, proving the Cats Effect wiring end-to-end before any
todo logic exists.

**Acceptance Criteria:**
- A `Main` object extends `IOApp` (or `IOApp.Simple`) whose `run` prints a fixed
  greeting to stdout as an `IO` action and exits 0.
- A ScalaTest test executes the program's `IO` action and asserts the captured stdout
  equals the greeting.
- `just check` still passes.

## M3: Create todos (Status: PENDING)

`add`, backed by `todos.yaml`.

**Acceptance Criteria:**
- `todo add <description>` appends a new todo to `todos.yaml` with the next
  auto-incrementing id and `done: false`, creating the file if it does not exist yet.
- `todo add` with an empty or blank-only description exits non-zero, prints an error
  naming the missing description, and leaves `todos.yaml` unchanged (or not created).
- Writing todos and reading them back via `org.virtuslab::scala-yaml` round-trips: the
  todos read after a write equal the todos written.

## M4: List todos (Status: PENDING)

`list`, displaying the todos in `todos.yaml` as a short plain-text list.

**Acceptance Criteria:**
- `todo list` when `todos.yaml` is missing or empty prints a plain-text message that
  there are no todos and exits 0.
- `todo list` with existing todos prints one line per todo, in ascending id order,
  showing id, done/not-done status, and description as plain text (no color, table, or
  Markdown).

## M5: Updates (Status: PENDING)

`done` and `remove`.

**Acceptance Criteria:**
- `todo done <id>` for an existing, not-done todo sets that todo's `done` to `true` in
  `todos.yaml` and leaves every other todo unchanged.
- `todo done <id>` for an already-done todo exits 0 and leaves `todos.yaml` unchanged
  (idempotent).
- `todo done <id>` for an id that does not exist exits non-zero, prints an error naming
  the missing id, and leaves `todos.yaml` unchanged.
- `todo remove <id>` for an existing id deletes that todo from `todos.yaml`; the
  remaining todos keep their original ids.
- `todo remove <id>` for an id that does not exist exits non-zero, prints an error
  naming the missing id, and leaves `todos.yaml` unchanged.
- After a `done` or `remove`, a subsequent `todo list` reflects the change.
