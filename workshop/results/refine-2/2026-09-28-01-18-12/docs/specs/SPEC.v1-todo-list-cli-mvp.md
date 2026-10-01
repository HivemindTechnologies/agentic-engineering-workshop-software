# SPEC v1 — Todo List CLI MVP

A command-line todo list in Scala 3: pure functional core, Cats Effect at the edge, one YAML file as the store. The MVP ships `add`, `list`, `done`, and `remove`, a colored structured terminal view for humans, and a Markdown checklist import/export for interfacing with rich text elsewhere.

The CI gate is `just check` (scalafmt, compile with `-Werror`, tests). Every milestone below must pass it. The GitHub Actions workflow file that runs this gate lands with M1, the first code milestone.

**Out of scope for v1:** editing an item's title, due dates, priorities, tags, multiple lists/files, undo, and any interactive (non-argument) mode.

## M1: Project Scaffolding and CI Gate (Status: PENDING)

Stands up the sbt build, the Cats Effect entry point, and the CI workflow that runs `just check` on every push. No todo behavior yet — this milestone proves the gate itself is wired up.

**Acceptance Criteria:**
- `sbt compile` exits 0 with a Scala 3 build configured for `-Werror` (a stray unused-import or similar warning fails the build).
- `just check` exits 0 on a clean checkout.
- Running the built CLI with no arguments, or with `--help`, prints usage text listing the `add`, `list`, `done`, and `remove` commands and exits 0.
- Running the CLI with an unknown command prints an error naming the command and exits non-zero.
- `.github/workflows/ci.yml` exists, triggers on push and pull_request, and its job invokes `just check`.

## M2: Domain Model and YAML Store (Status: PENDING)

The pure functional core: an item type and a store type, plus encode/decode to/from YAML. File I/O is pushed to the edge via Cats Effect; the codec itself is pure and has no knowledge of the filesystem. This is the one store file the app reads on startup and writes after every mutation — there is no separate database or intermediate format.

**Acceptance Criteria:**
- A store value encoded to YAML and decoded back yields an equal store (round-trip test), for both an empty store and a store with multiple items.
- Decoding a missing store file yields an empty store rather than an error.
- Decoding a store file with malformed YAML (e.g. a scalar where a list is expected) yields a typed decode error value, not a thrown exception.
- Each item in the store carries at minimum: an id unique within that store, a title, and a done flag.
- The store file path defaults to `./todo.yaml` relative to the working directory and can be overridden with a `--file <path>` flag accepted by every command.

## M3: CLI Commands — add, list, done, remove (Status: PENDING)

Wires the domain core to the four MVP commands. `list` is the colored, structured human view: open and done items are visually distinguished (e.g. by color and a check marker), and the structure holds even when color is disabled.

**Acceptance Criteria:**
- `todo add "<title>"` appends a new item with a fresh id and `done = false` to the store file; running it twice with different titles produces two items with distinct ids, verified by reading the YAML file back.
- `todo list` prints one line per item including its id, done state, and title; a store with zero items prints a distinct "no items" message rather than an empty line.
- `todo list` output contains ANSI color codes that differ between a done item and an open item when color is enabled; setting `NO_COLOR=1` produces the same line structure (id, state, title, one item per line) with no ANSI codes present.
- `todo done <id>` sets that item's done flag to true and persists it; running it again on the same id is a no-op that still exits 0.
- `todo done <id>` on an id absent from the store prints an error naming the id, exits non-zero, and leaves the store file unchanged.
- `todo remove <id>` deletes that item from the store and persists the change; the id is no longer present in a subsequent `list`.
- `todo remove <id>` on an id absent from the store prints an error naming the id, exits non-zero, and leaves the store file unchanged.

## M4: Markdown Checklist Import and Export (Status: PENDING)

The rich-text interface. The store stays YAML; Markdown is a checklist the app can produce from the store or consume into it, so the todo list can be dropped into or pulled out of any Markdown document.

**Acceptance Criteria:**
- `todo export --format md <path>` writes the current store as a Markdown checklist, one line per item, `- [ ] <title>` for open items and `- [x] <title>` for done items, in store order.
- `todo import --format md <path>` reads a Markdown checklist file and adds its items to the store, mapping `- [ ]` / `- [x]` to the done flag and the remainder of the line to the title, each import assigning ids fresh from the target store.
- Exporting a store then importing that file into an empty store yields items with the same titles and done flags as the original, in the same order (round-trip test; ids are not expected to match since Markdown carries none).
- Importing a file containing a line that is not a `- [ ]` or `- [x]` checklist item prints an error naming the offending line and exits non-zero without partially modifying the store file.
