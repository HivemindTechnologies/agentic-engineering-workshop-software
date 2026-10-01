# SPEC v1 — todo-list-cli MVP

## Summary

A command-line todo list. Scala 3, pure functional core, Cats Effect confined to
the edges (CLI argument parsing, file I/O, process exit). One YAML file,
`todo.yaml`, in the current working directory, is the entire store. Output is
plain text: no color, no tables, no Markdown.

## Goals

- `add`, `list`, `done`, `remove` commands, nothing else.
- A pure, referentially transparent core: parsing args, validating input, and
  deciding what to do are all plain functions on immutable data. Cats Effect
  (`IO`) only wraps reading/writing `todo.yaml` and printing to stdout/stderr.
- A single YAML file is the store. No database, no config file, no daemon.
- `just check` (scalafmt check, `-Werror` compile, tests) is the one gate for
  correctness.

## Non-goals

- No color output, no box-drawing/table rendering, no Markdown formatting.
- No editing of task text, no due dates, no priorities, no tags, no
  sub-tasks, no search/filter flags.
- No concurrent access support (no file locking). The CLI is invoked once per
  process and exits.
- No config file, no `--store-path` flag, no environment variable overrides.
  The store is always `./todo.yaml`.

## Store format

`todo.yaml` lives in the current working directory. It is created on the
first `add` if missing. It is a YAML sequence of tasks:

```yaml
- id: 1
  text: "Buy milk"
  done: false
- id: 2
  text: "Write spec"
  done: true
```

- `id` — positive integer, assigned by the CLI, stable for the lifetime of
  the task, never reused after `remove`.
- `text` — the task description, exactly as given to `add`, no trimming
  beyond leading/trailing whitespace.
- `done` — boolean, defaults to `false` on creation.

The next `id` is `1 + max(existing ids)`, or `1` if the file is empty or
absent. IDs are not reassigned when a task is removed, so gaps are expected
and normal.

An empty or absent `todo.yaml` is treated as zero tasks, not an error.

## Commands

All commands operate on `./todo.yaml`. All commands print plain text lines
to stdout on success; errors go to stderr. No output uses color, tables, or
Markdown syntax.

### `add <text>`

Appends a new task with `done: false` and the next available id. `<text>` is
the remaining command-line arguments joined with a single space, so it does
not need to be quoted by the caller unless it contains characters the shell
would otherwise interpret.

- Empty or whitespace-only text is rejected with an error; no task is
  written.
- On success, prints the created task, e.g. `Added #3: Buy milk`.

### `list`

Prints every task, one per line, in ascending id order, in the form:

```text
[ ] 1  Buy milk
[x] 2  Write spec
```

- `[ ]` for not done, `[x]` for done.
- If there are no tasks, prints `No tasks.`.

### `done <id>`

Marks the task with the given id as done. Idempotent: marking an
already-done task done again succeeds silently and reports the task as
already done.

- If `<id>` does not exist, prints an error to stderr and exits non-zero.
- On success, prints `Done #<id>: <text>`.

### `remove <id>`

Deletes the task with the given id from the store.

- If `<id>` does not exist, prints an error to stderr and exits non-zero.
- On success, prints `Removed #<id>: <text>`.

## CLI behavior

- No arguments, or an unrecognized command, prints usage to stderr and exits
  non-zero.
- `<id>` arguments that are not positive integers are rejected with an error
  on stderr; exit non-zero.
- Exit code is `0` on success, non-zero on any validation or lookup failure.
- All success output goes to stdout; all errors go to stderr. No emojis, no
  ANSI escapes.

## Architecture

- **Core (pure)**: task model (`Task`, `TaskId`, `TaskText`), the list of
  tasks as an immutable value, and pure functions for each command
  (`add`, `markDone`, `remove`, `render`) that take the current task list and
  return either an error or the next task list plus a message to print.
  These functions have no knowledge of files, YAML, or `IO`.
- **YAML codec (pure)**: encode/decode between the core `Task` model and the
  YAML representation above. Decoding failures are values (`Either`/typed
  error), not exceptions.
- **Edge (Cats Effect `IO`)**: reads `todo.yaml` into a string, decodes it,
  runs the pure command logic, encodes the result, writes it back, and
  prints the resulting message — in that order, with the file write
  happening only on success.
- **CLI entry point**: parses `args: List[String]` into a typed command
  value (pure), then hands it to the edge layer. Argument parsing errors
  never touch `IO` or the filesystem.

## Testing

- Pure core and YAML codec are covered by unit tests with no file I/O
  (property-style where it fits: e.g. add-then-list contains the new task,
  remove-then-list does not contain the removed id).
- Edge/CLI behavior (reading and writing an actual `todo.yaml`, exit codes)
  is covered by tests against a temporary directory, not the repo's working
  directory.
- `just check` runs `scalafmtCheckAll` and `test` and must pass with zero
  compiler warnings (`-Werror`) before any change lands.

## Acceptance criteria

- Fresh checkout, no `todo.yaml`: `list` prints `No tasks.` and exits `0`.
- `add Buy milk` creates `todo.yaml` with one task, id `1`, `done: false`.
- `add` a second task assigns id `2`; `list` shows both in id order.
- `done 1` sets task `1`'s `done` to `true` in the file; `list` shows `[x]`
  for it.
- `remove 1` deletes task `1`; `list` no longer shows it; a subsequent
  `add` assigns id `3`, not `1`.
- `done 99` and `remove 99` (nonexistent id) both exit non-zero and print an
  error to stderr, leaving `todo.yaml` unchanged.
- No command ever prints ANSI color codes, a table, or Markdown syntax.
