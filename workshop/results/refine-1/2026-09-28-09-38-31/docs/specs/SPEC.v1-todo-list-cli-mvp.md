# SPEC.v1 — todo-list-cli MVP

## Summary

A command-line todo list. Scala 3, pure functional core, Cats Effect at the
edge, one YAML file as the store. Four commands: `add`, `list`, `done`,
`remove`.

## Goals

- Manage a flat list of todos from the shell.
- Keep domain logic pure; push all I/O (file read/write, console, exit codes)
  to the edge.
- Persist to a single YAML file, `todo.yaml`, in the current working
  directory.

## Non-goals

- No color output, no table rendering, no Markdown in any output.
- No due dates, priorities, tags, projects, or recurring todos.
- No config file, no support for a store path other than `./todo.yaml`.
- No concurrent access / file locking guarantees — single user, single
  process at a time.
- No sub-tasks or nested lists.

## Store

Single YAML file, `todo.yaml`, in the current working directory.

```yaml
todos:
  - id: 1
    text: "Buy milk"
    done: false
  - id: 2
    text: "Write spec"
    done: true
```

- `id`: positive integer, unique within the file, assigned by `add` as
  `max(existing ids) + 1` (`1` if the list is empty). Ids are never reused
  after a `remove`.
- `text`: non-empty string, the todo's description.
- `done`: boolean, defaults to `false` on creation.

If `todo.yaml` does not exist, it is treated as an empty list (`todos: []`)
for `list`, and is created on the first `add`. A missing file is not an
error.

## Commands

### `todo add <text>`

Appends a new todo with `done: false` and the next available id. Prints the
new todo's id on success.

- `<text>` is required and must be non-empty after trimming; otherwise exit
  with an error and non-zero status.

### `todo list`

Prints all todos, one per line, in ascending id order. Plain text only — no
color, no table layout, no Markdown syntax.

Format: `<status> <id> <text>`, where `<status>` is `[ ]` for not done and
`[x]` for done.

```
[ ] 1 Buy milk
[x] 2 Write spec
```

If there are no todos, prints nothing (empty output, exit code 0).

### `todo done <id>`

Marks the todo with the given id as `done: true`. No-op if it is already
done. Errors with non-zero exit status if no todo with that id exists.

### `todo remove <id>`

Deletes the todo with the given id from the store. Errors with non-zero
exit status if no todo with that id exists.

## Errors

All error messages are printed to stderr as plain text (no color, no
Markdown). Known error cases:

- Unknown command or missing/invalid arguments (e.g. non-numeric id).
- `add` with empty text.
- `done` / `remove` referencing an id that does not exist.
- `todo.yaml` present but not valid YAML matching the store schema.

Any of the above results in a non-zero exit code and no mutation of
`todo.yaml`.

## Architecture

- **Domain core (pure)**: `Todo` model and list operations (`add`, `markDone`,
  `remove`, `list`) as pure functions over `List[Todo]`, no effects.
- **YAML codec (pure)**: encode/decode between the domain model and the
  `todo.yaml` schema above; decoding failures are represented as values, not
  exceptions.
- **Edge (Cats Effect `IO`)**: CLI argument parsing, reading/writing
  `todo.yaml`, printing to stdout/stderr, and setting the process exit code.
  This is the only layer allowed to perform I/O.

## Testing & checks

`just check` is the single gate: scalafmt, compile with `-Werror`, and the
test suite. It must pass before any change is considered done.

- Domain core and YAML codec: unit tests, pure, no filesystem access.
- CLI/edge layer: tests exercise `add`/`list`/`done`/`remove` end-to-end
  against a temporary `todo.yaml`, asserting on file contents, stdout, and
  exit codes.
