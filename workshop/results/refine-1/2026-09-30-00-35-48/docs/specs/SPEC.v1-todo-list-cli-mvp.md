# SPEC v1 — Todo List CLI MVP

## Purpose

A command-line todo list, minimal and pure-functional. Version 1 covers
exactly four commands and a single flat-file store.

## Stack

- Scala 3
- Pure FP style, effects held in `IO` (or equivalent) at the edges; core
  logic is total, referentially transparent functions over immutable data
- Cats (and Cats Effect for the `IO` boundary)
- `org.virtuslab::scala-yaml` for reading and writing the store
- `just check` runs scalafmt, compiles with `-Werror`, and runs the tests —
  this is the single gate for the project

## Store

- One YAML file, `todos.yaml`, in the current working directory
- Read at the start of a command, written back after any command that
  mutates state (`add`, `done`, `remove`)
- If `todos.yaml` does not exist yet, it is treated as an empty list —
  the first mutating command creates the file
- Each todo has:
  - `id`: a stable integer, assigned on `add`, never reused after `remove`
  - `text`: the todo's description, a non-empty string
  - `done`: boolean, defaults to `false`

## Commands

- `add <text>` — appends a new todo with a fresh id and `done = false`
- `list` — prints all todos, one per line, plainly: id, done state, text
- `done <id>` — marks the todo with the given id as `done = true`
- `remove <id>` — deletes the todo with the given id from the store

Unknown commands, missing arguments, or an id that does not exist are
reported as plain-text errors on stderr with a non-zero exit code.

## Output

- Plain text only
- No color
- No table formatting
- No Markdown

## Out of scope for v1

Anything not listed above — editing text, due dates, priorities,
sorting/filtering flags, multiple stores, configuration files, or
alternate output formats — is out of scope for this spec.
