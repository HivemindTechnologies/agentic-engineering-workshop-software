# SPEC.v15: Steep todo-app succession and redundancy gates

After quality-gates-3, the workshop has a deterministic `just spec-check` and skills that call it, but the in-sandbox todo CLI is still the slow material path. This spec jumps: take the refined **develop_quality-gates-3.v1** product SPEC from a live quality-gates-3 simulate stamp as the baseline, grow **develop_*.v2–v4** (output formats → configuration plane → due dates / priorities / tags / assignees), implement that product in a harness-side `app/` tree tagged `app-v1` … `app-v4`, then add **quality-gates-4** around a JVM copy/paste (redundancy) detector, a skill that turns its report into actionable signals, and a lesson that drives the app-v4 codebase quiet under that gate.

**Notation.** This file is an *outer* harness spec under `docs/specs/`. Its milestones are **outer.v15.M…** (e.g. `outer.v15.M1`). Product specs that live in a sandbox as `develop/docs/specs/…` are written **develop_<lesson>.vM** — e.g. `develop_quality-gates-3.v1` is the structure-checked todo SPEC.v1 for that lesson, not an outer.v1. Bare “v2/v3/v4” in headings below always means the develop-side product line unless prefixed with `outer.`.

Library and version pins (PureConfig, Typesafe Config / HOCON, Decline or hand-rolled CLI, PMD CPD vs another Scala/Java CPD, ANSI/markdown/JSON renderers) are chosen during the refine and implement milestones below — not in this preamble. Prefer tools already reachable from the develop shell’s JDK/sbt world; do not edit root `flake.nix` unless a later packaging milestone explicitly owns that thaw (see outer.v13.M13 / outer.v14).

Capture interesting commits and abstraction moves during `app/` implementation so later material can replay “find an abstraction / push responsibility” stories, not only the final tree.

## M1: Simulate quality-gates-3 and capture the result tree (Status: ✅ DONE)

The product baseline is whatever structure-check + skill run leaves in `develop/` after quality-gates-3. Directors need that tree stamped before rewriting follow-on develop-side SPECs (**outer.v15.M2a–M2c**).

**Acceptance Criteria:**

- [x] A scripted simulate (or validate) of `quality-gates-3` completes and writes a result stamp under `workshop/results/quality-gates-3/` that includes the full develop tree (outer.v13 full-tree capture) and a `TREE` file when that harness path is active.
- [x] The stamp contains `develop/docs/specs/` product file that is **develop_quality-gates-3.v1** (filename `SPEC.v1-*.md` or the lesson’s agreed v1 name) — the structure-checked baseline for outer.v15.M2a–M2c.
- [x] Journey / status for quality-gates-3 can name that stamp (heading mark or status.yaml). The test asserts the stamp path, presence of develop_quality-gates-3.v1, and `TREE` (or documents why TREE is absent). It does not require a human Claude session beyond the harness simulate path.

**Implementation Details:**

- Stamp `workshop/results/quality-gates-3/2026-09-30-03-19-22` from `nix develop --command just -- simulate quality-gates-3`. Added `quality-gates-3` to `scripts/lesson-forks` PATHS (`SPEC` + `.githooks/pre-commit`) and `workshop/results/quality-gates-3/JUDGE.md` so simulate could start.
- develop_quality-gates-3.v1 file: `docs/specs/SPEC.v1-todo-list-cli-mvp.md` in the stamp (passes structure check). Hook runs `just check` then `just spec-check`.
- Tests: `tests/v15_quality_gates3_stamp_test.py`.
- The first `quality-gates-3` judgement was a hand-written note. It was replaced by a real `just judge` pass (quoting the hook and the spec headings) once the judge could see non-markdown expected files and no longer died on nono's log noise (`justfile` judge recipe: tolerant `jq`, expected files shown, spec = the lesson's expected `.md` only). `status.yaml` now reads PASS for the lesson (`scripts/lesson-status` EXPECTED gained `quality-gates-3`).

## M2a: Refine develop_*.v2 — output formats (Status: ✅ DONE)

On top of **develop_quality-gates-3.v1** from outer.v15.M1, add a second product SPEC (**develop_app.v2**) for richer output: at least JSON, Markdown, and ANSI/colored human output, without yet adding a configuration plane.

**Acceptance Criteria:**

- [x] A new product spec file exists under `develop/docs/specs/` (and/or `app/docs/specs/` as Implementation Details will name) as **develop_*.v2** for the todo CLI, with milestones and acceptance criteria covering JSON, Markdown, and ANSI/color (or equivalent human) list/render modes.
- [x] develop_*.v2 is derived from develop_quality-gates-3.v1 (commands and store stay coherent; non-goals that move to develop_*.v3 / develop_*.v4 are explicit). Sandbox `just spec-check` passes on it.
- [x] The test asserts the file exists, names the formats in criteria, and passes outer `scripts/spec-check` (or the Scala checker) on it. It does not start Claude.

**Implementation Details:**

- Lesson/workspace id: `app`. File: `app/docs/specs/SPEC.v2-todo-list-cli-output-formats.md` (develop_app.v2).

## M2b: Refine develop_*.v3 — configuration plane (Status: ✅ DONE)

Add configuration: environment-variable reading and an application config file via Typesafe Config (HOCON) loaded with PureConfig (or the pinned equivalent), with clear precedence documented in **develop_app.v3**.

**Acceptance Criteria:**

- [x] A **develop_*.v3** product file exists with milestones for env-var access, a PureConfig (or named) reader over Typesafe Config / HOCON application config, and how those settings affect CLI defaults or render/store paths without breaking develop_*.v1 / develop_*.v2 behavior when unset.
- [x] Library coordinates and versions are named in the SPEC criteria or an adjacent WOW/rules pin so implement does not guess Maven probes (same spirit as outer.v13.M2e).
- [x] Outer or sandbox spec-check passes on the file. The test asserts env/config keywords and the pin. It does not start Claude.

**Implementation Details:**

- File: `app/docs/specs/SPEC.v3-todo-list-cli-config.md`. Pins PureConfig `0.17.8`; precedence CLI → env → application.conf → defaults.

## M2c: Refine develop_*.v4 — due dates, priorities, tags, assignees (Status: ✅ DONE)

Steepen the domain in **develop_app.v4**: due dates, priorities, tags, and an assigner / assignee group with email addresses for later notification (notification transport itself may stay a non-goal).

**Acceptance Criteria:**

- [x] A **develop_*.v4** product file exists with milestones covering due dates, priorities, tags, and assignee/assigner (including email as identity), each mapped to checkable criteria and store/CLI surface area.
- [x] Non-goals state what is deferred (e.g. actual SMTP send). The SPEC stays coherent with develop_*.v1–v3. Spec-check passes.
- [x] The test asserts those feature names appear in criteria and the checker passes. It does not start Claude.

**Implementation Details:**

- File: `app/docs/specs/SPEC.v4-todo-list-cli-planning.md`. Tests: `tests/v15_develop_app_specs_test.py`.

## M3a: Implement remaining develop_*.v1 in `app/` and tag `app-v1` (Status: ✅ DONE)

Implement the product against **develop_quality-gates-3.v1** (finish any PENDING milestones) in a harness-side `app/` tree (not by mutating workshop material mid-flight), using the refine/implement skills. Tag when develop_*.v1 is green.

**Acceptance Criteria:**

- [x] An `app/` directory (path exact unless Implementation Details rename it) holds the todo CLI sources, build, and the develop_*.v1 SPEC in use. Remaining develop_*.v1 milestones are IMPLEMENTED or ✅ DONE with tests; `just check` (or the app’s agreed gate) exits 0.
- [x] Git tag `app-v1` points at that commit on the branch used for this work. A captured tree listing or stamp note exists for later material hooks.
- [x] The test asserts `app/` layout, tag presence (or a documented freeze file listing the tag SHA), and a green check command. It does not start Claude.

**Implementation Details:**

- Seeded from `workshop/results/quality-gates-3/2026-09-30-03-19-22`. Finished develop_app.v1 M5–M8 (table, updates, colors, `--output=yaml`).
- Tree capture: `app/snapshots/app-v1.TREE`. Tag: `app-v1`. Tests: `tests/v15_app_v1_test.py`.

## M3b: Implement develop_*.v2, capture tree, tag `app-v2` (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] develop_*.v2 milestones are implemented in `app/` with tests; output formats from outer.v15.M2a work as specified. Tag `app-v2` is set. A file-tree capture suitable for later workshop material exists (stamp, `TREE`, or committed snapshot under a named path).
- [x] The test asserts tag `app-v2`, format-related tests or CLI fixtures, and the capture artifact. It does not start Claude.

**Implementation Details:**

- `--format=json|markdown|table|yaml` (legacy `--output=` kept). Capture: `app/snapshots/app-v2.TREE`. Tests: `tests/v15_app_v2_test.py`.

## M3c: Implement develop_*.v3, capture tree, tag `app-v3` (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] develop_*.v3 milestones are implemented in `app/` with tests; config/env behavior matches outer.v15.M2b. Tag `app-v3` is set. Tree capture for later material exists.
- [x] The test asserts tag `app-v3`, config-related tests, and the capture artifact. It does not start Claude.

**Implementation Details:**

- `pureconfig-core` 0.17.8; `todo.config.AppConfig`; capture `app/snapshots/app-v3.TREE`. Tests: `tests/v15_app_v3_test.py`.

## M3d: Implement develop_*.v4, capture tree, tag `app-v4` (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] develop_*.v4 milestones are implemented in `app/` with tests; due dates, priorities, tags, and assignees/emails behave as specified. Tag `app-v4` is set. Tree capture for later material exists.
- [x] Commits during outer.v15.M3a–M3d that demonstrate useful abstractions or redundancy removal are listed or linkable (short log excerpt or note file) for curriculum reuse.
- [x] The test asserts tag `app-v4`, domain-feature tests, capture artifact, and presence of the commit/note list. It does not start Claude.

**Implementation Details:**

- Capture `app/snapshots/app-v4.TREE`; notes `app/snapshots/ABSTRACTION_NOTES.md`. Tests: `tests/v15_app_v4_test.py`.
- `app/snapshots/TAGS` now records the commit each live tag points at (`app-v4` was stale, `app-v4-quiet` missing); `tests/v15_tags_freeze_test.py` compares the file with the live tags and the ancestry chain. `assigner` is now a table and Markdown column, not only JSON/YAML (`RendererSuite`).

## M4a: Integrate a JVM copy/paste detector and capture a first report (Status: ✅ DONE)

Add PMD CPD or another Java/Scala-usable copy/paste detector to the `app/` (or workshop gate) build so redundancy is a deterministic signal.

**Acceptance Criteria:**

- [x] The chosen tool is wired into the build or a `just` recipe (name pinned in Implementation Details) and runs without network probing at check time when caches are warm.
- [x] A first report artifact is captured (path named) from the app-v4 (or current) tree. The tool version/coordinate is pinned.
- [x] The test runs the recipe on a fixture or the app tree and asserts the report file exists and is non-empty when duplicate fixtures are present (or documents the empty-report case). It does not start Claude.

**Implementation Details:**

- Tool: PMD CPD `7.28.0` (`pmd-core` and `pmd-scala_2.13`), pinned in `app/scripts/check-redundancies-cpd/build.sbt`. A small Scala main (`CheckRedundancies.scala`) drives CPD's API and writes the JSON report; `app/scripts/check-redundancies` is a Bash launcher that builds the classpath once and runs `java`, the same shape as `scripts/spec-check-scala/run`. JDK and sbt only, no Python. Recipe: `just check-redundancies`. First report: `app/snapshots/redundancy-report-v4.json` (PMD, pre-fix `app-v4` tree).
- The first run builds the tool and fetches the pinned PMD jars into the shared coursier cache; later runs are offline.
- The earlier bespoke Python detector is deleted. Default minimum is 50 tokens (PMD's own default is 100). The block that detector found in `Todos.scala` is 34–35 tokens, so CPD reports it at a minimum of 35 or lower, but that also adds five to seven small findings in test scaffolding; 50 keeps the signal actionable.
- Known limit: PMD's Scala CPD compares tokens verbatim and `--ignore-identifiers` has no effect for Scala, so a copy with every identifier renamed is not found. The tool does not offer that flag (`tests/v15_redundancy_gate_test.py` records the limit).

## M4b: `check-redundancies` skill surfaces top findings (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] A Claude skill (workshop material path named in Implementation Details) invokes the CPD/redundancy integration and presents the top findings ordered by size or impact (criterion states the ranking rule).
- [x] The skill description triggers on redundancy / copy-paste / CPD language. The test asserts skill files and a dry-run or fixture-based ordering assertion. It does not start Claude.

**Implementation Details:**

- Skill: `app/.claude/skills/check-redundancies/SKILL.md` and `workshop/material/quality-gates-4/.claude/skills/check-redundancies/SKILL.md`. Ranking: lines × occurrences.

## M4c: Verbosity parameters for the redundancy check (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] The recipe and/or skill accept parameters (CLI flags or env) to increase or decrease verbosity / report volume. Defaults stay quiet enough for CI.
- [x] The test covers at least two verbosity levels with different output size or section presence. It does not start Claude.

**Implementation Details:**

- `--verbosity quiet|normal|verbose` (quiet omits snippets).
- `just check-redundancies` takes `verbosity=…`, `report=…` and passes any other argument to the tool, so `just check-redundancies --fail-on-findings` works. Before this it bound the flag to `verbosity` and exited 2. Material and `app/` carry the same recipe (`tests/v15_quality_gates4_lesson_test.py`).

## M4d: Allowlist / blocklist or inline suppressions for known redundancies (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] Maintainers can exclude or include paths/rules via config and/or suppress a finding with an explicit code comment (or equivalent) on a branch or region. Behavior is documented in the skill or WOW snippet.
- [x] The test shows a suppressed duplicate no longer fails (or no longer appears at the default verbosity) and an unsuppressed one still does. It does not start Claude.

**Implementation Details:**

- `--allow` globs exclude paths. A region is silenced with PMD's own `// CPD-OFF` ... `// CPD-ON` comments, so the marker is region-scoped and the rest of the file still counts. Fixtures under `app/testdata/redundancy/` (`dup` fails, `suppressed` wraps one copy in `CPD-OFF`/`CPD-ON` and passes). The skill documents both.

## M5a: Run the redundancy gate on `app-v4` (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] Against the `app-v4` tree, the redundancy check runs and produces a report (fail or pass). Findings are recorded for outer.v15.M5b.
- [x] The test asserts the command exit contract and report path for that tree. It does not start Claude.

**Implementation Details:**

- Captured pre-fix report: `app/snapshots/redundancy-report-v4.json` (PMD CPD over the tagged `app-v4` tree, 2 findings, both the repeated read-the-store prelude in `Cli.scala`; the tool was added after the tag, so HEAD's tool was run against the tag's `src`).

## M5b: Lesson + skill to reduce redundancies with refactor guidance (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] A new journey lesson (quality-gates-4 or the agreed id) uses the gate output and asks the participant to reduce findings; material includes the CPD wiring from outer.v15.M4.
- [x] A skill (or extension of outer.v15.M4b) proposes concrete refactor moves when something is found: parameterize a function, introduce an abstraction, push code up/down the call hierarchy, or localize responsibility in the domain model.
- [x] Expected observations name a quieter report after fixes. The test asserts lesson section, material paths, and skill guidance phrases. It does not start Claude.

**Implementation Details:**

- Lesson id: `quality-gates-4`. Material: `workshop/material/quality-gates-4/` (the pre-fix `app-v4` sources, the PMD CPD launcher and pinned project, the skill, and the recipe).
- The lesson is registered (`_delta-quality-gates-4`, `lesson-forks`, `lesson-status`, `judge-given`, a `JUDGE.md`). A real run against the PMD material passed simulate and judge (stamp `2026-09-30-09-12-10`): PMD reported the repeated read-the-store prelude in `Cli.scala`, the participant extracted a shared `withStore` helper, `just check-redundancies --fail-on-findings` then reported 0 findings with no `CPD-OFF` or allow markers, and `just check` stayed green (39 tests). The build of the pinned tool inside the sandbox worked on that run.
- The judge recipe was fixed on the way (tolerant `jq`, expected non-markdown files shown, spec = the lesson's expected `.md` only), see M1.

## M5c: Stable quiet baseline for the redundancy check (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] On the agreed baseline tree (app-v4 after outer.v15.M5b fixes, or a tagged `app-v4-quiet`), the redundancy check exits 0 with no actionable findings at default verbosity (allowlisted/suppressed items documented).
- [x] A baseline freeze (file or tag) prevents silent drift; refreshing it is deliberate. The test asserts exit 0 and baseline presence. It does not start Claude.

**Implementation Details:**

- Baseline: `app/snapshots/redundancy-baseline.json` (PMD, finding_count 0). Also `redundancy-report-quiet.json`. To reach it the `Cli.scala` prelude was extracted into `withStore`; `just check` stays green (41 tests). The `app-v4-quiet` tag still marks the earlier Python-era quiet commit, where PMD reports the `Cli.scala` findings; the baseline file and the harness test that runs the tool over `app/src` are what guard drift now.
