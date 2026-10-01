# SPEC v1 — Todo List CLI (MVP)

## Overview

A command-line todo list application written in Scala 3, using pure
functional programming style with Cats. `just check` runs the tests.

## Commands

- `add` — add a new todo item.
- `list` — list todo items.
- `done` — mark a todo item as done.
- `remove` — remove a todo item.

## Storage

- The store is a single YAML file, `todos.yaml`, in the current directory.
- The file is read and written with `org.virtuslab::scala-yaml`.

## Output

- No color.
- No table.
- No Markdown.
