# SPEC v1 — todo-list-cli MVP

## Summary

A command-line todo list. Scala 3, pure functional core, Cats Effect at the
edge. Tasks live in a single YAML file, `todo.yaml`, in the current working
directory. Four commands: `add`, `list`, `done`, `remove`.

## Goals

- A todo list usable entirely from the shell, with one YAML file as the
  source of truth.
- A pure functional core (task model, id assignment, YAML encode/decode)
  that is fully unit-testable without touching the filesystem.
- A thin Cats Effect shell that does I/O (read file, run command, write
  file, print) and nothing else.
- `just check` (scalafmt check, compile with `-Werror`, `sbt test`) is the
  only gate this spec needs to satisfy.

## Non-goals

- No color output, no table rendering, no Markdown formatting. Output is
  plain text lines.
- No config file, no flags to change the store path or format.
- No due dates, priorities, tags, projects, or sub-tasks.
- No concurrent access support (e.g. file locking). Single-user, single
  process at a time.
- No interactive/TUI mode. Every invocation is a single command that exits.

## CLI

Invocation shape: `todo <command> [args...]`.

### `todo add <description>`

- Appends a new task with status `pending` to `todo.yaml` in the current
  directory.
- `<description>` is the remaining arguments joined with a single space
  (so it does not need to be quoted for simple cases, but quoting is
  recommended if it contains flags-like tokens).
- A blank/whitespace-only description is a user error (see Errors).
- Assigns the task the next unused id (see Data model).
- Prints one line on success: `Added #<id>: <description>`.
- If `todo.yaml` does not exist yet, it is created.

### `todo list`

- Prints every task, one per line, in ascending id order:
  `[ ] #<id> <description>` for pending, `[x] #<id> <description>` for
  done.
- If there are no tasks, prints nothing (exit code is still 0).
- Plain text only: no color, no table borders/columns, no Markdown.

### `todo done <id>`

- Marks the task with the given id as done (idempotent: marking an
  already-done task done again succeeds and reprints the same
  confirmation).
- Prints: `Done #<id>: <description>`.
- Unknown id is a user error (see Errors).

### `todo remove <id>`

- Removes the task with the given id from the file entirely.
- Prints: `Removed #<id>: <description>`.
- Unknown id is a user error (see Errors).

## Data model

Pure core type (illustrative, not binding on naming):

```scala
enum Status:
  case Pending, Done

final case class Task(id: Int, description: String, status: Status)
```

- Ids are positive integers, assigned by taking `max(existing ids) + 1`
  (starting at `1` for the first task).
- Ids of removed tasks are never reused.
- Task order in the file is insertion order; `list` sorts by id for
  display, which is equivalent since ids are monotonically increasing.

## Storage format

- Single file, `todo.yaml`, resolved relative to the current working
  directory.
- Top-level shape:

```yaml
tasks:
  - id: 1
    description: Buy milk
    status: pending
  - id: 2
    description: Write spec
    status: done
```

- `status` is the literal string `pending` or `done`.
- If the file does not exist, it is treated as an empty task list (no
  tasks) for `list`, and created on the first `add`.
- If the file exists but fails to parse as this schema, that is a user
  error (see Errors) — the CLI must not silently truncate or overwrite a
  file it cannot understand.
- Writes are whole-file rewrites (read full list, transform, write full
  list back), consistent with "single-user, single process" in Non-goals.

## Errors

- User errors (bad id, unknown id, blank description, unparseable
  `todo.yaml`, missing/malformed command or arguments) print a one-line,
  plain-text message to stderr and exit with a non-zero status. No stack
  traces.
- Unexpected/internal errors (e.g. filesystem permission failure) also
  print a one-line message to stderr and exit non-zero, rather than
  crashing with a raw exception dump.
- Exit code `0` is reserved for success only.

## Architecture

- **Pure core**: task model, id assignment, command-to-transformation
  logic (`add`/`done`/`remove` as pure functions over `List[Task]`), YAML
  encoding/decoding as pure functions (`String <-> List[Task]`, or an
  equivalent pure error-returning form). No `IO`, no filesystem, no
  console access in this layer — fully testable with plain values.
- **Effectful shell**: parses `args: List[String]` into a command, uses
  Cats Effect (`IO`) to read `todo.yaml` if present, calls into the pure
  core, writes the file back when the command mutates state, and prints
  the result line to stdout (or the error line to stderr). This is the
  only layer allowed to touch the filesystem or console.

## Testing

- Pure core is covered by unit tests with no I/O: task transformations
  (`add`/`done`/`remove` semantics, id assignment, idempotent `done`) and
  YAML round-tripping (encode then decode is identity; decoding malformed
  YAML yields an error, not an exception).
- `just check` runs `scalafmtCheckAll` and `sbt test` and must pass with
  zero warnings (`-Werror`).

## Open questions / future versions

- Editing a task's description.
- Filtering `list` (e.g. only pending).
- Bulk operations (remove all done, etc.).

These are explicitly out of scope for v1 and are not implemented against
this spec.
