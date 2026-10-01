# SPEC.v2 — Todo List CLI output formats

**develop_app.v2** — builds on **develop_quality-gates-3.v1** (`SPEC.v1-todo-list-cli-mvp.md`). Adds machine- and human-friendly list renderers beyond the v1 table/YAML plan: JSON, Markdown, and explicit ANSI color control. Configuration files and env precedence stay out of scope (develop_app.v3). Due dates, priorities, tags, and assignees stay out of scope (develop_app.v4).

## Goal

`list` (and any other read-side dump the CLI already exposes) can emit JSON, Markdown, or an ANSI-colored human table, selected by a CLI flag, without changing the YAML store format.

## Scope

- Output modes for listing: `table` (ANSI-aware human), `json`, `markdown`, and keep v1 `yaml` if already present.
- Deterministic JSON (stable field order / pretty or compact documented).
- Color on/off when the table mode is selected (TTY default on; `--no-color` / `NO_COLOR` respected).

## Non-goals

- Application config files or PureConfig (develop_app.v3).
- New domain fields (develop_app.v4).
- HTML, CSV, or protobuf.

## M1: JSON list output (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `list --format json` (or the flag spelling fixed in Implementation Details) prints a JSON array of todos to stdout and exits 0 on a non-empty store.
- [x] Empty store prints `[]` and exits 0.
- [x] JSON parses with a standard library parser in tests; field names for id, title, and status (or done) are stable across runs.
- [x] Invalid `--format` exits non-zero with a message that names the allowed formats.

**Implementation Details:**

- Flag: `--format=json` (also accepts legacy `--output=`). Compact JSON; fields `id`, `title`, `done`.

## M2: Markdown list output (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `list --format markdown` prints a Markdown table or bullet list (one style, documented) including id, title, and status.
- [x] Output is plain UTF-8 text suitable for piping into a `.md` file; no ANSI escapes in markdown mode.
- [x] A unit or integration test asserts header/structure markers (`|` or `- `) and a known title after `add`.

**Implementation Details:**

- Markdown pipe table with header `| ID | STATE | TITLE |`.

## M3: ANSI table and color controls (Status: IMPLEMENTED)

Aligns with or finishes develop_quality-gates-3.v1 color intent where still PENDING.

**Acceptance Criteria:**

- [x] `list --format table` (default if no `--format`) renders an aligned table; when color is enabled, not-started / in-progress / done use distinct ANSI styles (white/yellow/green or the WOW-documented mapping).
- [x] `--no-color` and env `NO_COLOR` (any value) disable ANSI codes in table mode.
- [x] A test captures stdout with color on and off and asserts escape sequences appear only when color is on.

**Implementation Details:**

- Pending = white (`37`), done = green (`32`). Color boolean from `Cli.colorEnabled` / `NO_COLOR`.
