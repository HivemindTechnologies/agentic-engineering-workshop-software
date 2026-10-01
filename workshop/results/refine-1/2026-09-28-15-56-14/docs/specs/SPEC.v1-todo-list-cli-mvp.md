# SPEC v1 — todo-list-cli MVP

## Summary

A command-line todo list written in Scala 3, with a pure functional core and
Cats Effect at the edge. State is stored in a single YAML file, `todo.yaml`,
in the current directory. Four commands: `add`, `list`, `done`, `remove`.

## Language and runtime

- Scala 3.
- Pure functional core: business logic (parsing commands, updating the todo
  list, deciding what to print) is expressed as pure functions with no side
  effects.
- Cats Effect is used at the edge only, for the effects the program actually
  needs: reading and writing `todo.yaml`, reading CLI arguments, writing to
  stdout/stderr, and exit codes.

## Storage

- Exactly one store: a YAML file named `todo.yaml`.
- Location: the current working directory the CLI is invoked from.
- If `todo.yaml` does not exist yet, the CLI treats the list as empty; it is
  created on the first write (e.g. the first `add`).
- Each todo item has:
  - an id (integer, assigned by the CLI, stable for the life of the item)
  - a text/title (string)
  - a done flag (boolean, defaults to false)

## Commands

### `add`

Adds a new todo item with the given text to `todo.yaml`. The new item is not
done. The CLI assigns it an id.

### `list`

Prints the todo items currently in `todo.yaml`, including their id, text,
and done status.

### `done`

Marks the todo item with the given id as done in `todo.yaml`.

### `remove`

Removes the todo item with the given id from `todo.yaml`.

## Output

- Plain text only.
- No color / no ANSI styling.
- No table rendering.
- No Markdown formatting.

## Testing and checks

- `just check` runs scalafmt, compiles with `-Werror`, and runs the test
  suite. This is the one gate for the project.
