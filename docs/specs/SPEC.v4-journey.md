# SPEC.v4: Journey

`workshop/JOURNEY.md` is the journey. Each lesson changes what the participant can ask for, and the next lesson is there because of what the previous one produced. The folder layout of v1 stays. This spec is the order of work, not a second copy of the prompts.

## M1: The tagged baseline holds (Status: ✅ DONE)

`refine-1`, `refine-1a`, and `refine-2` are the baseline. A spec is judged from its table of contents. The prompts live in `workshop/JOURNEY.md`.

**Acceptance Criteria:**

- [x] Until v6, `just validate` re-prepares, simulates, and judges only `refine-1`, `refine-1a`, and `refine-2`, with at least two runs each, and stops on the first `FAIL`. v6.M1 is the later command: one named lesson, or every lesson, one line each.
- [x] A run of `runs=1` fails before Claude starts.
- [x] Result trees from before the cutoff written by that command stay on disk and are not judged. See v3.M2.

## M2: Validate through implement-1 (Status: ✅ DONE)

The lessons already written after the baseline are checked with the same harness, one judge per lesson.

**Acceptance Criteria:**

- [x] `refine-3`, `refine-4`, `refine-5`, `refine-6`, and `implement-1` each have a `JUDGE.md` and an expected path before a validate run includes that lesson.
- [x] The judge for an implement lesson checks the acceptance criteria of the milestone the prompt names.
- [x] A lesson is added to `just validate` only after the two before it pass under their current cutoff.

**Implementation Details:**

- `refine-3`, `refine-4`, `refine-5`, `refine-6`, and `implement-1` each have `workshop/results/<lesson>/JUDGE.md` and an expected path, and `just validate` runs all of them. The 2026-09-28 run recorded `verdict: pass` for each lesson through `implement-1`.
- The implement-1 judge decides the two claims the prompt's first observations name: M1 is `(Status: IMPLEMENTED)`, and that milestone has a headless `**Implementation Details:**` line. A commit, a push, and the question about marking the milestone done do not decide the verdict. One scripted reply has no second turn and no outer git history.
- There is no harness check that refuses to add a lesson before the two before it pass. `refine-3` through `implement-1` were wired together after `refine-1`, `refine-1a`, `refine-2`, and `refine-4` had already passed, and the same run then recorded pass for all eight.

## M3: First tests, then a local gate (Status: ✅ DONE)

`implement-2` is one call that implements M2 and M3 together. `quality-gate-1` follows it. No remote workflow. The early prompts do not name the hook.

**Acceptance Criteria:**

- [x] `workshop/JOURNEY.md` gains `implement-2` and, immediately after it, `quality-gate-1`.
- [x] `implement-2` is the first lesson whose expected result includes a failing-then-passing test for those two milestones.
- [x] `quality-gate-1` installs a local pre-commit hook that runs `just check`. The lesson text names the hook when the lesson is written, not before.
- [x] GitHub Actions is a later change to that same `just check` gate, not a file this lesson creates.

## M4: Commands become skills, then the checker (Status: ✅ DONE)

The participant's `refine` and `implement` commands become skills. `quality-gate-2` runs the spec-check from v5.M1 on the result trees. Outlines from before that checker stay as the baseline.

**Acceptance Criteria:**

- [x] `quality-gate-2` follows the skill lessons. It runs the one Python spec-check added to this repository, on the specs in the result trees.
- [x] The script is on `PATH` inside the existing dev shell. The flake gains Python 3 for that script and does not gain a second flake.
- [x] A result tree stamped before `quality-gate-2` is not rewritten to satisfy the checker.
- [x] The Scala application does not depend on the script.
