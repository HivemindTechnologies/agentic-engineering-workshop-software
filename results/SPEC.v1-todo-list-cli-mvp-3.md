# Todo List CLI MVP

## M1: Add, List, Done, Remove (Status: PENDING)

A command-line todo list backed by a single YAML file.

**Acceptance Criteria:**
- The build targets Scala 3 and declares Cats as a dependency.
- Application logic is written in pure functional style using Cats, with no direct side-effecting code outside the effect boundary.
- `just check` runs scalafmt, compiles with `-Werror`, and runs the test suite, and it passes.
- The `add` command adds a new todo.
- The `list` command lists the todos.
- The `done` command marks a todo as done.
- The `remove` command removes a todo.
- Todos are persisted in a single YAML file named `todos.yaml` in the current working directory.
- `todos.yaml` is read and written using `org.virtuslab::scala-yaml`.
- Command output contains no ANSI color codes.
- Command output contains no table formatting.
- Command output contains no Markdown formatting.
