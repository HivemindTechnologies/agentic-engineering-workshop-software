# SPEC v1 — Todo List CLI MVP

A command-line todo list. Scala 3, pure FP with Cats and Cats Effect, one YAML file as the store.

## Settled decisions

- **Commands:** `add`, `list`, `done`, `remove`. No other commands in this spec.
- **Store:** a single file, `todos.yaml`, in the current working directory. Read and written with `org.virtuslab::scala-yaml`. No other YAML library.
- **Test gate:** `just check` (scalafmt, compile with `-Werror`, tests) is the only gate. The CI workflow file that runs it lands with the first code milestone (M1).
- **Output:** plain text only. No color, no table layout, no Markdown.
- **Todo identity:** each todo gets an integer id, assigned once when it is added, starting at 1 and increasing by 1 each time — never reused, even after a `remove`. The id is stored in `todos.yaml` alongside the todo and is what `done` and `remove` take as their argument.
- **Todo shape:** a todo has an `id` (integer), a `description` (non-empty text) and a `done` flag (boolean, `false` when added).

## M1: Scala and sbt setup (Status: PENDING)

An empty, buildable Scala 3 project. No application logic yet — this milestone proves the toolchain and the CI gate.

**Acceptance Criteria:**
- `build.sbt` targets a Scala 3 version and produces a runnable executable artifact.
- `sbt compile` succeeds with zero warnings and zero errors.
- `just check` succeeds (scalafmt check passes, compile runs with `-Werror`, the test task runs and reports zero failures).
- A CI workflow file exists (e.g. `.github/workflows/ci.yml`) that runs `just check` on push and on pull request, and it is present in the same commit as the rest of M1.

## M2: Cats hello world (Status: PENDING)

Wire up Cats and Cats Effect end to end with a minimal program, before any domain logic exists.

**Acceptance Criteria:**
- `build.sbt` adds `cats-core`, `cats-effect` and `munit-cats-effect` as dependencies.
- The application entry point is a Cats Effect `IOApp` that prints a fixed greeting line to stdout and exits with code 0.
- A pure function (not the `IOApp` itself) builds the greeting text using a Cats type class (e.g. `Show` or `Functor`), and a test exercises that pure function directly without running any `IO`.
- `just check` still passes.

## M3: Create and read todos (Status: PENDING)

The `add` and `list` commands, and the YAML store, following the pure-core rule: pure functions compute the new todo list, `IO` at the edge reads and writes `todos.yaml`.

**Acceptance Criteria:**
- A pure function takes the current list of todos, a description and the next id, and returns the list with the new todo appended; given an existing list and a description it returns a list one element longer, with the new todo's `done` set to `false`.
- Given an empty description (empty or all-whitespace), `add` fails fast: no file is written, the process exits non-zero, and the error message names the field.
- Running `add <description>` when `todos.yaml` does not exist creates it containing exactly the one new todo.
- Running `add <description>` when `todos.yaml` already contains todos appends the new todo without altering the existing ones, and assigns the next unused id.
- A pure function renders a list of todos as plain text lines, one todo per line, showing at least id, description and done state as plain characters (no ANSI color, no table borders, no Markdown syntax).
- Running `list` against a `todos.yaml` with N todos prints N lines in the order stored.
- Running `list` when `todos.yaml` does not exist, or exists with zero todos, prints a message and exits 0 without creating a file.
- Running `list` against a `todos.yaml` that is not valid YAML for the todo shape fails fast: the process exits non-zero and the error message says the file could not be read, without silently treating it as empty.
- `just check` still passes.

## M4: Updates (Status: PENDING)

The `done` and `remove` commands, reusing the read/write edge from M3.

**Acceptance Criteria:**
- A pure function takes the current list of todos and an id, and returns the list with the matching todo's `done` set to `true`, leaving every other todo unchanged.
- A pure function takes the current list of todos and an id, and returns the list with the matching todo removed, leaving the order of the remaining todos unchanged.
- Running `done <id>` for an id present in `todos.yaml` persists that todo with `done: true` and leaves all other todos byte-for-byte unchanged in content.
- Running `remove <id>` for an id present in `todos.yaml` persists the file without that todo, and the id is never reassigned to a later `add`.
- Running `done <id>` or `remove <id>` for an id not present in `todos.yaml` fails fast: the file is not written, the process exits non-zero, and the error message names the missing id.
- `just check` still passes.
