# SPEC.v1 — Todo List CLI MVP

## Goal

A command-line todo list: `add`, `list`, `done`, and `remove`, backed by a single
YAML file. Scala 3, pure FP, built on Cats. `just check` is the test gate.

## Non-Goals

- No color, table, or Markdown formatting anywhere in the output.
- No due dates, priorities, tags, notes, or editing of a todo's text.
- No multi-user or concurrent-access handling for `todos.yaml`.
- No packaging or distribution (native image, assembly jar, install script).
  For v1 the CLI is invoked in development via `sbt run -- <args>`.

## Tech Stack

- Scala 3.
- `org.typelevel::cats-core` for `Either`/`ValidatedNel`-based error handling.
- `org.typelevel::cats-effect` so every side effect (file read/write, console
  I/O) is a suspended `IO`, run exactly once at the CLI entry point.
- `org.virtuslab::scala-yaml` to encode and decode the store.
- `just check` — scalafmt check, compile with `-Werror`, and `sbt test` — is
  the one CI/test gate. No other command is authoritative.

## Store

A single file, `todos.yaml`, in the current working directory. A missing
file is treated as an empty list; it is not created until the first command
that mutates the list (`add`, `done`, or `remove`) succeeds. Schema:

```yaml
todos:
  - id: 1
    text: Buy milk
    done: false
  - id: 2
    text: Walk dog
    done: true
```

`id` is a positive integer, unique within the file, assigned by `add` as
`(current max id, or 0) + 1`. Ids are never reassigned or reused after a
`remove`.

## Constraints

These apply to every milestone below, not just the ones that mention them:

- No `var` and no mutable collections. All domain state is immutable.
- No thrown exceptions for expected error conditions (missing id, bad
  input, malformed YAML). Errors are values (`Either`/`ValidatedNel`), not
  control flow.
- All effects (reading or writing `todos.yaml`, writing to stdout/stderr)
  are suspended in `cats.effect.IO` and run once, at the CLI entry point.
- On any rejected input or failed lookup, the command exits with a non-zero
  code, prints a one-line error to stderr naming the problem, and leaves
  `todos.yaml` byte-for-byte unchanged.

## M1: Build & Tooling Setup (Status: PENDING)

Scaffold the sbt project so `just check` passes on an empty codebase, before
any application code exists.

**Acceptance Criteria:**
- `build.sbt` targets Scala 3, enables `-Werror`, and declares `cats-core`,
  `cats-effect`, and `org.virtuslab::scala-yaml` as dependencies.
- `.scalafmt.conf` sets the Scala 3 dialect; `just fmt` reformats the
  (empty) source tree without manual fixups.
- `just check` exits 0 on a fresh checkout with zero source and zero test
  files.

## M2: Domain Model & YAML Store (Status: PENDING)

The first milestone with application code: the immutable `Todo` model and
the pure encode/decode functions between it and `todos.yaml`. The CI
workflow is added here, alongside the first code it needs to check.

**Acceptance Criteria:**
- `Todo` is an immutable case class with fields `id: Int`, `text: String`,
  `done: Boolean`.
- Encoding an empty todo list and decoding the result produces the same
  empty list.
- Encoding a non-empty todo list and decoding the result produces an equal
  list (round-trip test with at least two todos).
- Loading from a path where `todos.yaml` does not exist yields an empty
  list, does not throw, and does not create the file.
- Loading a `todos.yaml` with malformed YAML yields a `Left`/error value,
  not a thrown exception.
- `.github/workflows/ci.yml` runs `just check` on push and pull_request.

## M3: `add` Command (Status: PENDING)

`todo add <text>` appends a new todo with a fresh id and `done = false`.

**Acceptance Criteria:**
- Running `add "Buy milk"` when `todos.yaml` does not exist creates it
  containing exactly one todo: id `1`, the given text, `done: false`.
- Running `add` again assigns an id one higher than the current maximum id
  in the file.
- Running `add` with an empty or whitespace-only text is rejected (per
  Constraints); `todos.yaml` is left unchanged (or absent, if it did not
  exist yet).

## M4: `list` Command (Status: PENDING)

`todo list` prints every todo as plain text, one per line.

**Acceptance Criteria:**
- With a missing or empty `todos.yaml`, `list` prints `No todos.` and
  exits 0.
- With todos present, `list` prints one line per todo in ascending id
  order, each formatted as `[ ] <id> <text>` for a pending todo or
  `[x] <id> <text>` for a done one.
- The output contains no ANSI escape codes, no box-drawing/table
  characters, and no Markdown syntax (`#`, `*`, `` ` ``, `|`).
- `list` never writes to `todos.yaml`.

## M5: `done` Command (Status: PENDING)

`todo done <id>` marks the matching todo as done.

**Acceptance Criteria:**
- Running `done <id>` for an existing, not-yet-done id sets that todo's
  `done` to `true` in `todos.yaml` and leaves every other todo unchanged.
- Running `done <id>` for an id already marked done succeeds idempotently:
  exit 0, file unchanged.
- Running `done <id>` for an id that is not in the file is rejected (per
  Constraints), with the error naming the missing id.
- Running `done <id>` where `<id>` does not parse as an integer is
  rejected (per Constraints).

## M6: `remove` Command (Status: PENDING)

`todo remove <id>` deletes the matching todo.

**Acceptance Criteria:**
- Running `remove <id>` for an existing id deletes exactly that entry;
  every other todo's id and fields are unchanged.
- Removing the only remaining todo leaves `todos.yaml` with an empty
  `todos` list, not an absent file and not `null`.
- Running `remove <id>` for an id that is not in the file is rejected (per
  Constraints), with the error naming the missing id.
- Running `remove <id>` where `<id>` does not parse as an integer is
  rejected (per Constraints).
