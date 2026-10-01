# SPEC.v4 — Todo List CLI planning fields and assignees

**develop_app.v4** — builds on develop_app.v3. Adds due dates, priorities, tags, and assigner/assignee identity (email) for later notification. Does not send email.

## Goal

Todos carry optional planning metadata and assignee information so a team can track who owns what and when it is due, while the store remains a single local YAML file.

## Scope

- Optional **due date** (ISO-8601 calendar date `YYYY-MM-DD`).
- Optional **priority** enum: `low` | `medium` | `high` (exact spellings fixed in Implementation Details).
- Zero or more **tags** (non-empty strings, case-sensitive, unique per todo).
- **Assignees**: zero or more people identified by email; optional **assigner** email for who assigned.
- CLI surfaces to set/clear these on `add` / `edit` (flag spellings in Implementation Details).
- JSON/Markdown/table/YAML outputs from develop_app.v2 include the new fields when present.

## Non-goals

- SMTP or any network notification transport.
- Recurring tasks, reminders, time zones beyond storing a naive date.
- Multi-file or remote stores.

## M1: Domain model and YAML round-trip (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `Todo` (or successor) includes optional due date, priority, tags, assignees, and assigner; smart constructors reject empty tags, empty emails, and invalid dates/priorities with messages that name the field.
- [x] YAML store round-trips the new fields; todos written without them still load (backward compatible with develop_app.v3 files).
- [x] Property or example tests cover round-trip and rejection cases.

**Implementation Details:**

- Types: `DueDate`, `Priority`, `TodoTag`, `Email`. Store encode omits empty optionals.

## M2: CLI write path (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `add` and `edit` accept flags to set due date, priority, tags, assignees, and assigner; omitting a flag leaves the field unchanged on edit and empty/default on add.
- [x] Clearing a field is supported (documented flag or empty value) for due date, priority, tags, and assignees.
- [x] Integration tests cover add-with-metadata and edit-clear.

**Implementation Details:**

- Flags: `--due=`, `--priority=`, `--tag=`, `--assignee=`, `--assigner=`, `--clear-due`, `--clear-priority`, `--clear-tags`, `--clear-assignees`, `--clear-assigner`.

## M3: CLI read path and filters (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] `list` output in table/json/markdown/yaml includes the new fields when set.
- [x] `list` supports filtering by at least one of: tag, assignee email, or priority (exact flags in Implementation Details).
- [x] Filter tests use a fixture store and assert inclusion/exclusion.

**Implementation Details:**

- Filters: `--tag=`, `--assignee=`, `--priority=`.

## M4: Config defaults for assignee identity (Status: IMPLEMENTED)

**Acceptance Criteria:**

- [x] Optional config/env default assigner email (e.g. `TODO_ASSIGNER` / `todo.assigner`) applies when `add` omits assigner.
- [x] Precedence matches develop_app.v3 (CLI → env → application.conf → default none).
- [x] A test sets env default assigner and asserts the stored todo.

**Implementation Details:**

- `AppConfig.assigner` / `TODO_ASSIGNER`; `Cli.run(..., defaultAssigner=...)`. Covered via `AppConfig.resolve` + domain `Todos.add` defaultAssigner.
