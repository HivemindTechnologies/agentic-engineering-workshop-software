# SPEC.v3: Judge

Judging compares result trees. Headings are the structure a spec claims to have, so they are the first evidence. The participant sandbox never sees a result. See v2 for how a tree is captured.

## M1: The judge reads trees and writes a verdict (Status: ✅ DONE)

`JUDGE.md` lives in `workshop/results/<lesson>/`. There is no shared judge prompt beside these folders. Expected observations stay in `workshop/JOURNEY.md`. The judge prompt is not printed by `just prepare`.

**Acceptance Criteria:**

- [x] `just judge <lesson>` fails before Claude starts when `workshop/results/<lesson>/JUDGE.md` is missing.
- [x] The prompt given to the judge contains, per tree, the heading lines of each `*.md` file and then the full spec text. A tree with no markdown file is given as `spec: absent` plus the final reply from `session.jsonl`.
- [x] The judge is `claude -p` with `--tools ""`. nono's working directory is `workshop/`, `.claude-home` at the harness root is an extra allow, and `develop/` is not in that grant.
- [x] The answer is appended to `workshop/results/<lesson>/judgements/<stamp>.md`. The recipe prints `PASS judge <lesson>` only when the answer contains a line `verdict: pass`. `verdict: fail`, or no such line, prints `FAIL judge <lesson>` and exits non-zero.

## M2: A cutoff drops older trees (Status: ✅ DONE)

Older trees stay on disk. A cutoff file selects which stamps are judged.

**Acceptance Criteria:**

- [x] When `workshop/results/<lesson>/cutoff` contains a stamp, `just judge <lesson>` with no stamp arguments skips every stamp directory whose name is strictly earlier, prints `cutoff:` and `skipped:`, and judges only the rest.
- [x] Fewer than two stamps at or after the cutoff fails before Claude starts, with `expected: at least 2 trees` and `received:` equal to the count that remains.
- [x] A stamp argument names a tree. A named stamp from before the cutoff is skipped. `just validate` writes the cutoff once, at the moment that command starts, into each lesson it runs, then simulates and judges only trees from that moment on.

## M3: One line per lesson (Status: PENDING)

`just summary` reads the trees already on disk. It does not start Claude and it does not prepare.

**Acceptance Criteria:**

- [ ] The command prints one line per lesson, in journey order: `refine-1`, `refine-1a`, `refine-2`, `refine-3`, `refine-4`, `refine-5`, `refine-6`, `implement-1`.
- [ ] A lesson with no stamp at or after its cutoff prints `not run`. A lesson whose in-range tree is missing `docs/specs/SPEC.v1-todo-list-cli-mvp.md`, for refine-1, refine-1a, refine-2, or refine-4, prints `FAIL simulate`. Fewer than two complete in-range trees prints `FAIL judge`. The newest in-range judgement of `verdict: pass` prints `PASS`. A complete pair with no in-range verdict prints `not judged`.
- [ ] The recipe exits non-zero when any line is `FAIL simulate` or `FAIL judge`. `not run` and `not judged` do not by themselves fail it.
- [ ] `just validate` prints this same summary on the way out, including when a simulate or a judge has already failed.

## M4: The judge is given what the participant was given (Status: ✅ DONE)

A claim such as "aligned with the ways of working" compares the spec with a file. The judge has only the spec in its prompt, so today it compares the spec with the paraphrase in `JUDGE.md`. A spec that cites `docs/rules/WOW.md` cannot be checked. The prompt therefore has to grow, and the judge stays a reader: no tools, no sandbox over `develop/`. The material is the same files `just prepare` copies, so the judge sees what the participant saw. Verdicts stay on the spec text, and the judge does not run anything.

**Acceptance Criteria:**

- [x] The prompt given to the judge gains a section `# Given to the participant` after `# Material`. It holds every file under `workshop/material/00-base/` and every file under `workshop/material/<delta>/` for each delta `just prepare <lesson>` applies through that lesson, in prepare order. Each file is written as `## <path relative to develop/>` followed by its full text in a fence. A later delta that ships the same path replaces the earlier text, so `CLAUDE.md` for `refine-5` is the `refine-5` copy.
- [x] `just judge refine-4` therefore gives the judge `justfile`, `CLAUDE.md`, `.claude/commands/refine.md`, and `docs/rules/WOW.md`. `just judge refine-1` gives it the base files only. `just judge refine-5` gives it the `refine-5` `CLAUDE.md`.
- [x] The judgement file under `judgements/` records the relative paths that were given, one per line under `given:`, and not their text.
- [x] The judge is still `claude -p` with `--tools ""`. nono's working directory is still `workshop/`. `develop/` is still not in that grant. The material text reaches the judge only through the prompt.
- [x] `workshop/results/refine-4/JUDGE.md` claim 3 reads the spec against the given `docs/rules/WOW.md`. It passes when each tree either states the rules for expected failure, a pure core, and the stack, or cites `docs/rules/WOW.md` as binding, and nothing in the tree contradicts that file. A tree that specifies mutable state, or exceptions as the way to report an expected failure, fails it. A tree that neither states nor cites fails it.
- [x] The `refine-4` fenced prompt in `workshop/JOURNEY.md` no longer repeats the ways of working. Its settled list is the same four bullets as `refine-3` and `refine-5`. The line that begins `Expected failure is Option or Either` is removed.
- [x] A fixture judge prompt built from a fake material tree with two deltas shows the base file, the later copy of a path both deltas ship, and no file from a delta after the named lesson. That test does not start Claude.

**Implementation Details:**

- `scripts/judge-given` prints the section. `just judge` appends it to the prompt and writes the paths under `given:`. A file that contains backticks is fenced with a longer fence.
- Deltas that copy files are `refine-1a`, `refine-4`, `refine-5`, `refine-6`, and `implement-1`, the same set `just prepare` copies. A later file replaces an earlier one at the same path.
- Re-judging the refine-4 tree `2026-09-28-16-17-57`, whose spec cites `docs/rules/WOW.md` and does not state `Option` or `Either`, returned `verdict: pass` once `WOW.md` was in the prompt. The refine-4 prompt no longer repeats that rule.
