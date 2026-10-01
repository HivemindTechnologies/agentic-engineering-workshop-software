# 🏝️ Refine 1a

**The same prompt, now under /refine.** The prompt is the refine-1 request with `/refine` in front. The command says to ask when a criterion would otherwise be a guess.

<!-- journey: refine-1a -->
<!-- backing-lesson: refine-1a -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 01:00
- Last Token Usage: 135.1k
- Results: `workshop/results/refine-1a/2026-09-29-02-27-21`
- Material: `workshop/material/refine-1a/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Refine 1a

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare refine-1a
just claude
```

</div>
<div class="column">

*WORKTREE*

```plaintext
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── docs/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
```

</div>
</div>

----

<!-- .slide: class="steckbrief-prompt-obs" -->

## Refine 1a

*PROMPT TO TEST*

```plaintext
/refine a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI.
Scala 3, pure FP, Cats, and just check runs the tests. Commands are add,
list, done, and remove. The store is one YAML file, todos.yaml, read and
written with org.virtuslab::scala-yaml, in the current directory. No
color, no table, no Markdown.

Write the spec from that paragraph. Do not ask, and do not add a
criterion the paragraph does not state.
```

*EXPECTED OBSERVATIONS*

- It writes the spec from the paragraph.
- It does not add color, a table, or Markdown.

----

<!-- showcase:from workshop/results/refine-1a/EXPLANATION.md -->

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
