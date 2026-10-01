# SPEC v1 — todo-list-cli MVP

## Summary

A command-line todo list. Scala 3, pure functional core, Cats Effect confined to
the edge (CLI entry point and file I/O). State lives in a single YAML file,
`todo.yaml`, in the current working directory. Four commands: `add`, `list`,
`done`, `remove`. Plain text output — no color, no tables, no Markdown.

## Goals

- Add, list, complete, and remove todo items from the command line.
- Persist state as YAML the user can read and edit by hand.
- Keep domain logic pure and effects isolated, so the core is testable without
  touching the filesystem.
- `just check` is the one gate: scalafmt, compile with `-Werror`, tests.

## Non-goals (v1)

- No color, no table rendering, no Markdown output.
- No due dates, priorities, tags, or subtasks.
- No config file, no environment variables, no multiple lists.
- No concurrent access support (no file locking).
- No editing item text after creation.

## Data model

```scala
final case class Todo(id: Int, text: String, done: Boolean)
```

- `id`: positive integer, assigned by the app, stable for the lifetime of the
  item, never reused after removal.
- `text`: non-empty, single-line (newlines stripped/rejected on input).
- `done`: defaults to `false` on creation.

## Storage

- File: `todo.yaml` in the current working directory.
- Format: a YAML sequence of items at the document root.

```yaml
- id: 1
  text: Buy milk
  done: false
- id: 2
  text: Write spec
  done: true
```

- If `todo.yaml` does not exist, it is treated as an empty list; it is created
  on the first write (`add`, `done`, or `remove` that changes state).
- If `todo.yaml` exists but fails to parse, the command fails with a non-zero
  exit code and a plain-text error on stderr. No partial writes.
- Writes are whole-file: read, modify in memory, serialize, overwrite. No
  append-only log, no locking.
- Next `id` is `(max existing id) + 1`, or `1` for an empty list.

## Commands

All output is plain text to stdout; errors go to stderr. No color, no tables,
no Markdown formatting anywhere in output.

### `todo add <text>`

- Appends a new item with `done: false` and the next available id.
- `<text>` is required and must be non-empty after trimming; otherwise exit
  non-zero with an error message and no file write.
- On success, prints the created item, e.g.:

```
Added #3: Write spec
```

### `todo list`

- Prints all items in ascending `id` order, one per line.
- Format: `[<x or space>] #<id> <text>` where `x` marks done items.

```
[ ] #1 Buy milk
[x] #2 Write spec
```

- Empty list prints a single line: `No todos.`

### `todo done <id>`

- Marks the item with the given id as done.
- `<id>` must be a positive integer and must reference an existing item;
  otherwise exit non-zero with an error and no file write.
- Marking an already-done item done again succeeds (idempotent) and reprints
  the item.
- On success, prints the updated item, e.g.:

```
Done #2: Write spec
```

### `todo remove <id>`

- Removes the item with the given id.
- `<id>` must be a positive integer and must reference an existing item;
  otherwise exit non-zero with an error and no file write.
- Removing an id does not renumber remaining items.
- On success, prints:

```
Removed #2: Write spec
```

## CLI behavior

- No arguments, or an unrecognized command: print usage to stderr and exit
  non-zero.
- Usage text lists the four commands and their argument shape, plain text only.
- Exit codes: `0` on success, non-zero on any validation or I/O error.

## Architecture

- **Pure core**: domain model (`Todo`), the operations on `List[Todo]` for
  add/list/done/remove, argument parsing/validation, and YAML
  encoding/decoding of the domain model — all pure functions, no `IO`.
- **Effectful shell**: a thin Cats Effect `IO`-based entry point that reads
  `todo.yaml`, calls into the pure core, writes `todo.yaml` back if changed,
  and prints output. This is the only layer that touches the filesystem or
  stdout/stderr.
- The pure core must be usable and testable without constructing an `IO` or
  touching disk.

## Testing

- Unit tests for the pure core: add/list/done/remove semantics, id assignment,
  validation failures (empty text, non-existent id, non-positive id).
- Unit tests for YAML encode/decode round-tripping `List[Todo]`, and for
  parse-failure handling.
- `just check` runs scalafmt (check mode), compiles with `-Werror`, and runs
  the full test suite; this is the single required gate before a change is
  considered done.

## Acceptance criteria

- Running `add`, `list`, `done`, `remove` in sequence against a fresh
  directory produces the outputs and `todo.yaml` contents described above.
- All commands validate input and fail closed (non-zero exit, no write) on
  bad input.
- No output anywhere contains ANSI color codes, table borders, or Markdown
  syntax.
- `just check` passes.
