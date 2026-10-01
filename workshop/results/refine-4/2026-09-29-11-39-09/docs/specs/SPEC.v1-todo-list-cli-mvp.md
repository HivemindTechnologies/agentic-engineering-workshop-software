# SPEC v1: Todo List CLI MVP

A command-line todo list. Scala 3, pure FP with Cats and Cats Effect, ways of
working per [`docs/rules/WOW.md`](../rules/WOW.md). `just check` is the test
gate for every milestone.

Settled for this version:

- Commands: `add`, `list`, `done`, `remove`.
- Store: a single `todos.yaml` in the current directory, read and written
  with `org.virtuslab::scala-yaml` — no other YAML library.
- The CI workflow file lands with M1, the first code milestone, and runs
  `just check`.
- Output is plain text: no color, no table, no Markdown.

## M1: Scala and sbt setup (Status: PENDING)

Bootstrap the sbt project on Scala 3 with the dependencies and checks from
WOW.md, and land the CI workflow that runs `just check`.

**Acceptance Criteria:**

- `sbt compile` succeeds with `-Werror` enabled and reports zero warnings on
  a clean checkout.
- `build.sbt` targets Scala 3 and declares `cats-core`, `cats-effect`,
  `munit`, `munit-cats-effect`, `munit-scalacheck`, and
  `org.virtuslab::scala-yaml` as the only YAML dependency.
- `.scalafmt.conf` exists, and `sbt scalafmtCheckAll` passes on the initial
  source tree.
- `sbt test` runs and reports at least one passing munit test, proving the
  test runner is wired up.
- `just check` runs `scalafmtCheckAll` and `test` and exits `0` on the
  initial project.
- A CI workflow file (e.g. `.github/workflows/ci.yml`) exists and its job
  runs `just check` on push.

## M2: Cats hello world (Status: PENDING)

Wire a Cats Effect `IOApp` as the CLI entry point and prove the pure-core /
effectful-edge split with a trivial greeting, before any todo logic exists.

**Acceptance Criteria:**

- A pure function computes the greeting text from an input with no side
  effects; a munit test named for the behaviour it checks asserts its
  output for at least one input.
- The `IOApp` entry point calls that pure function and performs the only
  side effect — printing — through `IO`; running the built CLI with no
  arguments prints the greeting to stdout and exits `0`.
- A `munit-cats-effect` test runs the `IO` action and asserts on its result
  without printing to the real console and without mocks (e.g. the action
  returns the line to print rather than writing to stdout directly).

## M3: Create and read todos (Status: PENDING)

Implement `add` and `list` against `todos.yaml`: the domain model and the
YAML round-trip via `org.virtuslab::scala-yaml`.

A todo has an `id` (positive integer, assigned by the store, not the user),
a `description` (non-blank text) and a `done` flag. Ids are assigned by
incrementing the current maximum id in the file; they are never reused
within a run.

**Acceptance Criteria:**

- A `Todo`'s description is built only through a smart constructor that
  rejects an empty or blank string, returning a `Left` whose message names
  the `description` field.
- `add "<description>"` on a directory with no `todos.yaml` creates the
  file containing exactly one todo: id `1`, `done: false`, and the given
  description.
- `add "<description>"` on an existing `todos.yaml` appends a new todo
  whose id is one greater than the current maximum id, leaving the
  existing todos unchanged.
- `add` with a blank or empty description is rejected before the file is
  written; `todos.yaml` is left unchanged (or absent).
- `list` on a directory with no `todos.yaml`, or with an empty list, prints
  `No todos.` and exits `0`.
- `list` prints one line per todo in ascending id order, formatted as
  `<id> [ ] <description>` for an open todo and `<id> [x] <description>`
  for a done todo — no color codes, no table borders, no Markdown syntax.
- Writing a list of todos to `todos.yaml` and reading it back reproduces
  the same ids, descriptions and done flags, checked as a property over
  generated todo lists (`munit-scalacheck`).
- A `todos.yaml` that fails to parse (malformed YAML) makes the command
  fail fast with a non-zero exit code and an error message, rather than
  silently continuing with an empty list.

## M4: Updates (Status: PENDING)

Implement `done` and `remove` against `todos.yaml`.

**Acceptance Criteria:**

- `done <id>` sets that todo's `done` to `true` in `todos.yaml` and leaves
  every other todo unchanged.
- `done <id>` for an id absent from `todos.yaml` fails fast with a
  non-zero exit code and a message naming the missing id; the file is
  left unchanged.
- `remove <id>` deletes that todo from `todos.yaml`; the remaining todos
  keep their existing ids.
- `remove <id>` for an id absent from `todos.yaml` fails fast with a
  non-zero exit code and a message naming the missing id; the file is
  left unchanged.
- `done` and `remove` on a missing `todos.yaml` fail fast with a non-zero
  exit code and an error message, rather than creating a file or raising
  an unhandled exception.
