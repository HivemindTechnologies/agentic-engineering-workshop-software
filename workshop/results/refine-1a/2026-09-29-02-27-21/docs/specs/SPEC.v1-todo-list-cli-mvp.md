# SPEC v1: Todo List CLI MVP

## M1: Todo list CLI (Status: PENDING)

A command-line todo list, written in Scala 3 as pure FP with Cats. Todos are
stored in a single YAML file, `todos.yaml`, in the current directory, read and
written with `org.virtuslab::scala-yaml`. The CLI has four commands: `add`,
`list`, `done`, and `remove`. Output is plain text: no color, no table, no
Markdown.

**Acceptance Criteria:**

- The project targets Scala 3, and `just check` (scalafmt check, compile with
  `-Werror`, and the test suite) passes.
- The build depends on Cats, and command logic is implemented as pure
  functions with side-effecting I/O pushed to the edge (no direct mutation or
  I/O inside the core add/list/done/remove logic).
- `add` adds a new todo to the store; a subsequent `list` shows it.
- `list` prints every todo currently in the store.
- `done` marks an existing todo as done in the store; a subsequent `list`
  shows it as done.
- `remove` deletes an existing todo from the store; a subsequent `list` no
  longer shows it.
- All four commands read and write a single file, `todos.yaml`, in the
  current directory, using `org.virtuslab::scala-yaml`.
- Command output contains no ANSI color/escape codes, no table formatting,
  and no Markdown syntax (e.g. `#`, `*`, `` ` ``) — plain text only.
