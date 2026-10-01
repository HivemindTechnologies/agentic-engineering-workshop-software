# Refine-1 — three PASS simulates, three different SPECs

Curated for the software deck Steckbrief after Variance 1. Same prepare, same
prompt, fresh sessions — three successful runs that still wrote different
programs. Not a dump of every stamp under `workshop/results/refine-1/`.

Stamps used (all Claude `result=success`, SPEC present):

| Run | Stamp | Lines | Bytes | Headings |
| --- | --- | ---: | ---: | ---: |
| 1 | `2026-09-27-22-50-35` | 207 | 12126 | 17 |
| 2 | `2026-09-28-01-29-15` | 151 | 5758 | 14 |
| 3 | `2026-09-28-13-02-13` | 29 | 565 | 6 |

Outlines below are `scripts/tocmd` of
`docs/specs/SPEC.v1-todo-list-cli-mvp.md`, truncated to **12 lines** so both
columns share the same visual budget.

<!-- showcase:begin -->

## Results: Run 1 vs Run 2

They both differ in lengths and structure.

<div class="two-column">
<div class="column">

**Run 1** · **207 lines** · **12126 bytes**

```plaintext
# SPEC v1 — Todo List CLI (MVP)
## 1. Objective
## 2. Non-goals (v1)
## 3. Architecture
## 4. Domain model (`core`)
## 5. Storage (`store`)
### 5.1 YAML schema
## 6. Interfaces
### 6.1 CLI commands
### 6.2 Terminal output (colored, structured)
### 6.3 Rich-text interface (Markdown)
## 7. Errors & exit codes
… (+5 headings)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1/2026-09-27-22-50-35/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 2** · **151 lines** · **5758 bytes**

```plaintext
# SPEC v1 — todo-list-cli MVP
## Summary
## Goals
## Non-goals
## Store format
## Commands
### `add <text>`
### `list`
### `done <id>`
### `remove <id>`
## CLI behavior
## Architecture
… (+2 headings)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1/2026-09-28-01-29-15/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Run 2 vs Run 3

They both differ in lengths and structure.

<div class="two-column">
<div class="column">

**Run 2** · **151 lines** · **5758 bytes**

```plaintext
# SPEC v1 — todo-list-cli MVP
## Summary
## Goals
## Non-goals
## Store format
## Commands
### `add <text>`
### `list`
### `done <id>`
### `remove <id>`
## CLI behavior
## Architecture
… (+2 headings)
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1/2026-09-28-01-29-15/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
<div class="column">

**Run 3** · **29 lines** · **565 bytes**

```plaintext
# SPEC v1 — todo-list-cli MVP
## Overview
## Commands
## Store
## Output
## Testing
```

<p class="reproduce"><code>just tocmd workshop/results/refine-1/2026-09-28-13-02-13/docs/specs/SPEC.v1-todo-list-cli-mvp.md</code></p>

</div>
</div>

----

## Results: Generated Spec

````plaintext
# SPEC v1 — Todo List CLI MVP

## Purpose

A command-line todo list, minimal and pure-functional. Version 1 covers
exactly four commands and a single flat-file store.

## Stack

- Scala 3
- Pure FP style, effects held in `IO` (or equivalent) at the edges; core
  logic is total, referentially transparent functions over immutable data
- Cats (and Cats Effect for the `IO` boundary)
- `org.virtuslab::scala-yaml` for reading and writing the store
- `just check` runs scalafmt, compiles with `-Werror`, and runs the tests —
  this is the single gate for the project

## Store

- One YAML file, `todos.yaml`, in the current working directory
- Read at the start of a command, written back after any command that
  mutates state (`add`, `done`, `remove`)
- If `todos.yaml` does not exist yet, it is treated as an empty list —
  the first mutating command creates the file
- Each todo has:
  - `id`: a stable integer, assigned on `add`, never reused after `remove`
  - `text`: the todo's description, a non-empty string
  - `done`: boolean, defaults to `false`

## Commands

- `add <text>` — appends a new todo with a fresh id and `done = false`
- `list` — prints all todos, one per line, plainly: id, done state, text
- `done <id>` — marks the todo with the given id as `done = true`
- `remove <id>` — deletes the todo with the given id from the store

Unknown commands, missing arguments, or an id that does not exist are
reported as plain-text errors on stderr with a non-zero exit code.

## Output

- Plain text only
- No color
- No table formatting
- No Markdown

## Out of scope for v1

Anything not listed above — editing text, due dates, priorities,
sorting/filtering flags, multiple stores, configuration files, or
alternate output formats — is out of scope for this spec.
````


<!-- showcase:end -->
