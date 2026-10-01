# SPEC v1 — Todo List CLI (MVP)

Status: Draft
Scope: first shippable milestone chain for `todo`, a command-line todo list

## 1. Objective

A `todo` CLI that is:

- **Simple to set up** — one `sbt` project, one YAML file as the store, no daemon, no database.
- **CI-friendly** — deterministic, offline, warnings-as-errors, a single `just check` gate that a pipeline can call verbatim.
- **Pure FP / Cats style** — an effect-free domain core (plain functions, immutable data) wrapped by a thin Cats Effect `IO` shell at the edges (file I/O, console, clock).
- **Legible output** — colored, columnar terminal rendering that degrades gracefully when color isn't wanted (pipes, `NO_COLOR`, `--no-color`).
- **Directly interoperable** — the store is YAML anyone can read/edit by hand, and the list can be exported to and imported from a Markdown checklist ("rich text") for sharing outside the tool.

## 2. Non-goals (v1)

- Multi-user sync, locking across processes, or a server component.
- Recurring tasks, subtasks/hierarchies, reminders/notifications.
- Full Markdown fidelity (arbitrary GFM) — only the checklist subset defined in §6.3.
- Packaging/distribution (native image, brew formula, etc.) — tracked as future work in §12.
- Config file / profiles beyond a single store path override.

## 3. Architecture

```
core/    pure domain: model, invariants, pure operations on TodoList (no IO, no Console, no Clock)
store/   YAML <-> domain codecs + file persistence effects (Cats Effect Resource, atomic write)
render/  domain -> presentation: table rows, colors, Markdown checklist rendering/parsing
cli/     argument parsing (decline) + wiring: parses args -> loads store -> calls core -> renders -> saves
```

Rule: `core` never imports `cats.effect.*` or touches `System`/`Clock`/files directly. All non-determinism (current time, IDs, file contents) is passed in as data or produced by the `cli`/`store` layer and injected. This keeps the domain trivially unit-testable with plain `munit` and no fixtures.

Effect boundary: a single `IO[A]` program built with `for`-comprehensions in `cli`; no `Future`, no side-effecting `def`s that return `Unit`.

## 4. Domain model (`core`)

```scala
enum Priority derives CanEqual:
  case Low, Medium, High

enum Status derives CanEqual:
  case Open, Done

final case class TodoId(value: Long) extends AnyVal

final case class Todo(
  id: TodoId,
  title: String,           // non-empty, validated at construction (smart constructor)
  status: Status,
  priority: Priority,
  tags: List[String],
  createdAt: Instant,
  dueDate: Option[LocalDate]
)

final case class TodoList(items: Vector[Todo], nextId: Long)
```

Pure core operations, all total functions `TodoList => (TodoList, Either[TodoError, A])` or `TodoList => Either[TodoError, TodoList]`:

- `add(list, title, priority, tags, dueDate, now): Either[TodoError, TodoList]` — rejects blank titles.
- `complete(list, id): Either[TodoError, TodoList]` — `TodoError.NotFound` if id is absent.
- `reopen(list, id): Either[TodoError, TodoList]`
- `remove(list, id): Either[TodoError, TodoList]`
- `edit(list, id, changes): Either[TodoError, TodoList]`
- `filter(list, view: View): Vector[Todo]` where `View = All | Open | Done`, sorted by `(status, priority.reverse, dueDate, id)`.

`TodoError` is a sealed trait (`NotFound`, `BlankTitle`, `DuplicateImportId`, ...) — never exceptions. The `cli` layer maps each case to a message and a process exit code (§8).

## 5. Storage (`store`)

- Default path: `${TODO_HOME:-$HOME/.todo}/todo.yaml`, overridable per-invocation with `--file <path>`.
- One file, one `TodoList`. No partial writes: render to a temp file in the same directory, `fsync`, then atomic `rename` over the target (`Files.move` with `ATOMIC_MOVE`). Modeled as a `Resource`-scoped operation so a crash mid-write never corrupts the store.
- Missing file is not an error: treated as an empty `TodoList` (a fresh store is created on first successful write).
- Concurrent external edits are out of scope for v1: last writer wins, no lock file.

### 5.1 YAML schema

```yaml
version: 1
nextId: 4
items:
  - id: 1
    title: "Write the SPEC"
    status: done
    priority: high
    tags: [docs]
    createdAt: "2026-09-27T09:00:00Z"
    dueDate: null
  - id: 2
    title: "Wire up CI"
    status: open
    priority: medium
    tags: []
    createdAt: "2026-09-27T09:05:00Z"
    dueDate: "2026-10-01"
```

- `version` enables future migrations; v1 readers reject any other value with `TodoError.UnsupportedVersion` rather than guessing.
- Codec: `circe-yaml` for the YAML <-> JSON AST bridge, `circe-generic`/semiauto for `Todo`/`TodoList` <-> JSON. Enum fields serialize as lowercase strings (`open`, `done`, `low`/`medium`/`high`), not the enum's `toString`, so the file stays a stable public interface independent of Scala identifier casing.
- This schema **is** the YAML interface: `todo export --format yaml` and `todo import --format yaml` read/write exactly this shape, so the store file can be committed, diffed, or hand-edited directly.

## 6. Interfaces

### 6.1 CLI commands

Parsed with `decline` (functional, `Opts[A]`-based, composes cleanly with the `cats.effect` runtime via `decline-effect`).

| Command | Effect |
|---|---|
| `todo add <title> [--priority low\|medium\|high] [--due YYYY-MM-DD] [--tag t]...` | append, print the new row |
| `todo list [--open\|--done\|--all] [--format table\|yaml\|markdown]` | render current view, default `table`, default view `open` |
| `todo show <id>` | render one item in full |
| `todo done <id>` / `todo reopen <id>` | flip status |
| `todo edit <id> [--title] [--priority] [--due]` | partial update |
| `todo rm <id>` | delete, with the removed row echoed |
| `todo export --format yaml\|markdown [--output <path>]` | dump full list; stdout if no `--output` |
| `todo import --format yaml\|markdown <path> [--merge\|--replace]` | load items; `--merge` appends renumbering ids, `--replace` overwrites the store |

Global flags: `--file <path>` (store override), `--no-color`, `--quiet` (suppress the confirmation line, keep only errors/list output).

### 6.2 Terminal output (colored, structured)

- Renderer lives in `render`, is a pure `Vector[Todo] => String` (or `Chunk[fansi.Str]`), independent of whether it ends up on a real terminal — testable without a TTY.
- Color is applied with `fansi` (small, no transitive deps) and stripped centrally by calling `.plainText` when: output is not a TTY (`System.console() == null`), `NO_COLOR` is set (https://no-color.org), or `--no-color` is passed. One decision point in `cli`, never scattered across renderers.
- Palette: `Done` rows dim/strikethrough gray; `Open` rows default; priority tints the priority column only (`High` red, `Medium` yellow, `Low` unstyled) — color never carries meaning alone (status/priority are always also printed as text) to keep it usable when stripped.
- Layout: fixed-width columns (`id`, `[x]`/`[ ]`, priority, title, due date, tags), truncated with `…` past terminal width (`jansi`/`System.console` width probe, fallback 80).

### 6.3 Rich-text interface (Markdown)

A restricted, round-trippable GFM task-list dialect — the "rich text" interchange for sharing a list outside the tool (paste into a PR description, a README, Obsidian, etc.):

```markdown
- [ ] Wire up CI `#medium` `due:2026-10-01` `tag:ci`
- [x] Write the SPEC `#high` `tag:docs`
```

Grammar (per line, order-insensitive metadata tokens):

- `- [ ] ` / `- [x] ` — required, maps to `Status.Open`/`Status.Done`.
- Title — everything up to the first backtick-metadata token, trimmed.
- `` `#<priority>` `` — optional, one of `low|medium|high`; absent means `Medium`.
- `` `due:<YYYY-MM-DD>` `` — optional.
- `` `tag:<name>` `` — zero or more.

Not preserved through Markdown: `id`, `createdAt` (regenerated on import: new sequential id, `now()` as `createdAt`). This is the one intentional lossy edge and is documented in `todo export --help`, not left implicit. YAML export/import remains the lossless round trip.

## 7. Errors & exit codes

`AppError` (in `cli`) wraps `TodoError` plus I/O/parse failures (`StoreCorrupt`, `AmbiguousId`, `UnsupportedVersion`). Every path ends in exactly one of:

| Exit code | Meaning |
|---|---|
| 0 | success |
| 1 | user error (bad args, not found, blank title, ...) — message to stderr |
| 2 | store error (unreadable/corrupt YAML, unsupported version) |

No stack traces on expected errors; `IO`'s error channel carries `AppError`, caught once at the program's edge and turned into `(stderr message, exit code)`.

## 8. Dependencies

- Scala 3, `cats-core`, `cats-effect` (3.x).
- `com.monovore::decline` + `decline-effect` — CLI parsing.
- `io.circe::circe-core`, `circe-generic`, `circe-yaml` — codecs.
- `com.lihaoyi::fansi` — terminal color, no heavier than needed.
- `org.scalameta::munit`, `org.typelevel::munit-cats-effect-3` — tests.
- `org.scalameta::munit-scalacheck` — property tests for codec round-trips.

No network access anywhere in the main path — a hard requirement for the CI story in §10.

## 9. Testing strategy

- **Core**: pure `munit` tests, no fixtures beyond in-memory `TodoList` values — one test per pure function per `TodoError` case plus the happy path.
- **Codecs**: `munit-scalacheck` round-trip property — `decode(encode(list)) == list` for generated `TodoList`s, for both YAML and the Markdown subset (modulo the documented lossy fields, asserted explicitly rather than via full equality).
- **Store**: `munit-cats-effect-3` `IOSuite`, using JDK `Files.createTempDirectory` per test (no shared state, no cleanup ordering issues) — covers "missing file reads as empty," "write is atomic," "corrupt file surfaces `StoreCorrupt`."
- **CLI**: black-box tests that build the `Opts`/`IO` program and run it against a temp store, asserting on captured stdout/stderr and exit code — no subprocess spawning needed since the whole program is a pure `IO[ExitCode]` value.
- **Render**: golden-string tests comparing `.plainText` output (color stripped) for fixed inputs; a couple of targeted tests assert the raw ANSI-coded string for the color-on path.
- No test depends on wall-clock time or environment beyond an injected `now: Instant`.

## 10. CI integration

- `just check` is the one gate: `scalafmtCheckAll` -> `sbt test` (which fails the build on any `-Werror` warning at compile time). A CI job is exactly:

  ```sh
  just check
  ```

- Single JDK/Scala version matrix for v1 (no cross-building) — keep the pipeline fast and the setup simple, per the objective in §1.
- `sbt` dependency resolution should be cacheable (`~/.cache/coursier`, `~/.sbt`, `~/.ivy2`) by whatever CI runner is used; no other CI-specific code lives in the repo.

## 11. Milestones (one commit each, in order)

1. **Scaffold** — `build.sbt` (Scala 3, dependencies from §8), `project/`, package skeleton (`core`/`store`/`render`/`cli`), `scalafmt.conf`. `just check` passes on an empty test suite.
2. **Domain core** — model + pure operations from §4, full unit coverage, zero IO imports in `core`.
3. **YAML store** — schema (§5), circe codecs, atomic file `Resource`, temp-dir-backed tests.
4. **CLI wiring** — `decline` parser, `add`/`list`/`done`/`reopen`/`rm`/`edit`/`show` end-to-end against the real store, black-box CLI tests.
5. **Colored rendering** — table renderer, `fansi` palette, `NO_COLOR`/TTY/`--no-color` handling, golden-string tests.
6. **Markdown interface** — grammar (§6.3) encode/decode + `export`/`import --format markdown`, round-trip property tests.
7. **YAML interface parity** — `export`/`import --format yaml`, `--merge`/`--replace`, ambiguous/duplicate-id handling.

## 12. Open questions / future work

- Packaging (native-image, Homebrew tap, `scala-cli` shebang install) — deferred, not needed for the CI/dev-loop objective.
- Config file for defaults (default priority, default view) — deferred until there's a second real user preference to store.
- Multi-file / multi-list support — deferred; v1 is intentionally one file, one list.
