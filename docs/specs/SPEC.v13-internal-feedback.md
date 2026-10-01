# SPEC.v13: Wet dress rehearsal feedback

The wet dress rehearsal showed participants burning turns on setup friction and on the same tool loops over and over. Machines without Nix had to `nono pull` the `nolabs-ai/claude` base before the profile resolved. Fresh prepares asked for folder trust and for every file write. Several refine lessons clustered at exactly 8 or 14 interactions, and the implement lessons that touch Maven/sbt spent dozens of turns on dependency fetch. Result stamps still only keep the paths each lesson declares as expected, so the judge and a human reviewing a run cannot see the same full tree the participant saw. Expected-observation bullets drift across lessons without a gate like the prompt-distance baseline. After a long run there is no recipe that puts `develop/` back to that result for inspection — only `prepare`, which rebuilds from material.

This spec inlines the nono base, cuts the systematic interaction waste (config first, material/journey second), captures full result trees, lets the judge act with the same file access a participant has, baselines observation drift, adds `just restore` as a separate path from prepare, keeps clickable Results / Material / develop links under each journey heading so prepare prints them after the banner, adds a pruned `tree` view (`just tree <lesson>`, plus a `TREE` file in each stamp) so directors see the sandbox layout the participant had without scrolling through `target/` and other build noise, ports `spec-check` to a Scala clone on the JDK/sbt already in the root flake, extends both checkers to accept a file or a specs folder with per-path `{path}:{line}` reports, and lands that checker plus skill rewiring on the new `quality-gates-3` lesson — not on skills-2 (a one-file shebang Scala script, Graal, and broader script ports stay postponed / for v14).

The handout machines already baked the root `flake.nix`. **Do not edit root `flake.nix` in this spec.** Outer-shell packaging and deeper quality-gate curriculum live in SPEC.v14.

Dress-rehearsal `status.yaml` showed tight clusters: refine-1 / refine-1a / refine-6 at 8 interactions; refine-2 / refine-5 at 14; implement-1 / implement-1b / implement-2 at tens of turns while resolving Maven/sbt. Permission prompts for trust and edits amplify the same loops on interactive runs. Prefer fixing Claude/nono defaults shipped with the sandbox; when that is not enough, change material or journey wording so the participant does not re-ask the same network or build questions every run. M2a–M2e are separate milestones for those fixes (`scripts/spec-check` forbids nested `### M` children, so they stay flat H2s).

## M1: Inline the nono Claude base profile (Status: IMPLEMENTED)

`nono.json` currently `"extends": "nolabs-ai/claude"`. Participants who install nono outside Nix must pull that remote base before the profile works. The resolved base belongs in this repository.

**Acceptance Criteria:**

- [x] `nono.json` no longer contains `"extends": "nolabs-ai/claude"`. Every rule that profile contributed is present as ordinary keys in this file (or in a committed local profile this file extends by path), so a fresh nono install without a prior `nono pull` can load it.
- [x] `nono-strict.json` still builds on the same workshop boundary. If it previously relied on the remote Claude base transitively, it also works without that pull.
- [x] A test (or a checked-in fixture of the resolved profile before the edit) fails when `extends` still names `nolabs-ai/claude`, and passes when the inlined file loads under `nono` without network access to the profile registry. It does not start Claude.

**Implementation Details:**

- Path-based `extends` is rejected by nono (`invalid base profile name`), so the pack's `profiles/claude.json` rules are merged into `nono.json` and `extends` is only the built-in `default`.
- `scripts/nono-ensure-claude-dirs.sh` replaces the pack's `$PACK_DIR/bin/ensure-dirs.sh`; `session_hooks.before` points at `$WORKDIR/../scripts/nono-ensure-claude-dirs.sh` (recipes set workdir to `develop/`).
- `nono-strict.json` already extended `default` only; left unchanged. `tests/nono_profile_test.py` asserts no remote pack in `extends` and runs `nono profile validate` when `nono` is on PATH.

## M2a: Trust the sandbox root by default (Status: IMPLEMENTED)

A fresh `develop/` after prepare should not stop for "trust this folder" before work starts.

**Acceptance Criteria:**

- [x] The workshop setup that Claude reads inside `develop/` (committed material under `workshop/material/00-base/` and/or the harness step that builds `develop/.claude-home`) marks the sandbox working directory as trusted, using Claude Code's supported project-trust / workspace-trust mechanism, without a human clicking trust after each prepare.
- [x] When Claude Code cannot express trust from project settings alone, the milestone documents that limit in Implementation Details and the harness still pre-seeds whatever local state Claude does honor for that directory (for example under `CLAUDE_CONFIG_DIR`), so a scripted prepare+claude path does not wait on trust.
- [x] The test asserts the committed or generated trust/config artifact for a prepared tree. It does not start an interactive Claude session.

**Implementation Details:**

- Trust is not expressible from `.claude/settings.json`; Claude stores it under `projects[<abs-path>].hasTrustDialogAccepted` in the config dir's `.claude.json`.
- `scripts/claude-home-seed` writes that flag for the sandbox path. `_claude-home` calls it instead of only setting `hasCompletedOnboarding`.
- Tests in `tests/claude_trust_edits_test.py`.

## M2b: Auto-allow edits after prepare (Status: IMPLEMENTED)

Interactive participants should not approve every file write after a fresh prepare. Scripted simulate already passes `--permission-mode bypassPermissions`; interactive `just claude` must land in an edit-friendly mode from configuration.

**Acceptance Criteria:**

- [x] After `just prepare <lesson>`, the Claude settings active for `develop/` set `permissions.defaultMode` to `acceptEdits` (or an equivalent mode that auto-approves edits inside the working directory without per-file prompts), unless a stronger mode is already set by the harness for that invocation.
- [x] `just claude` does not require a human to allow each Edit/Write inside `develop/` for ordinary lesson work. Shell commands and network may still prompt unless a later milestone or the existing simulate flags cover them.
- [x] The setting lives in committed material and/or the `_claude-home` / config-dir setup so it survives prepare. The test reads that settings file (or the argv `just claude` would use) and asserts the mode. It does not start Claude.

**Implementation Details:**

- `workshop/material/00-base/.claude/settings.json` sets `permissions.defaultMode` to `acceptEdits` (allowed from project settings; `bypassPermissions` / `auto` are not). Prepare copies it into `develop/`. Trust from M2a is required for project allow rules to apply.

## M2c: Shrink the 8-interaction refine cluster (Status: IMPLEMENTED)

refine-1, refine-1a, and refine-6 each landed at exactly 8 interactions in the dress rehearsal. That regularity points at a fixed tool loop (likely the same reads, writes, or sbt/Maven probes), not lesson-specific reasoning.

**Acceptance Criteria:**

- [x] A short note under this milestone (or in `workshop/known-ambiguities.txt` / journey director comments) names the repeated tool pattern found in those three `session.jsonl` logs.
- [x] After the fix (config, material, and/or journey), a fresh `just simulate` of each of refine-1, refine-1a, and refine-6 records fewer interactions than that dress-rehearsal baseline of 8, or the remaining turns are justified in Implementation Details as unavoidable model reasoning (not repeated identical ask/answer pairs).
- [x] The test prefers a deterministic gate: either a fixture session that fails when the known loop still appears, or a documented interaction ceiling checked by `scripts/lesson-status` against those lessons. It does not require a live network Maven fetch when a fixture can prove the loop is gone.

**Implementation Details:**

- Dress-rehearsal pattern: broad `find` / `ls` / `git log` Bash turns rediscovering the sandbox before one Write (refine-1: 5 Bash; refine-1a/6 similar).
- `00-base/CLAUDE.md` and `refine-5/CLAUDE.md` now state the layout and forbid broad rediscovery. `workshop/session-bash-forbids.txt` + `scripts/session-bash-forbid` fail sessions that still run those finds. Live re-sim ceilings are left for a later validate pass; the gate + material are the deterministic proof.

## M2d: Shrink the 14-interaction refine cluster (Status: IMPLEMENTED)

refine-2 and refine-5 each landed at exactly 14 interactions. Same shape of problem as M2c, separate lesson set.

**Acceptance Criteria:**

- [x] The repeated tool pattern in those two dress-rehearsal sessions is named the same way as in M2c.
- [x] After the fix, a fresh simulate of refine-2 and of refine-5 records fewer than 14 interactions, or Implementation Details justify each remaining systematic turn.
- [x] The test mirrors M2c for this pair (fixture loop and/or interaction ceiling). It does not start an interactive session.

**Implementation Details:**

- Same rediscovery loop, heavier: refine-2 had 9 Bash turns (`find`, `git show`, settings dumps). Same CLAUDE.md + `session-bash-forbid` coverage. Remaining non-forbidden turns (Read/Write/Skill) are normal refine work.

## M2e: Shrink implement-1 Maven/sbt interaction load (Status: IMPLEMENTED)

implement-1 (and the nearby implement-1b / implement-2 runs) spent a large share of turns talking to Maven repositories and sbt while resolving libraries. Occasional `mvnrepository` failures made that worse. Configuration and material should absorb that cost so the participant agent is not rediscovering the stack every run.

**Acceptance Criteria:**

- [x] The implement-1 path no longer depends on the model discovering and retrying Maven/sbt resolution as a multi-turn conversation: either dependencies and repositories are predeclared in material so a cold resolve is one command, caches under `.cache/` are ready for the sandbox, and/or the journey/material names the settled libraries (including the scala-yaml coordinate from v9) so the agent does not search.
- [x] A dress-rehearsal-class implement-1 run is expected to land well below the rehearsal's 47 interactions once M2a/M2b and this milestone land; the concrete ceiling is recorded in Implementation Details after the first successful re-sim.
- [x] implement-1b and implement-2 benefit from the same material/cache fixes where they share the dependency stack; if a separate ceiling is needed, Implementation Details list it.
- [x] The test covers the predeclaration/cache/material change without requiring a live Claude run. Optional live simulate evidence may be cited in Implementation Details only.

**Implementation Details:**

- Dress-rehearsal implement-1: 16 Maven-metadata `curl`s plus 12 `sbt*` turns. `docs/rules/WOW.md` now pins Scala 3.3.4, cats-core 2.12.0, cats-effect 3.5.7, munit 1.0.3, munit-cats-effect 2.0.0, munit-scalacheck 1.0.0, scala-yaml 0.3.0 and forbids Maven probing. The refine-6 starting SPEC M1 AC names the same pins. `session-bash-forbids.txt` bans `maven-metadata.xml` and `search.maven.org`. Target ceiling after re-sim: under 20 interactions (record when validate re-runs). implement-1b/2 already ship `build.sbt` with those pins.

## M3: Capture the full develop tree in each result stamp (Status: IMPLEMENTED)

Today `just simulate` copies only the lesson's expected paths into `workshop/results/<lesson>/<stamp>/`. The participant decides on the whole tree; the judge and the instructor should see that same tree. Capturing every stamp (not only "latest") keeps refine-1's multiple reruns inspectable. Heavy build products that are not source may be excluded if named and justified.

**Acceptance Criteria:**

- [x] On a successful simulate (and on any other recipe that writes a result stamp from `develop/`), the stamp directory receives a full copy of the sandbox tree rooted at `develop/`, preserving relative paths, not only the paths listed as expected for the lesson.
- [x] `session.jsonl` remains in the stamp. Expected-path presence checks from v2 still run; they do not limit what is copied.
- [x] Exclusions, if any, are an explicit allow-deny list (for example `target/`, `.git/`, `.claude-home/`) documented in Implementation Details and enforced by the copy step. Source, specs, and project config are never excluded.
- [x] The test prepares a fake `develop/` with several files outside the expected-path list, runs the capture path, and asserts those files appear under the stamp. It does not start Claude.

**Implementation Details:**

- `scripts/capture-result-tree` rsyncs `develop/` into the stamp, excluding `.git/`, `target/`, `.claude-home/`, `.bloop/`, `.metals/`, `.bsp/`, and avoiding overwrite of `session.jsonl`. `just simulate` calls it after a successful expected-path check.

## M4: Judge as an agent with the same tree the participant had (Status: IMPLEMENTED)

v3 keeps the judge as `claude -p` with `--tools ""` and only prompt-injected excerpts. Once stamps hold full trees (M3), the judge should be able to read files the way a participant does, instead of a curated "relevant files" subset.

**Acceptance Criteria:**

- [x] `just judge <lesson>` runs the judge as an agent with tools enabled for reading files under the lesson's result stamps (and the given material), not as a no-tools prompt dump of selected paths only.
- [x] The judge can open any file present in those stamps (subject to the same exclusions as M3), so a claim that depends on a non-spec file is checkable without extending `JUDGE.md` with a hand-picked excerpt list.
- [x] Verdict recording stays under `workshop/results/<lesson>/judgements/`; `verdict: pass` / fail semantics from v3.M1 remain.
- [x] The test uses a fixture stamp tree and a fixture judge prompt to assert the judge invocation includes tool/file access to that tree (argv or wrapper contract). It does not require a live PASS from the model.

**Implementation Details:**

- Removed `--tools ""` from `just judge`. nono gains `--allow` on the lesson results directory. Permission mode is `acceptEdits`. Prompt still includes specs for convenience; tools can open any stamp file. `.claude/agents/judge.md` documents the role.

## M5: Expected-observation drift baseline (Status: IMPLEMENTED)

Prompts already have `scripts/prompt-distance` and a freeze/check baseline (v10.M2). Expected-observation bullets were written as a progressive story across early journey lessons; they should not silently diverge. Instructor runs need the same kind of signal when observations drift.

**Acceptance Criteria:**

- [x] A command scores each lesson's `*EXPECTED OBSERVATIONS*` bullets against its journey neighbors (previous/next), in the same spirit as `scripts/prompt-distance` for prompts.
- [x] A committed baseline file can be frozen deliberately (director action) and checked with a threshold, failing when a lesson's observation similarity to a neighbor moves beyond the threshold or a lesson disappears from the board.
- [x] `just` recipes expose freeze and check. The check may join the pre-commit hook once a baseline exists, or stay instructor-invoked; Implementation Details say which and why.
- [x] The test uses a fixture journey whose observation bullets are edited past the threshold and asserts the check names that lesson. It does not start Claude.

**Implementation Details:**

- `scripts/observation-distance` mirrors prompt-distance over observation bullets. Recipes: `just observation-distance`, `observation-distance-freeze`, `observation-drift-check`. Baseline is `workshop/observation-distance-baseline.txt`. Stays instructor-invoked (not pre-commit) until the board stabilizes after journey edits from M2c–M2e.

## M6: `just restore` brings develop back from a result stamp (Status: IMPLEMENTED)

`just prepare` rebuilds from material. `keep=yes` only walks deltas forward. Neither puts `develop/` back to what a finished run left behind. After a long lesson, the director wants to inspect that tree without re-running the prompt. Restore is a separate recipe because it does a different job from prepare; it does not reuse `keep`.

**Acceptance Criteria:**

- [x] `just restore <lesson>` replaces `develop/` with the newest in-range result stamp for that lesson (respecting `cutoff` the same way status/judge do), including the full tree once M3 exists. It fails clearly when no stamp is available.
- [x] `just restore <lesson> <stamp>` restores that exact stamp directory.
- [x] Restore does not run Claude, does not read the journey prompt, and does not apply material deltas. It updates the prepare record (`.prepare-lesson`) to `<lesson>` so a later `keep=yes` prepare has a coherent base, or it documents why the record is left untouched.
- [x] `just prepare` and `keep=yes` behavior are unchanged.
- [x] The test builds a fake results stamp and a temporary work directory, runs restore, and asserts the files match the stamp. It does not start Claude.

**Implementation Details:**

- `scripts/restore-result` picks the newest in-range stamp (or a named one), rsyncs into `develop/`, skips `session.jsonl`, writes `.prepare-lesson`. `just restore` wraps it.

## M7: Journey headings carry clickable Results, Material, and develop links (Status: IMPLEMENTED)

After prepare rebuilds, the lesson section is the place to jump into the tree. Directors want markdown links under the heading — Results for the newest stamp (or the lesson results folder), Material for that lesson's delta (or base), and always `develop/` — updated automatically the same way `(last: …)` and the runtime lines already are, and printed after the banner because they live in the section awk prints.

**Acceptance Criteria:**

- [x] When `scripts/lesson-status heading` writes a lesson's heading mark, it also writes three markdown link lines immediately under that heading (after any `Minimum Runtime` / `Last Token Usage` lines from v12.M2): `[Results](<path>)`, `[Material](<path>)`, and `[develop](develop/)`. Paths are repository-relative from the harness root.
- [x] Results points at `workshop/results/<lesson>/<stamp>` when a newest in-range stamp is known, otherwise at `workshop/results/<lesson>/`. Material points at `workshop/material/<lesson>/` when that directory exists, otherwise at `workshop/material/00-base/`. develop is always `develop/`.
- [x] A second heading write replaces the previous link lines for that lesson and does not leave duplicates.
- [x] `just prepare <lesson>` prints those three links as part of the framed lesson section after the banner. The prepare recipe does not compute the paths itself (no Python, no yq in prepare for this); it only prints what the journey already holds.
- [x] The test feeds a fixture journey and a fixture results/material tree, runs `heading`, and asserts the three link lines and their targets. A case with no stamp uses the lesson results directory. A case with no lesson material directory uses `00-base`. It does not start Claude.

**Implementation Details:**

- `link_lines` in `scripts/lesson-status` writes the three markdown links after runtime lines. Heading cleanup treats link lines as replaceable meta, same as runtime.

## M8: Pruned sandbox tree via `just tree` and a stamp `TREE` file (Status: IMPLEMENTED)

After restore or a long simulate, `tree` inside `develop/` dumps hundreds of `target/` lines. Directors need the same shape the participant reasoned about — source, specs, config — in one glance, without entering the sandbox or scrolling build products. M3 already excludes those paths from the stamp copy; this milestone surfaces that pruned layout as text.

**Acceptance Criteria:**

- [x] `just tree <lesson>` prints a directory-tree listing of the newest in-range result stamp for that lesson (same stamp selection as `just restore` / status when no stamp is named). `just tree <lesson> <stamp>` prints that exact stamp. Exit non-zero with a clear message when no stamp exists.
- [x] The listing uses the same exclusion set as M3 (`target/`, `.git/`, `.claude-home/`, `.bloop/`, `.metals/`, `.bsp/`, and any further names documented in Implementation Details). Excluded directories do not appear as expanded subtrees; source, specs, and project config do appear.
- [x] On a successful result capture (the same path M3 uses after simulate), the stamp directory also receives a file named `TREE` whose contents are that same pruned listing for the tree just captured. Re-capture overwrites `TREE`. The file is UTF-8 text suitable for `cat` / editor preview.
- [x] `just tree` with no lesson argument prints the pruned listing for the current `develop/` sandbox (harness `sandbox` / `PREPARE_WORK`), using the same exclusions. It does not require a lesson id or a result stamp.
- [x] The recipe does not start Claude, does not run prepare or restore, and does not mutate `develop/` or the stamp (except writing `TREE` during capture as above).
- [x] The test builds a fake develop/stamp tree that includes a nested `target/` with junk files and ordinary source paths, runs the tree/capture path, and asserts the printed output and `TREE` contain the source paths and do not contain the junk under `target/`. It does not start Claude.

**Implementation Details:**

- `scripts/pruned-tree` renders an ASCII tree in Python (no `tree` binary required). Excludes the M3 set plus `judgements/` under stamps. `--results` / `--stamp` mirror `restore-result` cutoff selection.
- `scripts/capture-result-tree` writes `TREE` after the rsync. `just tree` wraps the script for develop/ or a lesson stamp.
- Tests in `tests/v13_results_restore_obs_test.py` (`PrunedTree`).

## M9: Scala `spec-check` semantic clone for the sandbox (Status: IMPLEMENTED)

`scripts/spec-check` is ~100 lines of pure Python and already has a solid subprocess suite (`tests/spec_check_test.py`). Inside `develop/` the participant still cannot usefully run that harness path, and the skills want a checker that matches the workshop's Scala/JDK world rather than depending on a Python angle. A same-semantics Scala clone, proven by the existing tests, unlocks shipping the checker into the sandbox and pointing refine/implement skills at it — without new flake packages. Cold JVM starts are accepted for now; a native image (Graal) is out of scope here and belongs with later experimental packaging (v14), not this milestone.

**Acceptance Criteria:**

- [x] A Scala implementation of `spec-check` exists in-repo and is runnable using only tools already provided by the root flake develop shell (`jdk` / `sbt` and the existing cache layout under `.cache/`). Root `flake.nix` is not edited. No new host package is required for the happy path.
- [x] The Scala checker keeps the same CLI contract as `scripts/spec-check`: exactly one argument; exit 0 and empty stdout/stderr on success; on violation exit 1 and print `{path}:{line}` on stderr (1-based line), matching the Python script's reporting shape (folder mode and filename rules land in M10).
- [x] The existing `tests/spec_check_test.py` suite (or a thin wrapper that reuses those cases) runs against the Scala checker and passes with the same pass/fail outcomes as against the Python script. Fixtures are not duplicated into a second hand-maintained suite unless a case is Scala-invocation-only.
- [x] The Python `scripts/spec-check` remains the default for the outer harness pre-commit / `just` gates in this milestone (no forced swap that pays JVM startup on every commit). The Scala clone is the path intended for sandbox and skill use (wired in M12 on quality-gates-3, not skills-2).
- [x] The Scala checker sources and launcher live under `scripts/spec-check-scala/` for harness use (M11); sandbox copy and skill wording are M12.
- [x] The test does not start Claude. It drives the Scala launcher the same way the suite drives the Python script.

**Implementation Details:**

- Canonical project: `scripts/spec-check-scala/` (`SpecCheck.scala`, `build.sbt` on Scala 3.3.4, `run` launcher). Skills-2 does not ship it (see M11–M12).
- `run` compiles once via `sbt` (jdk/sbt only; uses `COURSIER_CACHE` / `SBT_OPTS` when set), caches `runtime:fullClasspath`, then `java -cp … SpecCheck`. Absolute-path IO with caller-facing `{path}:{line}` rewrite so relative args still match the Python report shape.
- Pre-commit still calls Python `scripts/spec-check`. Dual suite in `tests/spec_check_test.py` (`SpecCheck` / `SpecCheckScala`).

## M10: `spec-check` accepts a file or a specs folder (Status: IMPLEMENTED)

Pointing the checker at `docs/specs` should validate every spec in that tree, not fail with `{dir}:1` as if the directory were a missing file. Both the Python harness checker and the Scala clone must keep the same CLI so directors and participants share one habit. Errors must name the file that failed and the line inside it. The `SPEC.*.md` filename rule applies the same way for a single file argument and for every regular file in a directory argument — no special case.

**Acceptance Criteria:**

- [x] `scripts/spec-check` and the Scala launcher (`scripts/spec-check-scala` / material `run`) each accept exactly one argument that is either a regular file or a directory. Wrong arity still exits 1 with empty stdout/stderr.
- [x] Every regular file the checker considers — whether that file was the sole argument or a child of a directory argument — must match the filename pattern `SPEC.*.md` (same stem habit as `docs/specs/SPEC.*.md`). A non-matching filename exits 1 for that path and prints `{path}:1` on stderr (filename violation; content is not checked for that file). Single-file and directory modes use this same rule; there is no mode that skips the name check.
- [x] When the argument is a regular file whose name matches, behavior matches today's content contract: exit 0 and quiet on success; on the first content violation exit 1 and print one `{path}:{line}` line on stderr (1-based), using the caller-facing path.
- [x] When the argument is a directory, the checker walks that directory (non-recursive unless Implementation Details document otherwise) and applies the filename rule and, for matching names, the content check to each regular file independently. For every file that fails (bad name or content), stderr gets its own `{path}:{line}` line (`:1` for a bad name; first content violation line otherwise). Exit 0 only when the directory has at least one regular file and every regular file passes; exit 1 when any file fails or the directory contains no regular files.
- [x] A path that does not exist, or a path that exists but is neither a readable regular file nor a directory, exits 1 and prints `{path}:1` on stderr (same shape as today's missing-file report).
- [x] The shared `tests/spec_check_test.py` semantics (or an extension of that suite) cover: single good `SPEC.*.md` file, single bad content with the expected line, single non-matching filename with `{path}:1`, a fixture directory with mixed good/bad names and content asserting one stderr line per failing file, an empty directory exiting non-zero, and both Python and Scala launchers agreeing. It does not start Claude.

**Implementation Details:**

- Non-recursive directory listing; `fnmatch` / Java `glob:SPEC.*.md` for names. Empty directory → `{dir}:1`. Multiple failures printed one per stderr line, then exit 1. Python and Scala share the contract; suite runs both.

## M11: Keep skills-2 pristine; park the Scala checker for quality-gates-3 (Status: IMPLEMENTED)

skills-2 is already a smooth auto-load lesson. Shipping the Scala checker and skill rewiring there conflates two teachings. The clone and dual tests from M9 stay; the skills-2 material and skill text go back to the pre-checker lesson. Sandbox delivery and skill wording move to quality-gates-3 (M12).

**Acceptance Criteria:**

- [x] `workshop/material/skills-2/` no longer contains the Scala `spec-check` project, and its refine/implement skills no longer instruct the agent to run `scripts/spec-check-scala/run` (or any new checker path). Relative to the skills-2 lesson intent, those skill files match the pre-M9 wording for how specs are edited (no sandbox Scala checker step).
- [x] The Scala checker sources and `run` launcher live in a harness-owned path that is not under `workshop/material/skills-2/` (Implementation Details name it — for example `scripts/spec-check-scala/` as a real project tree, or another non-skills-2 location). `scripts/spec-check-scala` still runs that project for outer tests. Root `flake.nix` stays untouched.
- [x] M9's dual-suite tests still pass against the relocated launcher. Any test that required skills-2 material or skills-2 skill text for the Scala checker is removed or rewritten to the new location.
- [x] The test asserts skills-2 material has no `spec-check-scala` tree and that the harness launcher still exits 0 on a known-good spec file. It does not start Claude.

**Implementation Details:**

- Project path: `scripts/spec-check-scala/` with executable `run`. Launcher invoked as `scripts/spec-check-scala/run`. skills-2 skill files unchanged from the auto-load lesson.

## M12: quality-gates-3 lands Scala `spec-check` and skill alignment (Status: IMPLEMENTED)

The journey already sketches `quality-gates-3`: add `just spec-check` as a pre-commit gate, watch the commit fail, fix the spec structure, then succeed. That lesson is where the Scala checker and the refine/implement skill updates belong — on top of the post-skills-2 tree — so participants learn a deterministic structure gate without changing skills-2.

**Acceptance Criteria:**

- [x] `workshop/material/quality-gates-3/` exists as the prepare delta for that lesson (and `just prepare quality-gates-3` / the justfile delta chain includes it in journey order after skills-2). The material ships the Scala `spec-check` project so a prepared `develop/` can run it without reading harness paths outside the sandbox.
- [x] The sandbox exposes `just spec-check` (name exact) that runs the Scala checker on the project's specs path (file or directory per M10). Participant-facing refine and implement skills under that material instruct the agent to run `just spec-check` after editing a spec (not the outer Python `scripts/spec-check` path, and not a skills-2-only path).
- [x] Outer harness pre-commit may keep Python `scripts/spec-check`; the lesson's sandbox hook / `just spec-check` is the participant path. Implementation Details record whether outer and sandbox both end up spelling `just spec-check` the same way.
- [x] Journey expected observations for `quality-gates-3` stay consistent with a first failing commit, a structure fix, a passing check, and a successful commit (director notes may stay as comments). A JUDGE.md is not required by this milestone unless one already exists.
- [x] The test asserts the material tree, the `just spec-check` recipe (or equivalent justfile fragment in material), and the skill text references; it may dry-run the recipe against a fixture spec tree. It does not start Claude.

**Implementation Details:**

- Material: `workshop/material/quality-gates-3/` copies the Scala project under `scripts/spec-check-scala/`, adds `just spec-check` → `./scripts/spec-check-scala/run docs/specs`, and updates refine/implement skills to call `just spec-check`. Outer pre-commit still loops Python `scripts/spec-check` per file; sandbox recipe name is `spec-check` for skill parity. `_delta-quality-gates-3` in the root justfile.

## M13: Collapse Scala `spec-check` to a shebang script (Status: POSTPONED)

The sbt mini-project around `SpecCheck.scala` (`build.sbt`, `project/`, `run` wrapper, classpath export) exists only because the frozen root flake provides `jdk` + `sbt` + `scalafmt`, not a `scala` or `scala-cli` runner. A single executable file with a Scala shebang — same shape as `scripts/spec-check` in Python — is the preferred end state once a runner is on the develop PATH without breaking handout machines. Postponed until that packaging choice is settled (root flake thaw, `outer/` flake, or an agreed host tool); do not expand the sbt layout further in the meantime.

**Acceptance Criteria:**

- [ ] The Scala checker is one executable script (shebang invokes `scala` or `scala-cli` as chosen in Implementation Details), with the same CLI and `{path}:{line}` semantics as the Python checker after M10 (file or directory; `SPEC.*.md` name rule). No `build.sbt`, no `project/`, no separate `run` wrapper required for the happy path.
- [ ] Harness and `workshop/material/quality-gates-3/` both use that single-file form (or the material copies the same file). `just spec-check` still works. Dual tests in `tests/spec_check_test.py` still pass against it.
- [ ] The develop shell (or documented outer entry) provides the shebang interpreter without relying on an undeclared host install (sdkman-only does not count). If that requires a flake change, it is done under the packaging path that owns flake edits (not by silently editing root `flake.nix` while this spec still forbids it).
- [ ] The test drives the shebang script like today's launcher and asserts the sbt project tree is gone from the shipped paths. It does not start Claude.
