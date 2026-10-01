# SPEC.v10: Known ambiguities and prompt drift

Two more gates join `hooks/pre-commit`, after `scripts/spec-check` and before `scripts/lesson-status smooth`. Both extend tooling this repository already has, rather than replacing it.

`scripts/term-drift` (v9.M2) catches word-level clusters — a plural, a one-edit typo, a near-synonym — across the whole corpus, without anyone naming the term in advance. It cannot catch a structural or behavioral ambiguity in one lesson's own wording, the kind that only surfaces once a real participant run resolves it the wrong way. `skills-1` is the case in hand: the prompt said "make the claude commands into skills" without naming the `.claude/skills/<name>/SKILL.md` layout, and a real run produced flat `.claude/skills/refine.md` files instead — not auto-discovered as a skill. M1 is a registry of incidents like that one: named, dated, and checked by a literal string, not a clustering score. Where term-drift asks "what looks alike that nobody named," this registry asks "did the specific thing we already fixed come back."

`scripts/prompt-distance` (v7.M1) already scores each lesson's fenced prompt against its neighbors and prints `previous=`/`next=`. That report stays informational — v7.M1 fixed that a low similarity does not fail the command, because a segment boundary is supposed to look different from what came before it. M2 does not change that. It adds a second comparison: not a lesson's similarity to its neighbors, but a lesson's similarity *to its own last recorded value*. A prompt edit that leaves the lesson looking like a different lesson, without anyone deciding that on purpose, is what this catches.

## M1: A registry of ambiguities that must not come back (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] `workshop/known-ambiguities.txt` is the registry. Entries are separated by one blank line. Each entry is exactly three lines, in order: `lesson: <id>`, then either `require: <text>` or `forbid: <text>`, then `why: <one-line reason>`. A malformed entry (wrong field order, a missing field, an unknown lesson id) is a script error naming the line.
- [x] `scripts/ambiguity-check` reads `workshop/JOURNEY.md`, `workshop/material/`, and the registry. For each entry it builds that one lesson's own corpus — its fenced prompt, its expected-observation bullets, and every file under `workshop/material/<lesson>/` — the same texts `scripts/term-drift` already reads for that lesson. A `require` entry passes when its text appears somewhere in that corpus; a `forbid` entry passes when it does not.
- [x] The command exits 0 when every entry passes. The first entry that fails stops the check: it prints the lesson id, the `require`/`forbid` line, and the `why:` line. It does not read `workshop/results/`, does not prepare `develop/`, and does not start Claude.
- [x] `just ambiguity-check` runs it.
- [x] The registry starts with one entry for the incident above: `lesson: skills-1`, `require: .claude/skills/<name>/SKILL.md`. Reverting `workshop/JOURNEY.md`'s `skills-1` prompt to wording that does not name that path fails the check on that entry.
- [x] The test supplies a fixture registry and a fixture journey/material tree, including one deliberately reverted to a past ambiguity, and asserts the command fails naming that entry. It does not start Claude.

**Implementation Details:**

`scripts/ambiguity-check` duplicates the small `lesson_texts`/fenced-prompt/observation-bullet readers already in `scripts/term-drift`, rather than importing that script as a module, matching how `lesson-status`, `judge-given`, `prompt-distance` and `instruct` each keep their own copy of the journey-order tuple. `workshop/known-ambiguities.txt` blocks are split on a blank line and parsed strictly: exactly three lines in the stated order, or `SystemExit` naming the registry path and the block's starting line number. An unknown `lesson:` id is the same kind of error. The per-lesson corpus is that lesson's fenced prompt plus its expected-observation bullets, concatenated with every file's text under `workshop/material/<lesson>/` (skipped entirely when that directory does not exist, as for a lesson like `skills-1` whose own delta is a no-op). The first failing entry prints `lesson:`, the `require:`/`forbid:` line, and `why:` to stderr and exits 1; the registry is otherwise silent on success, like `scripts/spec-check`. The registry's one entry is the `skills-1` incident from this journey: a real participant run once produced flat `.claude/skills/refine.md` files, not auto-discovered as a skill, before the prompt was corrected to name `.claude/skills/<name>/SKILL.md` explicitly.

## M2: A lesson's prompt drift from its own recorded baseline (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] `workshop/prompt-distance-baseline.txt` is a committed snapshot: one line per lesson, in the same shape `scripts/prompt-distance` already prints (`<lesson> previous=<value> next=<value>`). Nothing but `just prompt-distance-freeze` writes it.
- [x] `just prompt-distance-freeze` overwrites that file with the current board's output. It is a deliberate step the director runs after accepting a prompt's current shape, never run automatically.
- [x] `scripts/prompt-distance` gains `--check-baseline <file>` and `--threshold <fraction>` (default `0.05`). Without `--check-baseline`, its behavior is exactly as in v7.M1: it prints the board and never fails on similarity. With it, for every lesson present in both the current board and the baseline, it compares `previous=` and `next=` to the baseline's values for that same lesson and field.
- [x] A field whose baseline and current value are both numbers fails when `|current - baseline|` exceeds `--threshold`. A field that is `absent` in one and a number in the other fails unconditionally — a lesson gaining or losing a neighbor is a structural change, not a metric to threshold. A field that is `absent` in both does not fail.
- [x] A lesson present in the current board but not in the baseline does not fail — it has no recorded value yet. A lesson present in the baseline but no longer in the current board fails the check and names that lesson.
- [x] The command exits 0 only when no field fails. Each failing field prints the lesson, the field (`previous` or `next`), the baseline value, and the current value. It does not prepare `develop/` and does not start Claude.
- [x] `just prompt-drift-check` runs `scripts/prompt-distance` on `workshop/JOURNEY.md` with `--check-baseline workshop/prompt-distance-baseline.txt` and the default threshold.
- [x] The test supplies a fixture journey and a fixture baseline, including one lesson edited past the threshold and one within it, and asserts the command fails naming only the first. It does not start Claude.

**Implementation Details:**

`parse_baseline` reads one `<lesson> previous=<v> next=<v>` line per lesson — the exact shape `format_line` already prints, `absent` or a signed four-decimal number in each field — and `drift_failures` compares it against the same `neighbor()` values the plain board already computes, so freezing is just filtering the segment lines out of the normal board. `--check-baseline` and `--threshold` are additive flags: with neither, `main()` takes the same path as before and the six v7.M1 tests still pass unchanged. A lesson entirely missing from the current journey surfaces as its own baseline fields comparing against an absent current value, which the existing "absent vs. number always fails" rule already covers, so no separate case was needed for it. `workshop/prompt-distance-baseline.txt` was frozen once, from the journey as it stands with `skills-1` and `skills-2` already wired in, so it is the reference point the instructor's changes are committed against, not something they would drift from.

## M3: Both gates join the pre-commit hook (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] After `scripts/spec-check` passes on every spec, `hooks/pre-commit` runs `scripts/ambiguity-check`. A failure exits with that status and does not run the checks after it.
- [x] After `scripts/ambiguity-check` passes, the hook runs `scripts/prompt-distance` with `--check-baseline workshop/prompt-distance-baseline.txt`. A failure exits with that status and does not run `scripts/lesson-status smooth`.
- [x] When `workshop/prompt-distance-baseline.txt` does not exist, this step is skipped rather than failing — a clone that has never run `just prompt-distance-freeze` is not blocked by it.
- [x] The test builds fixture trees in a temporary directory. It does not start Claude.

**Implementation Details:**

`hooks/pre-commit` runs `scripts/ambiguity-check` unconditionally right after the `scripts/spec-check` loop, then, only when `workshop/prompt-distance-baseline.txt` exists, runs `scripts/prompt-distance --check-baseline ... > /dev/null` before falling through to the existing `scripts/lesson-status smooth` call. `set -euo pipefail` already stops the script at the first nonzero exit, so no extra `||` handling was needed. `tests/known_ambiguities_gate_test.py` stages the same kind of stub-script fixture `tests/quality_gate_test.py` uses, and that older file's two shared fixtures (`CommitGate.repo`, `SpecCheckGate.stage`) now also stub a passing `scripts/ambiguity-check`, since the hook calls it unconditionally.
