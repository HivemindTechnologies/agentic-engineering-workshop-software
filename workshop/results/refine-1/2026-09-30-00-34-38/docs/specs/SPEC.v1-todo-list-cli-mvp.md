# SPEC v1 — Todo List CLI MVP

## Overview

A command-line todo list application written in Scala 3, using pure
functional programming with Cats. All state lives in a single YAML file,
`todos.yaml`, in the current directory, read and written with
`org.virtuslab::scala-yaml`.

## Commands

- `add <text>` — append a new todo with the given text. New todos start
  not done.
- `list` — print all todos.
- `done <id>` — mark the todo with the given id as done.
- `remove <id>` — delete the todo with the given id.

No other commands or flags are in scope for this version.

## Data Model

Each todo has:

- `id` — a unique integer.
- `text` — the todo's description.
- `done` — a boolean, `false` until marked done.

## Storage

- All todos live in one YAML file, `todos.yaml`, in the current working
  directory.
- Each command reads the current file, applies its change (if any), and
  writes the full file back using `org.virtuslab::scala-yaml`.
- If `todos.yaml` does not exist yet, it is treated as an empty todo list;
  `add` creates the file.

## Output

Plain text only: no color, no table formatting, and no Markdown in any
command's output.

## Tech Stack

- Scala 3
- Cats, pure FP style throughout
- `org.virtuslab::scala-yaml` for reading and writing `todos.yaml`

## Build & Test

`just check` is the one gate: it runs scalafmt, compiles with `-Werror`,
and runs the tests.
