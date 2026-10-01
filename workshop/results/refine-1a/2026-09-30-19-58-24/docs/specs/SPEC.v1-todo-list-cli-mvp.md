# Todo List CLI — MVP

## M1: Todo List CLI MVP (Status: PENDING)

A command-line todo list application.

**Acceptance Criteria:**
- Written in Scala 3, pure FP, using Cats.
- `just check` runs the test suite.
- The CLI supports four commands: `add`, `list`, `done`, and `remove`.
- Todos are stored in one YAML file, `todos.yaml`, in the current directory.
- `todos.yaml` is read and written using `org.virtuslab::scala-yaml`.
- CLI output has no color.
- CLI output has no table formatting.
- CLI output has no Markdown formatting.
