# SPEC.v9: Prepare onward, and one store

`just prepare <lesson>` still rebuilds `develop/` from `00-base` through that lesson. That wipe drops `.claude-home`, so a person walking the journey logs in again at every lesson. This spec adds a flag that applies only the deltas still ahead, and then pins two facts the runs keep re-deciding: the store file is `todos.yaml`, and the YAML library is `org.virtuslab::scala-yaml`.

Recorded result trees stay as they are. A tree stamped before this spec may say `todo.yaml` or name another library. This spec does not rewrite `workshop/results/`.

M2 is the generic check, and it comes before any fix. It clusters terms that are close to each other across the journey prompts, the expected observations, and the material. It does not search for a term named in advance. Recorded result trees are not part of that corpus. The first run of that check on the tree as it is today is the reproduction of the splits below; a fix is not accepted until M2 reported the pair it removes.

M3 and M4 pin the store name and the library for every lesson. M5 and M6 are the two discrepancies already found. They stay separate, and they come last, so a general rename is not accepted as the fix until these two cases pass on their own. Each of those two is implemented in order: a test that fails on the tree as it is today, then the change that makes that same test pass. The change is a judge edit when a `JUDGE.md` still requires the observed wording, a material edit when the file the participant reads is the observed wording, or both. Stamped trees and files under `judgements/` are not the fix.

## M1: Prepare can continue from the lesson already applied (Status: ✅ DONE)

The full rebuild stays the default. `keep=yes` starts from the lesson `develop/` was last prepared to and applies the deltas after it.

**Acceptance Criteria:**

- [x] `just prepare <lesson>` deletes `develop/`, rebuilds from `00-base` through that lesson, and prints the lesson, as it does today. It records that lesson as the one `develop/` is prepared to.
- [x] `just prepare <lesson> keep=yes` does not delete `develop/`, does not run `git init`, and does not remove `develop/.claude-home`. It applies each delta strictly after the recorded lesson, through `<lesson>`, in journey order, and then records `<lesson>`.
- [x] The record is one lesson id in a file outside `develop/`. `develop/` does not contain that file. A delta that copies nothing still advances the record.
- [x] `keep=yes` when the record is missing, names an unknown lesson, or names a lesson that is not the recorded lesson or after it, exits non-zero, prints the reason, and leaves `develop/` unchanged.
- [x] `keep=yes` when `<lesson>` is the recorded lesson changes nothing and exits 0.
- [x] The test points the work directory at a temporary directory. It does not modify this repository's `develop/`, and it does not start Claude.

**Implementation Details:**

- The record is `.prepare-lesson` at the repository root, one lesson id. It is gitignored. `keep=yes` reads it and applies each delta after that id through the named lesson. The same lesson prints the section and does not rewrite the record. A value other than `keep=yes` exits non-zero before any delete.
- Tests set `PREPARE_WORK` and `PREPARE_RECORD`. `sandbox` is `PREPARE_WORK` when that variable is set, so the suite does not write this clone's `develop/` or `.prepare-lesson`.

## M2: Close terms cluster without a named search (Status: ✅ DONE)

A search for one term finds only that term. This milestone clusters tokens that resemble each other, so the next split is reported before anyone names it. Plural against singular, and a synonym that shares most of its characters, both show up as a cluster. A synonym with no shared characters does not. Those pairs are written down by the director, one pair per line, and the check fails when both sides appear.

The similarity is computed in the script. Character trigrams are the embedding. Their cosine is the score. Levenshtein distance is the edit score, and it is the Hamming distance when the two tokens have the same length. No embedding service is called. One corpus and one run produce the same scores again.

**Acceptance Criteria:**

- [x] `just term-drift` reads three sources and nothing else: the fenced prompt under each `*PROMPT TO TEST*` in `workshop/JOURNEY.md`, the bullets under each `*EXPECTED OBSERVATIONS*` in that file, and the text files under `workshop/material/`. It does not read `workshop/results/`, it does not prepare `develop/`, and it does not start Claude.
- [x] A token is a lowercase run of letters, digits, and dots. Tokens shorter than four characters are dropped. A fixed stopword list is dropped. The list is in the script, not in the corpus.
- [x] Two tokens form a cluster when their Levenshtein distance is 1, or when the cosine of their character-trigram vectors is at least `+0.8500`. A token and the same token plus a trailing `s` is reported as `plural`, not as an edit. The cosine prints as a sign and four decimal places. The distance prints as an integer.
- [x] The command prints one line per cluster: the two tokens, the lesson or material path each came from, `plural` or `edit` or `cosine`, and the score. The lines are sorted by token, then by path. A second run on the same corpus prints the same bytes.
- [x] A cluster whose two tokens are listed in `workshop/term-drift-natural.txt` does not fail the command. A cluster whose tokens are listed in `workshop/term-drift-pinned.txt` fails the command. A cluster listed in neither file fails the command. Both files are one pair per line, the two tokens separated by a single space, sorted.
- [x] A fixture whose only pair is `file` and `files`, listed as natural, exits 0. A fixture whose only pair is `todo.yaml` and `todos.yaml`, listed as pinned, exits non-zero and names both tokens. A fixture with `store` and `database` prints no cluster. The test supplies the texts and the two list files. It does not call an embedding service, and it does not start Claude.
- [x] Run on the tree as it is today, before M3 through M6, the command reports the pair `todo.yaml` `todos.yaml` and exits non-zero. That output is kept as the reproduction those milestones refer to.

**Implementation Details:**

- `just term-drift` runs `scripts/term-drift` on the journey, `workshop/material`, `workshop/term-drift-natural.txt`, and `workshop/term-drift-pinned.txt`. A line is `token path token path plural|edit|cosine score`. The path is the lexicographically first lesson id or material path for that token. A trailing `s` is `plural`. Otherwise distance 1 is `edit`, and equal lengths use the Hamming distance. Otherwise the printed cosine, at least `+0.8500`, is `cosine`.
- `workshop/term-drift-pinned.txt` starts with `todo.yaml todos.yaml`. `workshop/term-drift-natural.txt` is empty. `workshop/term-drift-reproduction.txt` is the stdout of this first run. A dot is a token character, so a sentence period stays on the word.
- Use the command to validate a pair you already suspect. The first run is 382 lines, and the store split is one of them: `todo.yaml refine-1 todos.yaml implement-1b/docs/specs/SPEC.v1-todo-list-cli-mvp.md edit 1`. Most other lines are a word against the same word plus a period, a plural, or a one-character edit of unrelated words, so the list is not a way to discover ambiguities from scratch. It is not a quality-gate candidate: a gate that fails on this noise would not be actionable. It is worth keeping as an in-between check. Once a pair is suspected, the line shows whether that pair is present, and whether a fix removed it.

## M3: The store file is todos.yaml everywhere the participant starts (Status: ✅ DONE)

Runs split on `todo.yaml` and `todos.yaml`. The name the journey hands the participant is `todos.yaml`.

**Acceptance Criteria:**

- [x] A search of `workshop/JOURNEY.md` and `workshop/material/` finds the filename `todos.yaml` and does not find the filename `todo.yaml`.
- [x] Each `workshop/results/<lesson>/JUDGE.md` that names the store file names `todos.yaml`. Files under `judgements/` and stamped trees are not edited.
- [x] A lesson prompt that does not mention the store is left unchanged.
- [x] After this milestone, `just term-drift` no longer reports the pair `todo.yaml` `todos.yaml`. That pair stays listed in `workshop/term-drift-pinned.txt`, so it fails again when it returns.
- [x] The test is a search of those paths. It does not start Claude.

**Implementation Details:**

- `workshop/material/` already said `todos.yaml`. The rename is the eleven `todo.yaml` names in `workshop/JOURNEY.md` and the store-file sentence in `workshop/results/refine-1/JUDGE.md`, `refine-1a/JUDGE.md`, and `refine-2/JUDGE.md`. Prompts that do not mention the store are untouched. Stamped trees and files under `judgements/` still say `todo.yaml`.
- `workshop/term-drift-pinned.txt` still lists `todo.yaml todos.yaml`. The live command no longer prints that pair. `workshop/term-drift-reproduction.txt` still has the line from the first run. M6's failing-before-the-fix step cannot be replayed on this tree; putting `todo.yaml` back into the refine-1 prompt is the check that still fails.

## M4: One YAML library is stated up front (Status: ✅ DONE)

The library is `org.virtuslab::scala-yaml`. It is named where the participant first reads the task, and nowhere does the material name a second library.

**Acceptance Criteria:**

- [x] The fenced prompt of `refine-1` contains `org.virtuslab::scala-yaml` and `todos.yaml`. The expected observations of that lesson say the spec states that library and that filename.
- [x] `workshop/material/refine-4/docs/rules/WOW.md` names `org.virtuslab::scala-yaml` in its stack section and names no other YAML library.
- [x] A search of `workshop/JOURNEY.md` and `workshop/material/` finds no `circe-yaml`, no `SnakeYAML`, and no `snakeyaml`. Every `scala-yaml` in those trees is the `org.virtuslab` coordinate.
- [x] `workshop/results/refine-1/JUDGE.md` requires the spec to state that library and `todos.yaml`. Stamped trees and judgement files are not edited.
- [x] The test is a search of those paths. It does not start Claude.

**Implementation Details:**

- The refine-1 prompt, and the five later prompts that repeat that sentence, name `org.virtuslab::scala-yaml` next to `todos.yaml`. The refine-1 observations say the spec states both. The WOW stack names that coordinate and no other YAML library. Bare `scala-yaml` mentions in the quality-gates material now carry the same coordinate. `org.virtuslab:scala-yaml` and `"org.virtuslab" %% "scala-yaml"` stay; both are that coordinate. Stamped trees are not edited.

## M5: CLAUDE.md no longer stands in for WOW.md (Status: ✅ DONE)

Observed. `workshop/material/00-base/CLAUDE.md` opens with "A command-line todo list in Scala 3. Pure functional core, Cats Effect at the edge, one YAML file as the store." That is the lesson prompt, shortened, sitting in the file the agent reads as rules. `docs/rules/WOW.md` is not in that tree. From refine-5 on, `CLAUDE.md` repeats the same sentence and then substitutes a shorter list — "pure FP, fail fast, illegal states unrepresentable, outcomes in the return type, TDD, no mocks" — for the file it points at. The agent follows the paraphrase. WOW.md has less effect.

Expected. `CLAUDE.md` does not contain the lesson prompt. Where WOW.md is in the tree, `CLAUDE.md` names `docs/rules/WOW.md` as the binding rules and does not restate them.

**Acceptance Criteria:**

- [x] Before any edit for this milestone, one test fails on the current tree. It fails because `workshop/material/00-base/CLAUDE.md` contains "A command-line todo list in Scala 3. Pure functional core, Cats Effect at the edge, one YAML file as the store.", and because `workshop/material/refine-5/CLAUDE.md` and `workshop/material/refine-7/CLAUDE.md` contain "pure FP, fail fast, illegal states unrepresentable, outcomes in the return type, TDD, no mocks." That failure is the reproduction. The test does not start Claude.
- [x] The same test passes only after the fix. No `CLAUDE.md` under `workshop/material/` contains that sentence. `workshop/material/00-base/CLAUDE.md` does not name `docs/rules/WOW.md`, because that file is not in the tree until refine-4. `workshop/material/refine-5/CLAUDE.md` and `workshop/material/refine-7/CLAUDE.md` each contain `docs/rules/WOW.md` and say that file is binding, and neither contains the paraphrase.
- [x] Putting the observed sentence back into `workshop/material/00-base/CLAUDE.md` makes the same test fail again.
- [x] A `JUDGE.md` that requires a spec or a file to contain the observed sentence or the paraphrase is updated in this milestone so that it requires the expected wording instead. A `JUDGE.md` that does not require either is left unchanged. Stamped trees and files under `judgements/` are not edited.

**Implementation Details:**

- The three `CLAUDE.md` files no longer open with the lesson sentence. `refine-5` and `refine-7` name `docs/rules/WOW.md` and say that file is binding, without the paraphrase. `00-base` does not name `docs/rules/WOW.md`. No `JUDGE.md` required the sentence or the paraphrase, so none were edited. Putting the sentence back into `workshop/material/00-base/CLAUDE.md` fails the same test.

## M6: The prompt and the refine-6 spec name the same store file (Status: ✅ DONE)

Observed. The refine-1 prompt, and the lessons that repeat it, say the store is `todo.yaml`. `workshop/material/refine-6/docs/specs/SPEC.v1-todo-list-cli-mvp.md` says `todos.yaml`, and implement-1 starts from that spec. The two names came from independent runs of the early prompts, then one of them was copied in as the starting spec. M2 reports this pair before any fix.

Expected. The prompt the participant sees before refine-6 names `todos.yaml`, and the spec refine-6 copies in names `todos.yaml`. implement-1 does not inherit a second name.

**Acceptance Criteria:**

- [x] Before any edit for this milestone, one test fails on the current tree. It fails because a fenced prompt from `refine-1` through `refine-5` contains `todo.yaml`, or because `workshop/material/refine-6/docs/specs/SPEC.v1-todo-list-cli-mvp.md` and that prompt name different store files. That failure is the reproduction. The test does not start Claude.
- [x] The same test passes only after the fix. Every fenced prompt in `workshop/JOURNEY.md` from `refine-1` through `refine-5` that names a store file names `todos.yaml` and does not name `todo.yaml`. The expected observations of `refine-1` say `todos.yaml`. `workshop/material/refine-6/docs/specs/SPEC.v1-todo-list-cli-mvp.md` contains `todos.yaml` and does not contain `todo.yaml`. No file under `workshop/material/implement-1/` contains `todo.yaml`.
- [x] Putting `todo.yaml` back into the refine-1 prompt makes the same test fail again.
- [x] A `JUDGE.md` that requires `todo.yaml` for one of these lessons is updated in this milestone so that it requires `todos.yaml`. A `JUDGE.md` that does not name a store file is left unchanged. Stamped trees and files under `judgements/` are not edited.

**Implementation Details:**

- M3 already renamed the prompts and the three judges, and `workshop/material/refine-6/docs/specs/SPEC.v1-todo-list-cli-mvp.md` already said `todos.yaml`, so the failing-before-the-fix step cannot be replayed on this tree. This test is the lock: the refine-1 through refine-5 prompts that name a store name `todos.yaml`, the refine-1 observations say `todos.yaml`, the refine-6 spec says `todos.yaml`, and `workshop/material/implement-1/` does not say `todo.yaml`. Putting `todo.yaml` back into the refine-1 prompt fails that test. `workshop/term-drift-reproduction.txt` is unchanged. Stamped trees still say `todo.yaml`.

## M7: The journey is a flat list of lesson slugs (Status: IMPLEMENTED)

`# Refine` and `# Implement` no longer describe the journey. Quality gates and skills sit under Implement today even though they are not implement lessons. Lesson order is also duplicated in the justfile and in several Python scripts. The journey file becomes the only list.

**Acceptance Criteria:**

- [x] Every lesson in `workshop/JOURNEY.md` is a top-level heading `# <slug>: <title>`. There is no `# Refine` heading and no `# Implement` heading. A heading that is not a lesson stays out of the order.
- [x] `scripts/lesson-order` prints one lesson id per line, in file order, by reading those headings. It is awk. `just prepare`, `just simulate`, and `just validate` use that list and no longer hardcode the lesson names.
- [x] The Python scripts that walk the journey (`lesson-status`, `instruct`, `judge-given`, `prompt-distance`, `term-drift`, `ambiguity-check`, `participant-session`) read the same heading shape and the same order. They do not keep a separate `ORDER` tuple of lesson ids.
- [x] `just prepare <lesson>` still prints that lesson's section. A lesson heading with no `_delta-<slug>` recipe fails when prepare reaches it.
- [x] The test supplies a fixture journey and asserts the printed order and the section boundaries. It does not start Claude.

**Implementation Details:**

- Lessons are `# <slug>: <title>` only. `scripts/lesson-order` (awk) and `scripts/journey.py` share that shape. `just prepare`, `simulate`, and `validate` call `lesson-order`; the Python walkers import `journey`. Non-slug `#` headings are ignored by the order. `EXPECTED` paths in `lesson-status` and `COPIES` in `judge-given` stay as per-lesson maps, not order lists.

