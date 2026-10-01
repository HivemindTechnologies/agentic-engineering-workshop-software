# SPEC.v8: Quality gates

These gates belong to the outer repository. A commit on this repo runs them from a tracked pre-commit hook. The hook uses the Python already installed on the machine. The flake does not gain Python.

`just test` is the harness unit-test recipe. `just check` inside `develop/` stays the Scala gate. This spec does not add an outer `just check`, and the hook does not run the Scala gate.

v4.M3 is a later lesson inside `workshop/JOURNEY.md`, where the participant installs a hook that runs that Scala `just check`. This spec does not add a lesson and does not edit `develop/`.

The hook grows in order. M1 runs the unit tests. M2 adds the spec checker after those tests pass. M3 adds the smooth-journey check after the spec checker passes. A failing step stops the hook. M4 writes `workshop/results/status.yaml` so the same measures can be read with `yq`. That file is a report. The hook does not read it and does not write it. The next gates, not written here, are a Python linter and a Python formatter. This hook does not run them.

## M1: The pre-commit hook runs just test (Status: ✅ DONE)

One tracked hook script is the only pre-commit check. Installing it points this clone at that script.

**Acceptance Criteria:**

- [x] `hooks/pre-commit` is a tracked executable. Its first check runs `just test` from the repository root and exits with that command's status.
- [x] `just install-hooks` sets this clone's `core.hooksPath` to `hooks` and changes no other git config. A second run leaves the same path.
- [x] In a temporary git repository whose hook is this script, a commit is rejected when `just test` exits non-zero, and a commit is created when `just test` exits 0. The test supplies the `just` command. It does not run the real suite, start Claude, or run sbt.
- [x] The hook does not start Claude and does not run a command inside `develop/`.

**Implementation Details:**

- `hooks/pre-commit` is the hook. `just install-hooks` runs `scripts/install-hooks`, which sets only `core.hooksPath` to `hooks`. The tests call that script on a temporary repository, so the suite does not change this clone. Run `just install-hooks` once to turn the hook on here.

## M2: The hook checks every spec (Status: ✅ DONE)

After the unit tests pass, the same hook checks the specs with the one checker from v5.M1.

**Acceptance Criteria:**

- [x] When `just test` exits 0, `hooks/pre-commit` runs `scripts/spec-check` once per file `docs/specs/SPEC.*.md`, from the repository root, and exits 0 only when every file exits 0.
- [x] When `just test` exits non-zero, the hook exits with that status and does not run `scripts/spec-check`.
- [x] When `scripts/spec-check` fails, the hook exits non-zero and the checker's `path:line` line is visible. The hook does not print a second diagnosis.
- [x] `scripts/spec-check docs/specs/SPEC.v8-quality-gates.md` exits 0.
- [x] The test uses a fixture spec and a stand-in for `just test`. It does not start Claude.

**Implementation Details:**

- After `just test` exits 0, the hook runs `scripts/spec-check` on each `docs/specs/SPEC.*.md`. A shell `nullglob` means a repository with no such file skips this step. The hook adds no message of its own when the checker fails.

## M3: The hook requires a smooth journey (Status: ✅ DONE)

After the specs pass, the same hook reads the recorded judgements. Smooth has the meaning from v7.M4: a lesson with `workshop/results/<lesson>/JUDGE.md` whose newest in-range judgement line is `verdict: pass`. A lesson with no `JUDGE.md` does not fail this gate.

**Acceptance Criteria:**

- [x] When `just test` and every `scripts/spec-check` exit 0, `hooks/pre-commit` checks each lesson in journey order and exits 0 only when every lesson that has a `JUDGE.md` is smooth.
- [x] A lesson with no `JUDGE.md` does not fail the hook. The hook prints `<lesson> not yet judged` for it and continues.
- [x] The first lesson that has a `JUDGE.md` and whose newest in-range verdict is not `pass` makes the hook exit non-zero. The hook names that lesson and does not check the lessons after it.
- [x] The check does not edit `workshop/JOURNEY.md`, does not prepare `develop/`, and does not start Claude. It does not call `just instruct`.
- [x] When `just test` or `scripts/spec-check` exits non-zero, the hook exits with that status and does not read a judgement.
- [x] The test builds the result trees in a temporary directory. It does not start Claude.

**Implementation Details:**

- The hook then runs `scripts/lesson-status smooth`. A lesson with no `JUDGE.md` prints `<lesson> not yet judged`. The first judged lesson whose newest in-range verdict is not `pass` prints `<lesson> not smooth` and the hook exits. Passing lessons are not printed. The hook does not call `just instruct`.

## M4: The last run of each lesson is one YAML file (Status: ✅ DONE)

`scripts/lesson-status lines` prints the measures and does not save them. The raw numbers stay inside each run's `session.jsonl`. This milestone writes one file for the newest in-range run of every lesson.

**Acceptance Criteria:**

- [x] `just status` writes `workshop/results/status.yaml` and prints nothing. It does not prepare `develop/`, does not edit `workshop/JOURNEY.md`, and does not start Claude. A second run on the same trees writes the same bytes.
- [x] `just validate` writes that same file after the lessons it was asked to visit. The file still lists every lesson in journey order, including a lesson that this validate did not visit.
- [x] The document has `baseline_wall_seconds` and a `lessons` list. Each lesson entry has `lesson`, `status`, `stamp`, `verdict`, `interactions`, `length`, `wall_seconds`, and `capped`, in that order. `status` is `PASS`, `FAIL simulate`, `FAIL judge`, or `not run`. `verdict` is `pass`, `fail`, or null. `capped` is `true` or `false`.
- [x] A lesson with no in-range tree has `status: not run`, and `stamp`, `verdict`, `interactions`, `length`, and `wall_seconds` are null. `baseline_wall_seconds` is the sum of the non-null `wall_seconds` values. A missing wall record is null, not 0.
- [x] The test builds the result trees in a temporary directory and compares the written file to a known document. It does not start Claude.

**Implementation Details:**

- `scripts/lesson-status yaml` writes the file and prints nothing. `just status` calls it with `@`, so the recipe line is hidden too. `just validate` calls the same writer after its lesson loop, on the whole results directory. The hook does not read or write this file. The document is emitted without a YAML library so a second run writes the same bytes. `baseline_wall_seconds` is 0 when every `wall_seconds` is null; that 0 is the sum.
