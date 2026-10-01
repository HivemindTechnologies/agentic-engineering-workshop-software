# SPEC v1 — todo-list-cli MVP

## Overview

A command-line todo list written in Scala 3, using a pure functional core
with Cats. The store is one YAML file, `todo.yaml`, in the current
directory.

## Commands

- `add` — add a new todo item.
- `list` — list todo items.
- `done` — mark a todo item as done.
- `remove` — remove a todo item.

## Store

- A single YAML file, `todo.yaml`, in the current working directory.

## Output

- Plain text only.
- No color.
- No table formatting.
- No Markdown formatting.

## Testing

- `just check` runs the tests.
