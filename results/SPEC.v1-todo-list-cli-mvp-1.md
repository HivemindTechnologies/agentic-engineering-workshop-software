# SPEC v1 — Todo List CLI (MVP)

Status: draft

## Summary

A command-line todo list. Four commands: `add`, `list`, `done`, `remove`. One
YAML file, `todos.yaml`, in the current directory, is the entire store. Scala
3, pure FP, Cats. `just check` (scalafmt, compile with `-Werror`, tests) is
the one gate.

## Goals

- Add, list, complete, and remove todos from the shell.
- Single human-readable store file, safe to read and edit by hand.
- Plain-text output only.

## Non-goals

- No color, no table rendering, no Markdown output.
- No due dates, priorities, tags, projects, or search.
- No config file, no environment variables, no concurrent access support.
- No interactive/REPL mode — one command per invocation.

## Tech stack

- Scala 3
- Cats (`cats-core`) for the FP building blocks; effects run under
  `cats-effect` `IO` — no side effect (reading argv, reading/writing the
  file, printing) happens outside of an `IO`.
- `org.virtuslab::scala-yaml` for reading and writing `todos.yaml`.
- munit (+ `munit-cats-effect`) for tests.
- scalafmt for formatting.

No other runtime dependencies (in particular: no CLI-parsing library —
argument parsing is small enough to hand-write and keep pure).

## Data model

```scala
final case class Todo(id: Int, text: String, done: Boolean)
```

- `id`: positive integer, assigned on `add`, stable for the todo's lifetime,
  never reused. Computed as `(max existing id, or 0) + 1`.
- `text`: the todo's description, non-empty, trimmed. Free-form; stored as a
  plain YAML string (quoted/escaped as scala-yaml sees fit).
- `done`: `false` on creation; flips to `true` via `done <id>`.

## Storage: `todos.yaml`

- Path: `./todos.yaml`, resolved against the process's current working
  directory. Not configurable in v1.
- Format:

  ```yaml
  todos:
    - id: 1
      text: "Buy milk"
      done: false
    - id: 2
      text: "Write spec"
      done: true
  ```

- Missing file is treated as an empty todo list — no file is created until
  the first `add`. `list`/`done`/`remove` against a missing file behave as if
  the store were empty (so `list` prints nothing, `done`/`remove` report "not
  found").
- Every command that mutates state (`add`, `done`, `remove`) reads the whole
  file, applies the change, and rewrites the whole file. No partial updates,
  no locking — single-user, single-process tool.
- A YAML file that fails to parse, or whose top-level shape doesn't match
  (missing `todos` key, wrong field types, etc.), is a fatal error: print a
  plain-text message to stderr and exit non-zero rather than guessing or
  silently truncating data.

## Commands

Invocation shape: `todo <command> [args...]`.

### `add <text...>`

- All trailing arguments are joined with a single space to form `text`.
- `text` must be non-empty after trimming; otherwise it's a usage error.
- Assigns the next id, appends the todo with `done = false`, writes the file.
- On success, prints one line to stdout: `Added <id>: <text>`.

### `list`

- Prints one line per todo, in ascending `id` order, to stdout.
- Line format: `<id> [ ] <text>` for an open todo, `<id> [x] <text>` for a
  done one — plain text, fixed-width bracket marker, no color, no table
  borders.
- Empty store prints nothing (no header, no "no todos" message) and exits 0.

### `done <id>`

- `id` must parse as an integer; otherwise it's a usage error.
- If a todo with that id exists and isn't already done, marks it done and
  writes the file; prints `Done <id>: <text>` to stdout.
- If already done, or no todo with that id exists, that's a "not found"
  error (see Errors).

### `remove <id>`

- `id` must parse as an integer; otherwise it's a usage error.
- If a todo with that id exists, removes it and writes the file; prints
  `Removed <id>: <text>` to stdout.
- If no todo with that id exists, that's a "not found" error.

## Output conventions

- Plain text only: no ANSI color/styling, no box-drawing/table layout, no
  Markdown syntax (`**`, `` ` ``, `#`, etc.) in any output.
- Normal command output goes to stdout, one line per event, terminated with
  a newline.
- Errors go to stderr as a single plain-text line, no stack traces.

## Errors and exit codes

- `0` — success.
- `1` — usage error: unknown command, wrong number of arguments, `id` that
  doesn't parse as an integer, empty `text` on `add`.
- `2` — not found: `done`/`remove` referencing an id that isn't in the
  store (including "already done" for `done`).
- `3` — store error: `todos.yaml` exists but can't be parsed into the
  expected shape, or can't be read/written (permissions, I/O failure).

## Testing

- Pure logic (id assignment, command → new-state transformation, line
  formatting) is unit-tested without touching the filesystem.
- YAML encode/decode round-trips (`Todo`/`List[Todo]` → YAML → back) are
  tested against `org.virtuslab::scala-yaml` directly.
- A thin layer of file-system-backed tests exercises each command end to end
  against a temp directory, covering: empty store, missing file, existing
  store, not-found cases, and a malformed `todos.yaml`.
- `just check` runs `scalafmtCheckAll` and `test` (via `sbt`) — this is the
  only gate; all of the above must pass under it.

## Open questions

- Exact stdout wording for each command (`Added`/`Done`/`Removed` prefixes
  above) is a placeholder — bikeshed at implementation time if needed.
- Whether `remove` on an already-done todo needs distinct messaging from
  removing an open one (currently: no, same message).
