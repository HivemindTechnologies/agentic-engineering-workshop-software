# Refine-1a — same TOC shape, three PASS simulates

Curated for the software deck Steckbrief after RefineA 1. Same prepare, same
`/refine` prompt, fresh sessions — three successful runs, picked as the last
three PASS simulates with a spec on disk. Not a dump of every stamp under
`workshop/results/refine-1a/`.

Stamps used (all Claude `result=success`, SPEC present):

| Run | Stamp | Lines | Bytes | Headings |
| --- | --- | ---: | ---: | ---: |
| 1 | `2026-09-28-18-43-21` | 18 | 852 | 2 |
| 2 | `2026-09-29-02-27-21` | 27 | 1312 | 2 |
| 3 | `2026-09-30-19-58-24` | 15 | 536 | 2 |

Outlines below are the full `scripts/tocmd` output of
`docs/specs/SPEC.v1-todo-list-cli-mvp.md` — no truncation needed. Where
refine-1's free-form prompt produced a different heading tree every run,
`/refine` collapses to the same two-heading shape (title, then one `M1: …
(Status: PENDING)`) every time. The variance moves out of the TOC and into
the body: line/byte count swings 2x, and run 1 is the one run that drifts
from the paragraph's own wording — `todo.yaml` instead of `todos.yaml`, and
no mention of `org.virtuslab::scala-yaml` at all.

<!-- showcase:begin -->

## Results: Run 1 vs Run 2

Same two-heading shape. Run 1 quietly renames the store file; run 2 carries
every noun from the paragraph into the acceptance criteria.

<div class="two-column">
<div class="column">

**Run 1** · **18 lines** · **852 bytes**

```plaintext
# SPEC v1: Todo List CLI MVP
## M1: Todo List CLI MVP (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1a/2026-09-28-18-43-21/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 2** · **27 lines** · **1312 bytes**

```plaintext
# SPEC v1: Todo List CLI MVP
## M1: Todo list CLI (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1a/2026-09-29-02-27-21/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Run 2 vs Run 3

Same two-heading shape again. Run 3 is the leanest of the three — one short
paragraph, eight bullets, no prose beyond the paragraph's own nouns.

<div class="two-column">
<div class="column">

**Run 2** · **27 lines** · **1312 bytes**

```plaintext
# SPEC v1: Todo List CLI MVP
## M1: Todo list CLI (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1a/2026-09-29-02-27-21/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 3** · **15 lines** · **536 bytes**

```plaintext
# Todo List CLI — MVP
## M1: Todo List CLI MVP (Status: PENDING)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1a/2026-09-30-19-58-24/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Generated Spec

````plaintext
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
````


<!-- showcase:end -->
