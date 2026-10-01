# SPEC.v11: Spec shape

`scripts/spec-check` accepts a milestone whose headless subsections are in any order, and it accepts an acceptance criterion that is a plain bullet. `docs/specs/SPEC.v10-known-ambiguities-and-prompt-drift.md` uses both. Its implementation details sit above the criteria, and the details label shares its line with the first sentence. Every other spec in `docs/specs/` puts `**Acceptance Criteria:**` first and `**Implementation Details:**` after it, each label alone on its line. The criteria in those files are plain `-` bullets, so a reader cannot tick one.

This spec restores that one order, makes every criterion a checkbox, and tells `/implement` to finish with a short way to try the milestone. The checker and the two skills change. Recorded trees under `workshop/results/` and the participant specs under `workshop/material/` stay as they are.

## M1: The subsection order is the same in every spec (Status: ✅ DONE)

A milestone body is the lines after its `## M` heading and before the next `## ` heading. The only headless subsection labels are `**Acceptance Criteria:**` and `**Implementation Details:**`. Criteria come first. Details, when present, come after. Each label is the whole line.

**Acceptance Criteria:**

- [x] `scripts/spec-check` exits non-zero, names the file and the line, and prints nothing else, when `**Implementation Details:**` appears before `**Acceptance Criteria:**` in a milestone.
- [x] The same command exits non-zero on the line where either label has more text after the closing `**`.
- [x] The same command exits non-zero when a milestone contains a second `**Acceptance Criteria:**` or a second `**Implementation Details:**`.
- [x] The same command exits 0 for a milestone whose body is a description, then `**Acceptance Criteria:**` on its own line, then criteria, and for the same body with `**Implementation Details:**` on its own line after those criteria.
- [x] After this milestone, `scripts/spec-check` exits 0 on every `docs/specs/SPEC.*.md`. `SPEC.v10-known-ambiguities-and-prompt-drift.md` has been reordered so each milestone's details follow its criteria, and each details label is alone on its line. No file under `workshop/results/` or `workshop/material/` is edited.
- [x] `.claude/skills/refine/SKILL.md` and `.claude/skills/implement/SKILL.md` both state that order: criteria, then details, each label alone on its line, details never before criteria. The test is a search of those two files and of fixture specs. It does not start Claude.

**Implementation Details:**

- `subsection_violation` reports the first line where details precede criteria, where either label has text after it, or where either label is repeated. `SPEC.v10-known-ambiguities-and-prompt-drift.md` now has criteria first, and each details label is alone on its line. The paragraph that used to share that line is the details body.

## M2: Acceptance criteria are checkboxes (Status: ✅ DONE)

A criterion is one line, `- [ ] <text>` or `- [x] <text>`. `/implement` checks a box when that criterion's test passes, and leaves it empty when it does not. A human reads the boxes as the claim and the text as the expectation. The status line is still what says the milestone is done, and only the human sets that.

**Acceptance Criteria:**

- [x] `scripts/spec-check` exits non-zero, names the file and the line, and prints nothing else, when a non-blank line between `**Acceptance Criteria:**` and the next `**Implementation Details:**` or `## ` heading is not `- [ ] ` or `- [x] ` followed by text.
- [x] A milestone whose status is `IMPLEMENTED` or `✅ DONE` fails the check when any criterion is `- [ ]`. A milestone in any other status fails the check when any criterion is `- [x]`. `PARTIALLY_DONE` may contain both.
- [x] Every criterion in `docs/specs/SPEC.v1-onion-layering.md` through `SPEC.v11-spec-shape.md` is a checkbox. A `PENDING`, `IMPLEMENTING`, `SKIPPED`, or `POSTPONED` milestone uses `- [ ]` only. An `IMPLEMENTED` or `✅ DONE` milestone uses `- [x]` only. No file under `workshop/results/` or `workshop/material/` is edited.
- [x] `.claude/skills/implement/SKILL.md` says to set a criterion's box to `- [x]` only after that criterion's test passes, and to leave `- [ ]` otherwise. `.claude/skills/refine/SKILL.md` says a new criterion is written as `- [ ]`.
- [x] The test is a search of those specs, those skills, and fixture specs. It does not start Claude.

**Implementation Details:**

- A criterion matches `^- \[[ x]\] .+$`. Blank lines are allowed. The region ends at `**Implementation Details:**`. `IMPLEMENTED` and `✅ DONE` require `- [x]`. Every other status requires `- [ ]`. `PARTIALLY_DONE` may mix. The plain bullets in v1 through v10 were converted in place. v11 was already checkboxes. No file under `workshop/` was edited.

## M3: Implement ends with how to try the milestone (Status: ✅ DONE)

The human decides that a milestone is done. The last thing `/implement` writes, before it asks for that decision, is a way to see the change. One block per milestone implemented in that turn. The block is the starting point, and the spec is where the rest of the criteria live.

**Acceptance Criteria:**

- [x] `.claude/skills/implement/SKILL.md` ends the workflow with one block per milestone just implemented. The block names the milestone as `v<N>.M<id>`, lists at most five shell commands that show the new behavior, and names the spec path and the test or script path to open next. It does not pad the list to five. It does not mark the milestone done.
- [x] The same skill still says the milestone is marked `(Status: ✅ DONE)` only after the user confirms.
- [x] The test is a search of that skill file. It does not start Claude.

**Implementation Details:**

- The try-it step is workflow step 7, after the boxes are set and the details are written, and before the confirmation step. The confirmation sentence is unchanged.
