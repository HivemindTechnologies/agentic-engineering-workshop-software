# SPEC v1: Todo List CLI MVP

A command-line todo list. Scala 3, pure functional core, Cats Effect at the edge. One YAML file, `todo.yaml`, in the current directory, is the store. `just check` is the test gate.

## Settled decisions

- Commands: `add`, `list`, `done`, `remove`. No other commands in this spec.
- Store: a single file, `todo.yaml`, in the directory the CLI is run from. No config for the path.
- Output: plain text only. No color, no table layout, no Markdown.
- `just check` (scalafmt, compile with `-Werror`, tests) is the one gate. A CI workflow file runs it on every push and pull request; the file lands with the first code milestone.

## M1: Scala and sbt setup (Status: PENDING)

Establish the build and the test gate before any domain code exists, so every later milestone lands on green.

**Acceptance Criteria:**
- `sbt compile` succeeds on Scala 3 on a fresh checkout.
- `sbt test` runs and reports at least one passing test, proving the test harness executes.
- `sbt scalafmtCheckAll` passes against a committed scalafmt config.
- `just check` runs scalafmt check, compile with `-Werror`, and test, in that order, and exits zero.
- A CI workflow file runs `just check` on every push and on every pull request.

## M2: Cats hello world (Status: PENDING)

Prove the pure-core-at-the-edge shape with the smallest possible program, before any todo domain exists: a pure function returns the value, `IOApp` performs the one print.

**Acceptance Criteria:**
- A pure function with no side effects returns the greeting text as a value; a test asserts on that returned value directly, without constructing or running an `IO`.
- Running the built application prints that greeting once via `IOApp` and exits zero.
- `just check` stays green.

## M3: Create and read todos (Status: PENDING)

The `add` and `list` commands, and the YAML store they share. Illegal todos are unrepresentable: a todo always has an id and a non-empty description.

**Acceptance Criteria:**
- A `Todo` value has an id, a description, and a done flag that defaults to false.
- Constructing a `Todo` with an empty (or all-whitespace) description is rejected through the return type (`Either`/`Option`), not by throwing.
- `add <description>` with a non-empty description appends one new todo to `todo.yaml` with a fresh, distinct id and done set to false.
- `add` with an empty description is rejected before any write to `todo.yaml`, and the CLI reports which field was invalid.
- `list` prints every todo in `todo.yaml` as plain text, one per line, each line showing id, description, and done state; no table, no color, no Markdown.
- `list` when `todo.yaml` does not exist prints that there are no todos, without error.
- Writing a set of todos to `todo.yaml` and reading them back yields the same ids, descriptions, and done flags.
- `list` against a `todo.yaml` that fails to parse as the expected shape fails fast with an error message naming the file, instead of crashing with a raw stack trace or silently returning an empty list.

## M4: Updates (Status: PENDING)

The `done` and `remove` commands, updating a todo already on disk.

**Acceptance Criteria:**
- `done <id>` for an id present in `todo.yaml` sets that todo's done flag to true and persists it; every other todo in the file is unchanged.
- `done <id>` for an id not present in `todo.yaml` fails fast with a message naming the id, and leaves the file unchanged.
- `remove <id>` for an id present in `todo.yaml` deletes that todo from the file; every other todo is unchanged.
- `remove <id>` for an id not present in `todo.yaml` fails fast with a message naming the id, and leaves the file unchanged.
- `list` run after `done` or `remove` reflects the persisted change, read fresh from `todo.yaml`.
