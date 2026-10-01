# Refine-3 — the prescribed milestones land, in order, every run

Curated for the software deck Steckbrief after Refine-2. Same prepare, same
`/refine` prompt with the settled-decisions list, now with an explicit XP-style
slice (`M1 scala and sbt setup`, `M2 cats hello world`, `M3 create and read
todos`, `M4 updates`) appended — three successful runs, picked as the last
three PASS simulates with a spec on disk. Not a dump of every stamp under
`workshop/results/refine-3/`.

Stamps used (all Claude `result=success`, SPEC present):

| Run | Stamp | Lines | Bytes | Headings |
| --- | --- | ---: | ---: | ---: |
| 1 | `2026-09-28-18-44-17` | 57 | 3972 | 6 |
| 2 | `2026-09-29-02-31-13` | 91 | 4247 | 6 |
| 3 | `2026-09-30-20-12-10` | 98 | 4906 | 6 |

Outlines below are the full `scripts/tocmd` output of
`docs/specs/SPEC.v1-todo-list-cli-mvp.md`. Where refine-2 still split its
milestones on its own terms (four in one run, six in the others), the four
milestones given in this prompt — `M1: Scala and sbt setup`, `M2: Cats hello
world`, `M3: Create and read todos`, `M4: Updates` — show up **verbatim, in
that order, in all three runs**. Only the title casing and a lead-in
"Settled choices"/"Settled decisions" heading move.

<!-- showcase:begin -->

## Results: Run 1 vs Run 2

Same four milestones, same order, as given in the prompt. Run 2 spends about
60% more bytes on the same slice — mostly extra acceptance criteria per
milestone, not new sections.

<div class="two-column">
<div class="column">

**Run 1** · **57 lines** · **3972 bytes**

```plaintext
# SPEC v1: todo-list-cli MVP
## Settled choices
## M1: Scala and sbt setup (Status: PENDING)
## M2: Cats hello world (Status: PENDING)
## M3: Create and read todos (Status: PENDING)
## M4: Updates (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-3/2026-09-28-18-44-17/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 2** · **91 lines** · **4247 bytes**

```plaintext
# SPEC.v1 — Todo list CLI MVP
## Settled decisions
## M1: Scala and sbt setup (Status: PENDING)
## M2: Cats hello world (Status: PENDING)
## M3: Create and read todos (Status: PENDING)
## M4: Updates (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-3/2026-09-29-02-31-13/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Run 2 vs Run 3

Same four milestones again, same order, same headings almost to the letter.
The only drift left is prose length: run 3 adds a fifth "pure FP" constraint
line and more acceptance criteria per milestone, not a fifth milestone.

<div class="two-column">
<div class="column">

**Run 2** · **91 lines** · **4247 bytes**

```plaintext
# SPEC.v1 — Todo list CLI MVP
## Settled decisions
## M1: Scala and sbt setup (Status: PENDING)
## M2: Cats hello world (Status: PENDING)
## M3: Create and read todos (Status: PENDING)
## M4: Updates (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-3/2026-09-29-02-31-13/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 3** · **98 lines** · **4906 bytes**

```plaintext
# SPEC v1: Todo List CLI MVP
## Settled decisions
## M1: Scala and sbt setup (Status: PENDING)
## M2: Cats hello world (Status: PENDING)
## M3: Create and read todos (Status: PENDING)
## M4: Updates (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-3/2026-09-30-20-12-10/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Generated Spec

````plaintext
# SPEC v1: Todo List CLI MVP

A command-line todo list: add, list, complete, and remove todos backed by a single
YAML file. Built Scala 3, pure FP, with Cats.

## Settled decisions

- Commands: `add`, `list`, `done`, `remove`. No other commands in this spec.
- Store: a single file, `todos.yaml`, in the current working directory. Read and
  written with `org.virtuslab::scala-yaml`. No database, no config file for the
  store path.
- `just check` (scalafmt, compile with `-Werror`, `sbt test`) is the test gate for
  every milestone.
- Output is plain text: no color/ANSI codes, no table formatting, no Markdown
  syntax anywhere in CLI output.
- Pure FP throughout: no `var`, no mutable collections, no thrown exceptions on
  any command path. Failures (bad input, missing todo, unreadable store) surface
  as values and are reported as a non-zero exit code plus a one-line message on
  stderr or stdout — never an uncaught exception or stack trace.

**Assumption flagged for review:** "the workflow file lands with the first code
milestone" is read as M1 (`sbt`/project setup), since that is the first milestone
that produces a buildable project and the first point `just check` has something
to run. If the intent was the first milestone with application behavior (M2),
say so and M1's CI criterion moves to M2.

## M1: Scala and sbt setup (Status: PENDING)

Bootstrap the sbt project for Scala 3 with Cats on the classpath, wired to the
`justfile` checks already in this repo. No application logic yet.

**Acceptance Criteria:**
- `build.sbt` declares a Scala 3.x project with `cats-core` as a dependency.
- `sbt compile` succeeds with `-Werror` and reports zero warnings on a clean
  checkout.
- `sbt test` succeeds (zero tests is acceptable at this milestone).
- `sbt scalafmtCheckAll` passes on the initial source tree.
- `just check` completes with exit code 0.
- A CI workflow file (e.g. `.github/workflows/ci.yml`) exists and runs
  `just check` on push and on pull request.

## M2: Cats hello world (Status: PENDING)

A minimal CLI entry point that proves the effect wiring works before any todo
logic exists: running the built program with no arguments prints a fixed
greeting and exits.

**Acceptance Criteria:**
- Running the program with no arguments prints exactly one greeting line to
  stdout and exits 0.
- The entry point sequences its output through a Cats-based effect type (e.g.
  `cats.effect.IO`), not direct `println` side-effected from `main` with no
  effect wrapper.
- A test runs the program's effect value and asserts on the captured output,
  rather than only asserting the code compiles.
- The main path contains no `var`, no mutable collections, and no `throw`.
- `just check` passes.

## M3: Create and read todos (Status: PENDING)

Implements `add` and `list`, and the `todos.yaml` read/write path.

**Acceptance Criteria:**
- Running `add "Buy milk"` on a directory with no `todos.yaml` creates the file,
  writes one todo with a unique id, title `"Buy milk"`, and `done: false`, and
  prints the assigned id to stdout.
- Running `add "Buy milk"` a second time appends a second todo with a different
  id; the first todo is unchanged in `todos.yaml`.
- Running `add ""` or `add "   "` (empty/whitespace-only title) exits non-zero,
  prints a message naming the title field, and leaves `todos.yaml` unchanged
  (or not created).
- Running `list` when `todos.yaml` does not exist, or exists with zero todos,
  exits 0 and prints no todo lines.
- Running `list` after two `add` calls prints both todos, one per line in the
  order they were added, each line showing at least id, done state, and title,
  with no color codes, table borders, or Markdown syntax.
- A todo written by `add` and then read back by `list` round-trips the same id
  and title; `todos.yaml` is valid YAML parseable by `org.virtuslab::scala-yaml`.
- Running `add` or `list` against a `todos.yaml` that is present but not valid
  YAML exits non-zero with a readable message, not a stack trace.
- `just check` passes.

## M4: Updates (Status: PENDING)

Implements `done` and `remove` against existing todos in `todos.yaml`.

**Acceptance Criteria:**
- Running `done <id>` for an id present in `todos.yaml` sets that todo's `done`
  field to `true` and exits 0; every other todo in the file is unchanged.
- Running `done <id>` for an id not present in `todos.yaml` exits non-zero with
  a message naming the missing id; `todos.yaml` is unchanged.
- Running `remove <id>` for an id present in `todos.yaml` deletes that entry and
  exits 0; every other todo in the file is unchanged.
- Running `remove <id>` for an id not present in `todos.yaml` exits non-zero
  with a message naming the missing id; `todos.yaml` is unchanged.
- After `done <id>`, a subsequent `list` shows that todo with done state true.
- After `remove <id>`, a subsequent `list` no longer shows that todo.
- `just check` passes.
````


<!-- showcase:end -->
