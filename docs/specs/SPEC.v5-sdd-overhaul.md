# SPEC.v5: SDD overhaul

This repository becomes a spec-driven project. The harness design lives in `docs/specs/` as v1 through v4. Lesson prompts stay in `workshop/JOURNEY.md`. The participant's later skill lessons stay in v4.M4. The skills in this spec are the ones the outer repository uses on itself.

## M1: refine and implement skills share one spec-check (Status: ✅ DONE)

The source text is `~/.claude/commands/refine.md` and `~/.claude/commands/implement.md`. Both skills call one script that lives in this repository.

**Acceptance Criteria:**

- [x] `.claude/skills/refine/SKILL.md` and `.claude/skills/implement/SKILL.md` exist. Each file's body contains the workflow of the matching command. A project copy replaces reading the home-directory command.
- [x] One script, `scripts/spec-check`, is the only checker. Both skills invoke that path. Neither skill contains a second copy.
- [x] `scripts/spec-check <spec.md>` exits 0 when every milestone heading that owns acceptance criteria matches `^## M[0-9]+([A-Za-z][A-Za-z0-9_-]*)?: .+ \(Status: (PENDING|IMPLEMENTING|IMPLEMENTED|PARTIALLY_DONE|SKIPPED|POSTPONED|✅ DONE)\)$`, the criteria label is the line `**Acceptance Criteria:**`, and no heading `### Implementation Details` or `### M` appears under a milestone.
- [x] The same command exits non-zero, names the file and the line, and prints nothing else, when any of those three rules fails.
- [x] `scripts/spec-check` exits 0 on `docs/specs/SPEC.v1-onion-layering.md`, `SPEC.v2-simulation.md`, `SPEC.v3-judge.md`, `SPEC.v4-journey.md`, `SPEC.v5-sdd-overhaul.md`, and `SPEC.v6-interactive-tracked-subagents.md`.

**Implementation Details:**

- The skill bodies are the command workflows. They do not point at a home-directory command, and the "follow `.cursor/skills` if it exists" sentence is omitted because these files are the project skills.
- `scripts/spec-check` prints the first violation as `path:line` on stderr and prints nothing on success.
- A status heading with no exact `**Acceptance Criteria:**` line fails on the heading line.
- A `### M` heading fails, so a grouped milestone does not pass the checker. Milestones in this repository stay flat.

## M2: The prose docs become these specs (Status: ✅ DONE)

v1 is the onion layering, v2 is simulation, v3 is the judge, v4 is the journey order. The prose files are the source that was reshaped. After this milestone they are no longer a second copy.

**Acceptance Criteria:**

- [x] `docs/specs/` contains `SPEC.v1-onion-layering.md`, `SPEC.v2-simulation.md`, `SPEC.v3-judge.md`, `SPEC.v4-journey.md`, `SPEC.v5-sdd-overhaul.md`, and `SPEC.v6-interactive-tracked-subagents.md`.
- [x] `docs/onion.md`, `docs/simulation.md`, `docs/judge.md`, and `docs/evolution.md` are absent.
- [x] `README.md` points at `docs/specs/SPEC.v1-onion-layering.md` for the design and at `workshop/JOURNEY.md` for the prompts.
- [x] A search of tracked files finds no remaining path `docs/onion.md`, `docs/simulation.md`, `docs/judge.md`, or `docs/evolution.md`.
- [x] `workshop/JOURNEY.md` is still the only file that holds lesson prompts. This milestone does not move a prompt into a spec.

**Implementation Details:**

- Comments in the outer justfile that cited `docs/simulation.md` and `docs/judge.md` now cite `docs/specs/SPEC.v2-simulation.md` and `docs/specs/SPEC.v3-judge.md`.
- The four prose paths remain written in the acceptance criteria above. `git ls-files` does not list them.

## M3: A spec table of contents with optional line numbers (Status: IMPLEMENTED)

Long spec files are easier to edit when the milestones are listed with their line numbers. This is a read-only index, not a second checker.

**Acceptance Criteria:**

- [x] `scripts/tocmd <path.md>` prints one line per ATX heading in file order, from `#` through `######`, with the `#` markers and title text unchanged. It does not print non-heading lines. A missing path exits non-zero and prints nothing on success.
- [x] `scripts/tocmd --lines <path.md>` prints the same headings with the 1-based line number first, then a single space, then the heading line exactly as it appears in the file.
- [x] `scripts/tocmd <directory>` prints the table of contents of every `*.md` file in that directory, sorted by name. When more than one file is printed, each block starts with the file path on its own line and blocks are separated by one blank line. A single file in a directory, or one file path, prints headings only with no path label.
- [x] `.claude/skills/refine/SKILL.md` tells the agent to run `scripts/tocmd` on a spec before editing it, and to use `--lines` when jumping to a milestone by line number.
- [x] `.claude/skills/implement/SKILL.md` tells the agent to run `scripts/tocmd --lines` on the active spec when selecting or reviewing a milestone.
- [x] The test supplies fixture markdown files and asserts both output shapes. It does not start Claude.

**Implementation Details:**

- `scripts/tocmd` treats a line as a heading when it matches `^#{1,6} `. Success prints headings to stdout only. `--lines` may appear before the path. A directory argument uses sorted `*.md` in that directory only, not subdirectories.
