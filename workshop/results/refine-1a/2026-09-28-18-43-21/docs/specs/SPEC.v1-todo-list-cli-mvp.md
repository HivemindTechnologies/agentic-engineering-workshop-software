# SPEC v1: Todo List CLI MVP

## M1: Todo List CLI MVP (Status: PENDING)

A command-line todo list written in Scala 3, with a pure functional core and Cats. State lives in a single YAML file, `todo.yaml`, in the current directory. Output is plain text.

**Acceptance Criteria:**
- The project is written in Scala 3.
- The build depends on a Cats library.
- `just check` runs the test suite and it passes.
- An `add` command adds a new item to `todo.yaml`.
- A `list` command lists the items in `todo.yaml`.
- A `done` command marks an item in `todo.yaml` as done.
- A `remove` command removes an item from `todo.yaml`.
- `todo.yaml` in the current working directory is the only file the CLI uses to store todos.
- Command output contains no ANSI color codes.
- Command output is not formatted as a table.
- Command output is not formatted as Markdown.
