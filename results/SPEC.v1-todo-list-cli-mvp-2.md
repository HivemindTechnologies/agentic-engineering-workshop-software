# SPEC v1 — Todo List CLI (MVP)

Status: Draft
Scope: first shippable milestone of the CLI

## 1. Overview

A command-line todo list. A single binary, invoked as `todo`, that reads and
writes one YAML file in the current directory. Four commands: `add`, `list`,
`done`, `remove`. No daemon, no config file, no network access.

## 2. Goals

- Scala 3, pure functional style: effects pushed to the edge, domain logic
  built from pure, referentially transparent functions over immutable data.
- Cats for the functional core (`Either`, `ValidatedNel`, effect type for the
  runtime shell).
- A single flat-file store: `todos.yaml` in the current working directory,
  read and written with `org.virtuslab::scala-yaml`.
- `just check` is the one gate: scalafmt check, `-Werror` compile, and the
  full test suite.

## 3. Non-Goals (v1)

- No `edit`, `undone`/`reopen`, `search`, `sort`, or `clear` commands.
- No priorities, due dates, tags, or projects.
- No color output, no ANSI, no box-drawing tables, no Markdown formatting
  (no `**bold**`, no `` ` ``-fences, no `|` tables) anywhere in stdout/stderr.
- No config file, no `$XDG_CONFIG_HOME` lookup, no alternate store location —
  always `./todos.yaml`.
- No concurrent-access protection (file locking). Single-user, single
  process at a time is assumed.
- No third-party CLI-parsing framework. Argument parsing is hand-rolled and
  small enough not to need one.

## 4. Dependencies

- `org.scala-lang:scala3-library` — Scala 3.
- `org.typelevel::cats-core` — `Either`, `ValidatedNel`, `Show`, syntax.
- `org.typelevel::cats-effect` — `IO` as the runtime effect type; all file
  and console I/O runs inside it. `IOApp` is the program entry point.
- `org.virtuslab::scala-yaml` — YAML parsing and serialization for the
  store. No other serialization library.
- `org.scalameta::munit` + `org.typelevel::munit-cats-effect` — the test
  framework `sbt test` runs.

No other runtime dependency is added in v1. If a future milestone needs one
(e.g. a proper CLI-arg library once flags multiply), that's a new spec.

## 5. CLI Interface

Invocation: `todo <command> [args...]`

### `todo add <text>`

Appends a new todo with the next free id and `done = false`. `<text>` is
everything after `add`, joined with single spaces (so it does not need to be
quoted by the caller, though the shell may still require quoting for
special characters).

- Empty or whitespace-only text is a usage error; nothing is written.
- On success, prints one line to stdout:
  ```
  added 3: Buy milk
  ```

### `todo list`

Prints every todo, one per line, in ascending id order. Plain text, fixed
format, no headers, no separators:

```
[ ] 1  Buy milk
[x] 2  Write spec
[ ] 3  Call dentist
```

- `[ ]` = open, `[x]` = done (lowercase x, no color).
- Columns are a single space after the checkbox, then the id, then two
  spaces, then the text — no padding/alignment beyond that (no table
  layout, ids are not column-aligned across rows).
- An empty store prints nothing (no "no todos" banner) and exits 0.

### `todo done <id>`

Marks the todo with the given id as done. Idempotent: marking an
already-done todo done again succeeds and reprints the same confirmation.

- Prints: `done 2: Write spec`
- Unknown id: error, see §7.

### `todo remove <id>`

Deletes the todo with the given id. Ids are not reused/recycled after a
removal — the next `add` always uses `max(existing ids) + 1` (1 if the
store is empty).

- Prints: `removed 2: Write spec`
- Unknown id: error, see §7.

### No command / `help` / `--help`

Prints usage to stdout and exits 0:

```
usage: todo <command> [args]

commands:
  add <text>     add a new todo
  list           list all todos
  done <id>      mark a todo as done
  remove <id>    remove a todo
```

## 6. Data Model

```scala
final case class Todo(id: Int, text: String, done: Boolean)
```

- `id`: positive `Int`, assigned by the store on `add`, never reused.
- `text`: non-empty, trimmed; no length limit imposed.
- `done`: `Boolean`, defaults to `false` on creation.

## 7. Store: `todos.yaml`

Location: `todos.yaml` in the process's current working directory. Fixed
name, not configurable in v1.

Format:

```yaml
todos:
  - id: 1
    text: Buy milk
    done: false
  - id: 2
    text: Write spec
    done: true
```

Behavior:

- **Missing file**: treated as an empty todo list, not an error. `add` on a
  missing file creates it.
- **Read/parse**: the whole file is parsed into `List[Todo]` via
  `org.virtuslab::scala-yaml` up front, on every invocation. A file that
  parses but has the wrong shape (missing field, wrong type, duplicate id)
  is a store-corruption error (§7.1) — the CLI does not try to
  partially recover or silently drop bad entries.
- **Write**: every mutating command (`add`, `done`, `remove`) reads the full
  store, applies one pure transformation to the in-memory `List[Todo]`, and
  rewrites the whole file. No append-only log, no partial writes.
- **Write ordering**: entries are written in ascending id order regardless
  of insertion order.
- File writes are not atomic (no write-to-temp-then-rename) in v1; a crash
  mid-write can corrupt the file. Acceptable for a single-user local tool at
  this stage; flagged as a known gap, not silently assumed safe.

### 7.1 Store-corruption error

If `todos.yaml` exists but fails to parse as YAML, or parses but doesn't
match the expected shape (missing/mistyped fields, duplicate ids), the CLI
exits non-zero with a message naming the problem and the file, e.g.:

```
error: todos.yaml: line 4: missing field 'done'
```

The CLI never overwrites a file it failed to fully understand.

## 8. Architecture

Three layers, each effect-free except the outermost:

1. **Domain** (`domain` package) — pure. `Todo`, and pure functions over
   `List[Todo]`: `addTodo`, `markDone`, `removeTodo`, id assignment,
   rendering a `Todo` to its `list`-line and confirmation-line strings.
   Returns `Either[DomainError, A]` for anything that can fail (unknown id,
   empty text). No `IO`, no YAML, no `println`, anywhere in this package.
2. **Store** (`store` package) — the only place that touches
   `org.virtuslab::scala-yaml` and the filesystem. `TodoStore` exposes
   `load: IO[Either[StoreError, List[Todo]]]` and
   `save(List[Todo]): IO[Either[StoreError, Unit]]`, built on top of
   `cats-effect`'s file-handling combinators (`Resource`, blocking-safe
   reads/writes). Converts YAML AST to/from `List[Todo]` explicitly — no
   case-class auto-derivation "magic" the reader can't trace back to a line
   of code.
3. **CLI shell** (`Main`, an `IOApp`) — parses `args` into a `Command` ADT
   (pure, `Either[UsageError, Command]`), then for each command: load the
   store, run the matching pure domain function, save if it mutated,
   print the result line via `IO.println`/`IO.println(...).to(stderr)`, and
   map errors to exit codes (§9). This is the only layer allowed to call
   `IO.println` or exit the process.

```
args: Array[String]
  -> CliParser.parse            (pure)          => Either[UsageError, Command]
  -> TodoStore.load              (IO, effectful) => Either[StoreError, List[Todo]]
  -> Domain.apply(command, list) (pure)          => Either[DomainError, Outcome]
  -> TodoStore.save               (IO, effectful) => Either[StoreError, Unit]  [add/done/remove only]
  -> render(Outcome)              (pure)          => String
  -> IO.println                   (IO, effectful)
```

## 9. Error Handling & Exit Codes

All error and confirmation messages are single-line, plain text, prefixed
`error: ` for failures. No stack traces on expected error paths.

| Exit code | Meaning                                              |
|-----------|-------------------------------------------------------|
| 0         | success (including `help` and an empty `list`)        |
| 1         | domain error (unknown id, empty text on `add`)         |
| 2         | usage error (unknown command, missing/bad arguments)   |
| 3         | store error (corrupt `todos.yaml`, unreadable/unwritable file) |

Examples:

```
$ todo done 99
error: no todo with id 99
$ echo $?
1

$ todo add
error: usage: todo add <text>
$ echo $?
2
```

## 10. Testing Strategy

`sbt test` (invoked by `just check`) must cover:

- **Domain unit tests** (pure, no `IO`): id assignment on `add`,
  `markDone`/`removeTodo` on hit and miss, rendering of list lines and
  confirmation lines, including the `[ ]`/`[x]` markers.
- **Store round-trip tests**: write a `List[Todo]` to a temp file via
  `TodoStore.save`, read it back via `TodoStore.load`, assert equality;
  a fixed sample YAML string decodes to the expected `List[Todo]`; a
  malformed sample string yields a `StoreError` rather than throwing.
- **CLI parser tests** (pure): each command's happy path and its usage
  errors (missing text, non-numeric id, unknown command, no args).
- No test depends on a specific working directory outside a temp dir it
  creates and cleans up itself; no test leaves a `todos.yaml` behind in the
  repo root.

## 11. `just check`

`just check` is the single gate before any commit:

```sh
just check   # scalafmt --check, compile with -Werror, sbt test
```

A change is not done until `just check` passes clean — no warnings, no
formatting diffs, all tests green.

## 12. Open Questions / Future Work

Deliberately deferred past v1, to be covered by later specs, not decided
here:

- Atomic file writes (temp file + rename) for `todos.yaml`.
- An `edit`/`reopen` command.
- Sorting/filtering flags on `list`.
- A configurable store path.
- Concurrent-access safety (file locking) if the CLI is ever used from
  scripts running in parallel.
