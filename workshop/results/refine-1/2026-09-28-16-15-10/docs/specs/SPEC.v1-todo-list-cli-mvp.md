# SPEC v1: todo-list-cli MVP

## Summary

A command-line todo list. Scala 3, pure functional core. The store is one
YAML file, `todo.yaml`, in the current directory. `just check` runs the
tests.

## Commands

- `add` — add a new todo item.
- `list` — list todo items.
- `done` — mark a todo item as done.
- `remove` — remove a todo item.

## Store

- A single YAML file named `todo.yaml`.
- Located in the current directory (the directory the CLI is run from).

## Output

- Plain text only.
- No color.
- No table formatting.
- No Markdown.

## Testing

- `just check` runs the tests.
