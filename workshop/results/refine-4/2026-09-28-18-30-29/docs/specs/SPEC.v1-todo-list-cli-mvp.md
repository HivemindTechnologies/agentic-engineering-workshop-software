# Todo List CLI — MVP (v1)

A command-line todo list. Scala 3, pure FP core with Cats and Cats Effect at the edge, one YAML file (`todo.yaml`, current directory) as the store. Ways of working: `docs/rules/WOW.md`. `just check` (scalafmt, compile with `-Werror`, tests) is the test gate for every milestone.

Commands: `add`, `list`, `done`, `remove`. Output is plain text — no color, no table, no Markdown.

## M1: Scala 3 and sbt project setup (Status: PENDING)

Bootstrap the build so `just check` has something to run against. This is the first code milestone, so the CI workflow file lands here too.

**Acceptance Criteria:**
- `sbt compile` succeeds with `-Werror` enabled (or equivalent strict `scalacOptions`) on a clean checkout.
- `sbt test` runs and passes at least one `munit` test; `munit`, `munit-cats-effect`, and `munit-scalacheck` are declared dependencies.
- `sbt scalafmtAll` leaves no unformatted files — `scalafmtCheckAll` passes.
- `just check` runs the scalafmt check, compile, and test steps in sequence and exits 0.
- A CI workflow file (e.g. `.github/workflows/*.yml`) exists and runs `just check` on push and pull request.
- The Scala version is a Scala 3.x release, pinned in `build.sbt`.

## M2: Cats hello world (Status: PENDING)

Prove the Cats Effect runtime wiring works before any domain logic exists.

**Acceptance Criteria:**
- The CLI entry point extends `IOApp` (or `IOApp.Simple`) and runs an `IO` action rather than a plain `def main`.
- Running the built app with no arguments prints one fixed greeting line to stdout and exits 0.
- A test asserts the `IO` action's output via `munit-cats-effect`, not just that `main` doesn't throw.
- No domain types (`Todo`, commands, YAML encode/decode) exist yet — this milestone is wiring only.

## M3: Create and read todos (Status: PENDING)

The first vertical slice: `add` writes a todo to `todo.yaml`, `list` reads it back. Establishes the pure-core / effectful-edge split — parsing, YAML encode/decode, and todo ordering are pure functions; only the file read and write run in `IO`.

**Acceptance Criteria:**
- `add <text>` appends a new todo with a unique id, the given text, and not-done status to `todo.yaml`; if the file doesn't exist yet, `add` creates it.
- `add` with empty or whitespace-only text is rejected: non-zero exit code, an error message naming the field, and no write to `todo.yaml`.
- `list` when `todo.yaml` doesn't exist prints an explicit "no todos" line and exits 0 — not an error.
- `list` prints each stored todo as plain text, one per line, showing at least its id, a done/not-done marker, and its text — no ANSI color, no table, no Markdown.
- `list` output order matches insertion order, checked by a test that adds several todos and lists them.
- The YAML decode/encode and the id-assignment/ordering logic are pure functions, tested without touching the filesystem; only top-level command wiring runs in `IO`.
- A round-trip test: encoding N todos and decoding them back reproduces the same N todos.

## M4: Updates (Status: PENDING)

`done` and `remove` both mutate an existing todo by id, sharing the "look up by id, fail if missing" shape.

**Acceptance Criteria:**
- `done <id>` marks the matching todo as done in `todo.yaml`, leaving its id and text unchanged; a following `list` shows it as done.
- `remove <id>` deletes the matching todo from `todo.yaml`; a following `list` no longer shows it.
- `done <id>` or `remove <id>` for an id absent from `todo.yaml` exits with a non-zero code and an error message naming the missing id; the file is left unchanged.
- Marking an already-done todo `done` again is a no-op and still exits 0.
- The "find by id" and "apply update" logic are pure functions, tested without filesystem access; only reading and writing `todo.yaml` runs in `IO`.
