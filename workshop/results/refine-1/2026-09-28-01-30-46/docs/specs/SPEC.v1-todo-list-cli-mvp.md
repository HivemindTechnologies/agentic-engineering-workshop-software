# SPEC v1 — Todo List CLI MVP

## Summary

A command-line todo list. Scala 3, pure functional core, Cats Effect at the
edge, one YAML file as the store. Four commands: `add`, `list`, `done`,
`remove`.

## Goals

- Manage a flat list of todo items from the shell.
- Single source of truth: one YAML file, `todo.yaml`, in the current
  working directory.
- Deterministic, scriptable output — plain text only.

## Non-goals

- No color output.
- No table rendering.
- No Markdown output.
- No config file, no environment variables, no XDG paths — the store is
  always `./todo.yaml`.
- No subtasks, priorities, due dates, or tags in v1.
- No concurrent-access protection beyond what the filesystem gives for
  free (single-user, single-process CLI usage).

## Data model

Each item has:

| Field | Type | Notes |
|---|---|---|
| `id` | positive integer | Assigned on `add`, stable for the item's lifetime, never reused after `remove`. |
| `text` | string | The todo description, as given on the command line. |
| `done` | boolean | `false` on creation, `true` after `done`. |

The next-id counter is derived from the current file contents (max existing
`id` + 1; `1` if the file is empty or absent), so no separate counter field
is stored.

## Store format

`todo.yaml`, in the current directory, UTF-8, created on first `add` if
absent:

```yaml
items:
  - id: 1
    text: Buy milk
    done: false
  - id: 2
    text: Write report
    done: true
```

An absent file is treated as an empty list (`items: []`) by `list`, `done`,
and `remove`; only `add` creates the file. The whole file is read, modified
in memory, and rewritten on every command that mutates state — no partial
writes, no append-only log.

## Commands

### `todo add <text>`

- Appends a new item with a fresh `id`, given `text`, and `done: false`.
- `text` is the remaining command-line arguments joined with a single
  space; it must not be blank after trimming.
- Prints the created item's id and text on success.
- Creates `todo.yaml` if it does not exist.

### `todo list`

- Prints every item, one per line, in ascending `id` order.
- Each line shows: id, done/pending state, text — plain text, no color, no
  table, no Markdown. Exact format:

  ```
  1 [ ] Buy milk
  2 [x] Write report
  ```

- An empty store prints nothing (exit code still `0`).

### `todo done <id>`

- Marks the item with the given `id` as `done: true`.
- No-op success if the item is already done.
- Fails with an error and non-zero exit code if `id` does not exist.

### `todo remove <id>`

- Deletes the item with the given `id` from the store.
- Fails with an error and non-zero exit code if `id` does not exist.
- Does not renumber or reuse remaining ids.

## CLI behavior

- Invocation: `todo <command> [args...]`.
- Unknown command, missing/invalid arguments (e.g. non-integer `id`,
  blank `text`), or a missing `id` on `done`/`remove` all print a one-line
  error to stderr and exit non-zero.
- Successful commands exit `0`.
- All output is plain text; no ANSI codes are ever emitted, regardless of
  whether stdout is a terminal.

## Architecture

- **Pure functional core**: parsing arguments, decoding/encoding the store,
  and applying `add`/`list`/`done`/`remove` to an in-memory model are pure
  functions with no side effects, independently testable without touching
  the filesystem.
- **Cats Effect at the edge**: the only effects — reading `todo.yaml`,
  writing `todo.yaml`, reading `args`, writing stdout/stderr, and setting
  the process exit code — live in a thin `IOApp` shell that calls into the
  pure core.
- Errors from the pure core (parse failures, unknown id, blank text) are
  values, not exceptions; the effectful shell is responsible for turning
  them into stderr output and a non-zero exit code.

## Testing & checks

- `just check` is the one gate: `scalafmt` check, compile with `-Werror`,
  then the test suite. All three must pass for a change to be considered
  done.
- The pure core (arg parsing, YAML encode/decode, command application) is
  covered by unit tests that don't touch the filesystem.
- A thin set of integration tests exercises the `IOApp` shell against a
  temporary `todo.yaml` for each command's happy path and its documented
  error cases.

## Out of scope for v1 (candidates for later specs)

- Editing existing item text.
- Filtering `list` (e.g. only pending, only done).
- Alternate store locations or formats.
- Undo/history.
