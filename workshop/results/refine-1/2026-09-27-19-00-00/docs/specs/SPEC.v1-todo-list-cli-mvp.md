# SPEC v1 — todo-list-cli MVP

Status: draft · Target: v1.0.0 · Author: Isaias Bartelborth · Date: 2026-09-27

A command-line todo list in Scala 3. Pure functional core, Cats Effect at the edge, one YAML
file as the store. Two textual interfaces the user can drive directly: a **YAML document** (the
store itself) and a **task line** grammar (one task per line, typed by hand, rendered back in
colour).

---

## 1. Objectives

1. **Simple setup.** One sbt module, one `just check` gate, a handful of dependencies, no
   database, no daemon, no config file. `git clone && just check` works on a clean machine with
   only a JDK and sbt.
2. **CI-native.** Deterministic output, stable exit codes, colour auto-disabled when not a TTY,
   every check runnable as one command. `todo check` is usable as a CI step against a repo's own
   `todo.yaml`.
3. **Test infrastructure first.** Five test layers (§8) established in the earliest milestones so
   later features arrive with tests already cheap to write.
4. **Pure FP.** Total functions, typed errors, no side effects outside the `app`/`cli` packages.
   Enforced mechanically (§4.3), not by convention.
5. **Coloured, well-structured output.** Semantic 8-colour ANSI, aligned columns, glyphs with an
   ASCII fallback. The colours are a rendering of the task-line grammar, so they are covered by
   round-trip laws rather than by eyeballing.
6. **Direct interfacing.** The store is hand-editable YAML; tasks can be piped in and out as
   YAML or as task lines. No hidden state, no lock-in.

### Non-goals for v1

Recurring tasks · subtasks / dependencies · sync or multi-device · a TUI · time zones beyond the
system offset · i18n · multi-user access · encryption · SQL storage · shell completions ·
preserving comments in the YAML file across writes (§6.4).

---

## 2. Domain model

```scala
final case class Task(
    id:        TaskId,          // opaque, short, stable
    title:     Title,           // non-empty, single line, trimmed
    status:    Status,
    priority:  Priority,
    project:   Option[Project],
    tags:      SortedSet[Tag],
    due:       Option[LocalDate],
    created:   Instant,
    completed: Option[Instant], // Some iff status == Done
    notes:     Option[Notes],   // free multi-line text
)

enum Status   { case Todo, Doing, Done, Dropped }
enum Priority { case High, Normal, Low }

final case class Store(version: Version, tasks: Vector[Task])
```

### 2.1 Invariants

| # | Invariant | Enforced by |
|---|---|---|
| I1 | `TaskId` is 6 lowercase base32 chars (`a-z2-7`), unique within a store | smart constructor + `Store.validate` |
| I2 | `Title` is non-empty after trim, contains no newline, and its **last whitespace-separated token does not parse as an attribute** (§5.2) | `Title.apply` returns `Either[Invalid, Title]` |
| I3 | `Tag` and `Project` match `[a-z0-9][a-z0-9._-]*`, lowercased on construction | smart constructors |
| I4 | `completed.isDefined == (status == Done)` | `Store.validate`, and unrepresentable via the transition functions (§3) |
| I5 | `created <= completed` when both present | `Store.validate` |
| I6 | `version == 1`; a higher version is a hard error, a lower one is migrated | `Codec.decode` |
| I7 | Task order in `Store.tasks` is insertion order and is preserved by every operation except explicit sorting on render | property test |

`Store.validate: Store => ValidatedNel[Invalid, Store]` accumulates **all** violations — it is
what `todo check` reports, so one run must surface every problem in a hand-edited file.

---

## 3. Pure core

All state change is a total function on `Store`:

```scala
// core/Ops.scala — no F[_], no clock, no ids generated here
def add     (s: Store, t: Task):                              Store
def update  (s: Store, id: TaskId, f: Task => Task):          Either[NotFound, Store]
def remove  (s: Store, ids: NonEmptyList[TaskId]):            Either[NotFound, Store]
def setStatus(s: Store, id: TaskId, st: Status, now: Instant): Either[NotFound, Store]

def select  (s: Store, q: Query):  Vector[Task]   // filter + sort, pure
def resolve (s: Store, p: String): Either[Ambiguous | NotFound, TaskId] // unique id prefix
```

Anything ambient — the clock, id generation, the filesystem, the terminal — is a parameter or a
capability (§4.2), never reached for. `setStatus(_, _, Done, now)` sets `completed = Some(now)`;
any other status clears it, which is how I4 is made unrepresentable rather than merely checked.

### 3.1 Laws (property-tested, §8.1)

* `setStatus` is idempotent for a fixed `now`.
* `remove` then `add` of the same task restores membership (not order).
* `select` never invents or duplicates tasks: `select(s, q).toSet ⊆ s.tasks.toSet`.
* `select(s, Query.empty) == s.tasks`.
* `resolve` is consistent with `select`: a resolvable prefix always names a task in the store.

---

## 4. Architecture

### 4.1 Layout

One sbt project. Package boundaries, not modules — the simplest thing that can be enforced.

```
src/main/scala/todo/
  core/     Task, Status, Store, Ops, Query, Invalid   — pure, no CE, no java.io
  codec/    Yaml (encode/decode), Line (parse/render)  — pure
  render/   Ansi, Palette, Table, View                 — pure, String-producing
  app/      Files, Store IO, Console, Clock, Ids       — Cats Effect
  cli/      Command tree (decline), wiring, ExitCode   — Cats Effect
  Main.scala                                           — IOApp.Simple, the only unsafe run
```

Dependency direction is strictly downward: `cli → app → {codec, render} → core`. `core` depends
on nothing but cats-core and the standard library.

### 4.2 Capabilities

```scala
trait Clock[F[_]]   { def now: F[Instant] }
trait Ids[F[_]]     { def fresh: F[TaskId] }
trait Console[F[_]] { def out(s: String): F[Unit]; def err(s: String): F[Unit] }
trait Files[F[_]]   { def read(p: Path): F[Option[String]]; def writeAtomic(p: Path, s: String): F[Unit] }
```

Four small traits, each with a production instance in `app` and a deterministic test instance
(`Ids.counter`, `Clock.fixed`, `Console.capturing`, `Files.inMemory`). This is what makes the CLI
end-to-end tests (§8.4) run in-process in milliseconds.

### 4.3 Purity, enforced

* `scalacOptions`: `-Werror -deprecation -feature -unchecked -source:future -Wunused:all
  -Wvalue-discard -Wnonunit-statement -Ysafe-init`. Warnings are errors, so a discarded `IO` is a
  build failure.
* An **architecture test** (§8.6) scans the sources of `core`, `codec` and `render` and fails on
  any import of `cats.effect`, `java.io`, `java.nio`, `scala.concurrent`, or on the tokens
  `unsafeRun`, `Await`, `System.out`, `println`, `new Date`.
* No `throw`, no partial functions (`get`, `head`, `.apply` on a Map) in `core`. Errors are
  `Either` / `ValidatedNel`; `MonadThrow` appears only in `app` and `cli`.

---

## 5. Interfaces

### 5.1 YAML store

The whole store is one document, meant to be opened in an editor.

```yaml
version: 1
tasks:
  - id: k3fa7q
    title: Write the v1 spec
    status: doing
    priority: high
    project: docs
    tags: [spec, writing]
    due: 2026-10-01
    created: 2026-09-27T17:57:44Z
    notes: |
      Two textual interfaces, five test layers.
  - id: p92mzx
    title: Wire up CI
    status: todo
    priority: normal
    tags: []
    created: 2026-09-27T18:02:10Z
```

Rules:

* Timestamps are RFC 3339, always serialised in UTC with `Z`; `due` is a bare `LocalDate`.
* Optional fields are **omitted** when empty, never written as `null`. On read, `null` and
  absent are the same thing; `tags:` absent means empty.
* Unknown keys are an error under `todo check` and a warning elsewhere (they are most likely a
  typo in a hand edit, e.g. `tag:` for `tags:`).
* Decode errors carry the YAML line and column and the offending key path.

### 5.2 Task line (rich text)

One task, one line. What the user types after `todo add`, what `todo export --format lines`
emits, and — with colour and an id column added — what `todo list` shows.

```
<title> [@project] [#tag]… [!priority] [due:YYYY-MM-DD]
```

```
Write the v1 spec @docs #spec #writing !high due:2026-10-01
Buy milk @errands
Refactor the @home automation script       # title keeps "@home": not a trailing token
```

**Parsing is right-to-left.** Tokens are taken from the end of the line while they match
`@project`, `#tag`, `!(high|normal|low)` or `due:<date>`; scanning stops at the first token that
does not. Everything left, trimmed, is the title. This makes the grammar unambiguous with no
quoting or escaping, at the price of invariant I2: a title may not *end* in something that looks
like an attribute. The rejection message says so and suggests reordering.

Duplicate attributes: last one wins for `@project`, `!priority` and `due:`; `#tag` accumulates.

### 5.3 Rendered output

`todo list` renders a table. Columns: id, status glyph, title, project, tags, priority, due.
Empty columns are dropped from the table entirely, so a store with no projects shows no project
column.

```
  k3fa7q  ▸  Write the v1 spec        @docs      #spec #writing   !high   due 2026-10-01  (4d)
  p92mzx  ·  Wire up CI               @ci                                 due 2026-09-28  (today)
  x7t1bb  ✓  Read the style guide                #reading
```

* **Glyphs**: `·` todo, `▸` doing, `✓` done, `✗` dropped. ASCII fallback: `-`, `>`, `x`, `~`.
* **Grouping**: `--group-by project|status|due` inserts a bold group header and a blank line.
* **Footer**: a one-line summary (`3 tasks · 1 doing · 1 done · 1 overdue`), suppressed by
  `--quiet`.
* **Law**: `Ansi.strip(render(task)) == "<id>  <glyph>  " + Line.render(task.line)` up to column
  padding — colour and alignment never change the content (§8.3).

### 5.4 Colour

Semantic roles only, mapped to the **8 base ANSI colours plus bold/dim**. No 256-colour or
truecolour codes: the output must be legible on a light terminal, a dark terminal and in a CI log.

| Role | Style | Used for |
|---|---|---|
| `id` | dim | task ids |
| `title` | default | titles (dim + strikethrough when done or dropped) |
| `project` | cyan | `@project` |
| `tag` | blue | `#tag` |
| `high` / `low` | bold red / dim | `!priority` |
| `overdue` | red | due dates in the past |
| `soon` | yellow | due today or tomorrow |
| `ok` | green | `✓`, success messages |
| `warn` / `error` | yellow / red | diagnostics on stderr |
| `header` | bold underline | group headers |

Resolution order for whether colour is emitted, decided once in `cli` and passed to `render` as a
`Palette` value (`Palette.coloured` or `Palette.plain`):

1. `--color=always|never|auto` (explicit flag wins)
2. `NO_COLOR` set to anything non-empty → never
3. `TERM=dumb` → never
4. stdout is not a TTY → never
5. otherwise → always

ASCII fallback triggers when `LANG`/`LC_ALL` do not indicate UTF-8, or on `--ascii`.

### 5.5 Commands

```
todo add <line>…                      Add a task from task-line text
todo list [filters] [--group-by …]    List tasks (default: status todo,doing)
todo show <id>                        One task in full, notes included
todo start|done|drop|reopen <id>…     Status transitions
todo edit <id> [--title|--due|…]      Field-level edit; --due= clears
todo rm <id>…                         Delete (asks unless --yes or not a TTY)
todo export [--format yaml|lines]     Whole store, or filtered, to stdout
todo import [-f <file>|-] [--replace] Read YAML or lines from a file or stdin
todo check [--file …]                 Validate the store; the CI entry point
todo --version | --help
```

Global options: `--file <path>`, `--color`, `--ascii`, `--output rich|plain|yaml`, `--quiet`,
`--yes`.

`--output yaml` makes **every** command machine-readable, including errors, which is what makes
the tool scriptable:

```yaml
error:
  kind: not-found
  message: no task matches prefix "zz"
```

Filters for `list` and `export`: `--status`, `--project`, `--tag`, `--priority`, `--due-before`,
`--due-after`, `--overdue`, `--all`, `--text <substring>`, `--sort
created|due|priority|title|status`, `--reverse`, `--limit`.

### 5.6 Store location

1. `--file <path>`
2. `$TODO_FILE`
3. `./todo.yaml` if it exists (so a repo can carry its own list, and CI can lint it)
4. `${XDG_DATA_HOME:-~/.local/share}/todo/todo.yaml`

A missing store is an empty store for reads; the first write creates parent directories.

### 5.7 Exit codes

| Code | Meaning |
|---|---|
| 0 | success (including "no tasks matched", unless `--fail-on-empty`) |
| 1 | usage error — bad flag, bad task line, unparseable argument |
| 2 | not found or ambiguous id prefix |
| 3 | invalid store — failed validation, unknown `version`, concurrent modification |
| 4 | IO failure — unreadable or unwritable store |

There is exactly one place (`cli/ExitCodes.scala`) where the error ADT maps to codes, and a test
asserting the mapping is total.

---

## 6. Storage

### 6.1 Read

Read the file, decode, validate. Validation failure is exit 3 with every violation listed — never
a partial silent load.

### 6.2 Atomic write

Write to `<file>.tmp.<random>` in the same directory, flush, `fsync`, then `rename` onto the
target. A crash mid-write leaves the previous store intact; the temp file is cleaned up by a
`Resource` finaliser on both paths.

### 6.3 Concurrent modification

Single-writer assumption, optimistically checked: record `(size, mtime)` at read, re-check
immediately before `rename`. A change means another process wrote in between → exit 3, nothing
overwritten. No lock files in v1.

### 6.4 Known limitation

A write serialises the model, so **comments and key order in a hand-edited file are not
preserved**. Read-only commands (`list`, `show`, `check`, `export`) never rewrite the file, so a
commented store survives as long as edits are made by hand. This is a deliberate v1 trade; it is
called out in `--help` for the mutating commands.

---

## 7. Build & CI

### 7.1 Dependencies

Exact versions are pinned in `build.sbt` at milestone 0; the majors are the contract.

| Dependency | Why |
|---|---|
| Scala 3.3 LTS | stable, and LTS keeps the toolchain boring |
| `cats-core` 2.x | the core's only dependency |
| `cats-effect` 3.x | the edge |
| `decline` / `decline-effect` 2.x | applicative CLI parsing — a `Command` is a pure value, so it is testable without a process |
| `scala-yaml` 0.x (VirtusLab) | Scala 3-native YAML, no Java interop, derives codecs. Confined to `codec/Yaml.scala` so it can be swapped for circe-yaml without touching anything else |
| `munit`, `munit-cats-effect`, `munit-scalacheck` | test layers §8 |
| `sbt-scalafmt`, `sbt-scoverage`, `sbt-assembly` | format gate, coverage gate, one-file distribution |

No logging framework, no DI framework, no effect-system abstraction over `IO`.

### 7.2 The one gate

`just check` (already in the repo) runs `scalafmtCheckAll` + `test` under `-Werror` and prints a
line count, test count and warning count. CI runs the same command — no CI-only build logic, so
a green local run means a green pipeline.

### 7.3 GitHub Actions

`.github/workflows/ci.yml`, one workflow, two jobs:

* **check** — `ubuntu-latest`, `actions/setup-java` (Temurin 21, `cache: sbt`), then `just check`.
  ~2 min warm. This is the required status check.
* **dist** — on tags only: `sbt assembly`, smoke-test the produced jar (§8.5), attach it to the
  release.

CI hygiene that the design pays for:

* Tests never read the ambient clock, filesystem or terminal, so there is no flake surface and no
  `NO_COLOR` dance — the palette is an explicit argument.
* On failure, the golden-file test writes `target/golden-diff/` and the job uploads it as an
  artifact, so a rendering regression is inspectable without a local repro.
* `-Werror` in CI and locally, identically. Warnings do not accumulate.
* Coverage: `sbt coverage test coverageReport`, gate at **90% statement coverage for `core`,
  `codec` and `render`**, no gate on `app`/`cli`. Added in milestone 6 once the shape is stable.

### 7.4 Using the tool in CI

`todo check` exits 3 with a per-violation report, so a repo can lint its own `todo.yaml` in a
pre-commit hook or a CI step. `todo list --overdue --fail-on-empty=false --output yaml` gives a
machine-readable overdue report for a scheduled job.

---

## 8. Test infrastructure

Five layers plus two guards. Each is established by the milestone that first needs it, and each
has a home so there is never a question of where a test goes.

### 8.1 Property tests — `test/scala/todo/core`

ScalaCheck generators live in `test/scala/todo/gen/` and are shared: `genTask`, `genStore`
(unique ids by construction), `genQuery`, `genTaskLine`. Every law in §3.1 and every invariant in
§2.1 is a property. Minimum 100 cases each; shrinking must produce readable counterexamples, so
generators favour small stores and short titles.

### 8.2 Round-trip laws — `test/scala/todo/codec`

The two interfaces are specified by three laws:

```
decode(encode(store))          == Right(store)          // YAML
Line.parse(Line.render(line))  == Right(line)           // task line
Line.parse(s).map(Line.render) == Line.parse(s).map(Line.render(Line.parse(_)))  // idempotent
```

Plus a corpus of hand-written YAML files under `test/resources/yaml/{good,bad}/`: each `bad/`
file is paired with the expected diagnostic, which keeps error messages under test — the part of
a CLI users actually experience.

### 8.3 Golden files — `test/scala/todo/render`

Rendered output is compared against `test/resources/golden/*.txt`, stored with escapes written
literally (`\e[36m`) so a diff is readable in a terminal and in a PR. Regenerate with
`TODO_GOLDEN_UPDATE=1 sbt test`; the test fails loudly if that variable is set in CI. Covered:
empty list, mixed statuses, overdue and due-soon, long titles, grouping, plain palette, ASCII
fallback, `--output yaml`, and the top-level `--help` text.

The strip law from §5.3 is a property here, not a golden: colour may change, content may not.

### 8.4 CLI end-to-end, in-process — `test/scala/todo/cli`

The whole command tree is run against `Files.inMemory`, `Clock.fixed`, `Ids.counter` and
`Console.capturing`. One helper:

```scala
def run(args: String*)(store: String = ""): (ExitCode, String, String, String)
//                                          exit,      stdout, stderr, resulting store
```

Assertions are on all four. This is the layer that grows with every feature: a new command is
done when its happy path, its error path, its exit code and its effect on the store are asserted
here. No process spawn, no temp directory, no sleeping — the suite stays under a second.

### 8.5 Real IO and real process — `test/scala/todo/app`

The narrow band that mocks cannot cover, using `munit-cats-effect` and a `ResourceFunFixture`
temp directory:

* atomic write: a `Files` that fails after the temp write leaves the original file byte-identical
* the optimistic concurrency check actually detects an interleaved write
* store discovery order (§5.6) with real env and real paths
* TTY detection returns *something* and defaults to no colour when piped
* one smoke test on the assembled jar: `add`, `list`, `done`, `check` in sequence, asserting exit
  codes only. Tagged `Slow`, excluded from the default `sbt test`, run by the `dist` job.

### 8.6 Architecture guard — `test/scala/todo/ArchitectureSuite.scala`

The source scan from §4.3. Fast, no reflection, and it fails at the moment a `cats.effect` import
drifts into `core` rather than at the code review that might not catch it.

### 8.7 Exhaustiveness guard

A test enumerating every `AppError` case and asserting it has an exit code (§5.7) and a rendered
message in both `rich` and `yaml` output. Adding an error case without wiring it up fails the
build.

---

## 9. Milestones

One commit per milestone, each green under `just check`, each independently reviewable.

| # | Deliverable | Acceptance |
|---|---|---|
| 0 | **Skeleton**: `build.sbt`, `.scalafmt.conf`, scalac options, CI workflow, `Main` with `--version`/`--help` | `just check` green in CI; `todo --version` prints a version; architecture suite present and passing on an empty `core` |
| 1 | **Domain + YAML codec**: §2, `codec/Yaml`, `Store.validate`, generators | round-trip property green; `bad/` corpus produces the expected diagnostics |
| 2 | **Store IO**: `Files`, atomic write, discovery, concurrency check, `todo check` | §8.5 suite green; `todo check` exits 0/3 correctly against the corpus |
| 3 | **`add` + `list` + rendering**: `Line.parse`, `render`, palette, colour resolution, goldens | strip law green; goldens for coloured, plain and ASCII output; `NO_COLOR` honoured |
| 4 | **Lifecycle**: `start`/`done`/`drop`/`reopen`/`rm`/`edit`/`show`, prefix resolution | §3.1 laws green; every command covered in §8.4 with its exit code |
| 5 | **Filters, sorting, grouping, `import`/`export`** | `export --format lines \| import` is a fixpoint on the store (property test) |
| 6 | **Polish**: `--output yaml` everywhere, error catalogue + §8.7 guard, help goldens, coverage gate, `sbt assembly` + `dist` job | coverage ≥ 90% on `core`/`codec`/`render`; jar smoke test green; README usage examples generated from goldens |

---

## 10. Definition of done for v1

* `just check` green; CI green on a clean checkout with a cold cache.
* Every §2.1 invariant and §3.1 law has a property test; every command has an end-to-end test
  asserting exit code, stdout, stderr and resulting store.
* `core`, `codec`, `render` contain no effects, proven by the architecture suite.
* `todo list` output is legible on light, dark and dumb terminals, and in a CI log.
* A hand-written `todo.yaml` can be read, validated, listed, exported as lines, re-imported, and
  compared equal.
* `--help` is complete enough that the README can quote it verbatim.

---

## 11. Open questions

1. **`scala-yaml` vs `circe-yaml`** — `scala-yaml` keeps the dependency tree Scala-only and
   derives codecs cleanly, but its diagnostics are less mature. Decide at milestone 1 against the
   `bad/` corpus; the codec is isolated precisely so this stays a one-file decision.
2. **`notes` editing** — v1 sets notes via `--notes` only. Launching `$EDITOR` is tempting but
   drags a hard-to-test capability into `app`; deferred unless it earns a milestone of its own.
3. **Comment preservation** (§6.4) — would need a round-tripping YAML AST. Out of scope for v1;
   revisit if hand-editing turns out to be the dominant workflow.
4. **`todo list` default filter** — hiding `done`/`dropped` by default is convenient but hides
   state; `--all` mitigates it. Keep for v1, watch for surprise.
