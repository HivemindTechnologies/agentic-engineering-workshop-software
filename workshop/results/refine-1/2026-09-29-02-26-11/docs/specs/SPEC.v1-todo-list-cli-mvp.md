# SPEC v1 — Todo List CLI MVP

## Overview

A command-line todo list application written in Scala 3, using pure
functional programming with Cats. Commands are `add`, `list`, `done`,
and `remove`. State is stored in a single YAML file, `todos.yaml`, in
the current directory, read and written with `org.virtuslab::scala-yaml`.
`just check` runs the tests.

## Language and Libraries

- Scala 3.
- Pure FP style, built on Cats (e.g. `Either`/`IO`-style effect handling
  for I/O and errors; no mutable state, no thrown exceptions for
  control flow).
- YAML parsing and serialization via `org.virtuslab::scala-yaml`.

## Storage

- A single file, `todos.yaml`, located in the current working directory.
- The file is the sole source of truth: each command reads the current
  state from `todos.yaml`, applies the change (if any), and writes the
  full state back to `todos.yaml`.
- If `todos.yaml` does not exist yet, it is treated as an empty todo
  list (no todos), and is created on the first write.
- Each todo has:
  - `id`: a unique integer identifying the todo.
  - `text`: the todo's description.
  - `done`: a boolean, `true` if completed, `false` otherwise.

## Commands

### `add <text>`

Appends a new todo with the given text to `todos.yaml`. The new todo
is created with `done: false` and assigned a unique id (e.g. one
greater than the current maximum id, or `1` if the list is empty).

### `list`

Prints the todos currently stored in `todos.yaml`, one per line, in
plain text. Each line shows the todo's id, its done state, and its
text. Output is plain text only.

### `done <id>`

Marks the todo with the given id as done (`done: true`) in
`todos.yaml`. If no todo with that id exists, the command reports an
error and leaves `todos.yaml` unchanged.

### `remove <id>`

Removes the todo with the given id from `todos.yaml`. If no todo with
that id exists, the command reports an error and leaves `todos.yaml`
unchanged.

## Output

- Plain text only.
- No color.
- No table formatting.
- No Markdown formatting.

## Testing and Checks

- `just check` runs scalafmt, compiles with `-Werror`, and runs the
  test suite — this is the single gate for the project.
- Tests cover the four commands (`add`, `list`, `done`, `remove`) and
  their interaction with `todos.yaml`.

## Out of Scope

Anything not listed above (additional commands, additional storage
formats or locations, colorized or table-based or Markdown output,
configuration files, due dates, priorities, tags, etc.) is out of
scope for this MVP.
