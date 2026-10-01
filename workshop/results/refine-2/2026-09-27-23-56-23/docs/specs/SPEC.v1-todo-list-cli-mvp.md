# SPEC v1 — Todo List CLI MVP

A command-line todo list, grown pure-functional-core / Cats-Effect-at-the-edge, backed by one YAML store file. The CI gate for every milestone is `just check` (scalafmt, compile with `-Werror`, tests) — nothing lands that doesn't pass it.

Settled scope for this spec:
- Human-facing output is colored, structured terminal text.
- Rich-text interop is a Markdown checklist (GitHub-flavored `- [ ]` / `- [x]`) that the app can import and export.
- The store is a single YAML file; every command loads it and, if it changes anything, saves it back — that load/save round trip *is* the YAML import/export.
- The MVP commands are `add`, `list`, `done`, `remove`.
- The CI workflow file that runs `just check` lands with the first code milestone (M1).

## M1: Build Scaffolding & CI Gate (Status: PENDING)

An sbt/Scala 3 project that builds, has a runnable CLI entry point with no commands wired up yet, and is checked in CI.

**Acceptance Criteria:**
- `sbt compile` succeeds with `-Werror` on a clean checkout (no warnings).
- `just check` (scalafmt check, compile, test) exits 0 on a clean checkout.
- Running the built CLI with no arguments or with `--help` prints usage text listing the four MVP commands (`add`, `list`, `done`, `remove`) and exits 0.
- Running the CLI with an unrecognized command prints an error to stderr and exits non-zero.
- A CI workflow file (e.g. `.github/workflows/ci.yml`) is added that runs `just check` on push and on pull requests.

## M2: Domain Model & YAML Store (Status: PENDING)

A pure `Task` type and pure YAML encode/decode functions for a task list, wired to file load/save at the edge via Cats Effect. Loading and saving this file *is* the app's YAML import/export.

**Acceptance Criteria:**
- A `Task` has an integer `id`, a non-empty `text`, and a boolean `done`; the functions that encode/decode a task list to/from YAML take no effect type in their signature (pure core).
- Encoding a list of tasks to YAML and decoding the result back yields an identical list (round-trip property, tested with generated task lists).
- Loading from a store path that does not exist yields an empty task list rather than an error.
- Loading a store file whose contents don't match the schema (e.g. `done` missing, `id` not an integer) fails with a non-zero exit and a stderr message naming the offending field, and leaves the file on disk unmodified.
- Saving a task list to a store path and then loading from that same path (through the filesystem, via Cats Effect) returns the same tasks.

## M3: Core Commands — add, list, done, remove (Status: PENDING)

Wires the four MVP commands to the store from M2. All four accept a `--file <path>` option for the store location, defaulting to `./todo.yaml`.

**Acceptance Criteria:**
- `todo add <text>` with blank/empty `<text>` is rejected: non-zero exit, stderr names the field, store is unchanged.
- `todo add <text>` with non-empty `<text>` appends a task with `done = false` and `id` = one more than the current highest id in the store (or `1` if the store is empty); the assigned id is printed to stdout.
- `todo list` against an empty or missing store prints an explicit "no tasks" message and exits 0.
- `todo done <id>` for an `<id>` absent from the store exits non-zero with a stderr message naming the id, and does not change the store.
- `todo done <id>` for an `<id>` present in the store sets that task's `done` to `true`; repeating the same command against the now-done task still exits 0 (idempotent).
- `todo remove <id>` for an `<id>` absent from the store exits non-zero with a stderr message naming the id, and does not change the store.
- `todo remove <id>` for an `<id>` present in the store deletes that task; the ids of the remaining tasks are unchanged, and a later `add` never reuses the removed id.
- Two invocations given the same `--file <path>` operate on that shared store regardless of the default `./todo.yaml` (e.g. `add --file custom.yaml ...` followed by `list --file custom.yaml` shows the added task; a plain `list` against the default store does not).

## M4: Colored, Structured `list` Output (Status: PENDING)

The human-facing rendering of `todo list`.

**Acceptance Criteria:**
- Tasks are printed in ascending `id` order, one per line, each showing its id, a checkbox marker (`[ ]` pending / `[x]` done), and its text.
- When stdout is a color-capable terminal, done and pending tasks are rendered in visually distinct colors (ANSI escape codes present in the raw output).
- When stdout is not a terminal (piped/redirected) or the `NO_COLOR` environment variable is set, no ANSI escape codes are emitted — this plain form is what tests assert against.

## M5: Markdown Checklist Import & Export (Status: PENDING)

Interfacing the store with a Markdown checklist file — the "rich text" side of the app, alongside the YAML store from M2.

**Acceptance Criteria:**
- `todo export <path>` writes the store's tasks as a Markdown checklist to `<path>`, one line per task in ascending `id` order (`- [ ] text` pending, `- [x] text` done), overwriting any existing file at that path.
- `todo import <path>` parses every line of `<path>` matching the checklist item pattern (`- [ ]` / `- [x]`, case-insensitive `x`) into a task, ignoring non-matching lines, and appends the parsed tasks to the store with new sequential ids.
- `todo import <path>` for a `<path>` that does not exist exits non-zero with a stderr message naming the path, and does not change the store.
- Round trip: exporting a store's tasks to a file, then importing that file into a separate empty store, produces tasks with the same `text` and `done` values in the same order (ids are not required to match, since export doesn't carry them).
