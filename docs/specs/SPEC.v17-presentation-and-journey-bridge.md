# SPEC.v17: Presentation port and journey–slide bridge

This repo owns the hands-on **journey** (`workshop/JOURNEY.md`, sandbox lessons, stamps). The slide deck that frames that workshop lives today in `~/Projects/hivemind/agentic-engineering-workshop/presentation/` (reveal-md spines, `lessons/*.md` units, theme, fonts, drawings). Directors need the deck fully inside this outer shell—runnable via `just`—then a bridge so sandbox hands-on work can back selected deck slots without inventing a second slide type.

**Notation.**

- **Exercise** — every unit in the reveal-md deck (`presentation/lessons/<id>.md`, `# 💡` theory / `# 🏝️` sandbox Steckbrief / `## 🛠️` in-room hands-on, listed in a spine’s `<!-- lessons -->` menu). Theory-only strips and hands-on cards are both exercises.
- **Lesson** — a sandbox hands-on unit in `workshop/JOURNEY.md` / `scripts/lesson-order` (e.g. `implement-2`, `quality-gates-3`). Lessons do **not** appear in the deck as a separate kind of slide; they optionally **back** an exercise.
- **Lesson-backed exercise** — an exercise whose Steckbrief (and optional sync) is derived from one journey lesson. Unbacked exercises stay as today (theory / existing workshop cards).
- **Spine** — a deck entry file (`deck-software-part1.md`, …) with a `<!-- lessons -->` menu that `build-deck` splices.
- **Steckbrief** — the 1–3 vertical slides inside a lesson-backed exercise that mirror that lesson’s JOURNEY section (prepare, worktree, prompt, observations, runtime measures).
- **Showcase** — optional slides after the Steckbrief that surface worth-mentioning outcomes from prior sandbox runs (lesson-specific; authored under that lesson’s results tree).

**Composition per topic.** For each hands-on slot, the deck keeps (1) an upfront **theory / motivation** exercise (or strip), then (2) a **lesson-backed** Steckbrief, then optionally (3) a **showcase** drawn from that lesson’s curated results narrative. Paths stay separate until assemble time: journey/results under `workshop/`, deck under `presentation/` (exact roots pinned in Implementation Details when implementing).
**Source of truth for the port.** Copy from `agentic-engineering-workshop/presentation/` at the commit/path named when implementing M1; **software track only** (`deck-software-part1.md`, `deck-software-part2.md`). Do **not** port `deck-infrastructure.md` or infra workshop trees in this version. Merge `presentation/drawings/` into this repo’s `docs/drawings/` (no silent overwrite without a documented rename).

**Directional spin — quality gates across the two half-days.**

- **Part 1** introduces *why* deterministic quality gates matter to everyone (the ring around non-determinism), and stays **superficial**: redundancy and complexity-style gates as they already appear in the journey / deck today. Motivation and vocabulary first; no deep Scala tooling tour.
- **Part 2** is where we circle back for **Scala engineers**: extended quality-gate exercises that take input from the `/deterministic-gates` skill (and its `catalog.yaml` recipe registry of recurring peel/freeze patterns) and push those patterns into **Scala-specific** checks, CI, and workshop material. Recurring catalog recipes become concrete Scala gates rather than general theory.
- Bridging journey lessons into spines should respect that split: Part 1 lesson-backed slots stay high-level; Part 2 absorbs the deeper Scala gate story when we wire showcases and Steckbriefs.

## M1: Port the software presentation into this repo (Status: ✅ DONE)

Bring the reveal-md stack here so `just present` (or the pinned recipe name) serves the software deck without leaving this repository.

**Acceptance Criteria:**

- [x] The software presentation tree lives in this repo (path pinned in Implementation Details): spines `deck-software-part1.md` / `deck-software-part2.md`, `lessons/` exercises, `theme/` (CSS/JS), `assets/` (fonts/images), `.bin/` scripts (`present`, `build-deck`, `check`, …), `package.json` / lockfile, and `reveal.json5` (or equivalent). `deck-infrastructure.md` is absent.
- [x] Drawings from the source `presentation/drawings/` are merged under `docs/drawings/`; name collisions with existing files (e.g. `sprouts.excalidraw`) are resolved by rename or subdirectory without losing either file, and the resolution is listed in Implementation Details.
- [x] Outer `just` recipes wrap the presentation commands used live: at least present/serve (default software-part1), build, stop, and check (or documented aliases). They run from the repo root and do not require editing root `flake.nix` unless a later packaging milestone owns that thaw.
- [x] `just <present-recipe>` (name pinned) starts or documents how to open the software Part 1 deck after `npm ci` in the presentation root; a test asserts the recipe exists, the software spines and theme files exist, infrastructure spine is absent, and drawings merge landed. It does not start Claude or a long-lived server in CI.

**Implementation Details:**

- Source: `~/Projects/hivemind/agentic-engineering-workshop` commit `e5a0ee969291fa0be9122a9768f8aa73d6c82222` (`presentation/`). Software track only — `deck-infrastructure.md` not copied.
- Deck root: `presentation/` (spines, `lessons/`, `theme/`, `assets/`, `.bin/`, `package.json` / lockfile, `reveal.json5`, Makefile, README, COMICS).
- Drawings: source files merged into `docs/drawings/` (including `output/`). No basename collision with existing `sprouts.excalidraw`; both kept. `presentation/drawings` is a symlink to `../docs/drawings` so the README export path still works.
- Outer recipes: `just present-install` (`npm ci`), `just present` (default `deck=software-part1`, `rebuild=yes` → bridge+assemble then serve `.build/`; `rebuild=no` skips assemble), `just present-build` (assemble only), `just present-stop`, `just present-check`. No root `flake.nix` change; Node stays local under `presentation/`.
- Ignore: `presentation/node_modules/`, `.build/`, `dist/`, `*.pdf` in root `.gitignore` (and existing `presentation/.gitignore`).
- Test: `tests/v17_presentation_port_test.py`.

## M2a: Basic bridge — back an exercise with a sandbox lesson (Status: ✅ DONE)

Directors can attach a journey lesson to an exercise slot (or generate that exercise from the lesson) so the spine stays an exercise menu while sandbox content is tugged in at a chosen position.

**Acceptance Criteria:**

- [x] A documented bridge mechanism (include directive, stub under `presentation/lessons/`, or generator—name pinned in Implementation Details) binds an **exercise id** to a **journey lesson id** (from `scripts/lesson-order`) and produces or references markdown that `build-deck` splices like any other exercise.
- [x] A spine can list that exercise id in its `<!-- lessons -->` block at an arbitrary position; `build-deck` (or the wrapped `just` build) exits 0 and the assembled `.build/` markdown contains recognizable content derived from the backing lesson’s JOURNEY section (at least the lesson title/slug).
- [x] Bridge docs describe the model as “every deck unit is an exercise; some are lesson-backed,” not as a second slide kind. The test uses a fixture journey snippet + fixture spine and asserts the assembled output contains the backing-lesson marker. It does not start Claude.


**Implementation Details:**

- Binding file: `presentation/bridge/bindings.yaml` (list of `{exercise, lesson, name?}`). Docs: `presentation/bridge/README.md`.
- Generator: `scripts/presentation-bridge` writes `presentation/lessons/<exercise>.md` (`# 🏝️ <Name> <n>` + journey intro + `<!-- backing-lesson: <id> -->`). Exercise ids stay `^[a-z]+\d+$` for `build-deck`. Theory exercises keep `# 💡`; in-room hands-on keep `## 🛠️`.
- Bridge is folded into `presentation/.bin/build-deck` (`run_bridge` first). `just present` (default `rebuild=yes`) → `.bin/present` → build-deck then serve `.build/`; `rebuild=no` serves an existing `.build/` only. `just present-build` assembles without serving. No separate `present-bridge` recipe.
- Live bindings start empty (`[]`); directors add entries and list the exercise id in a spine menu when ready.
- Test: `tests/v17_presentation_bridge_test.py`.

## M2b: Steckbrief shape, template, and sync skill/script (Status: ✅ DONE)

A lesson-backed exercise should look like the other exercises but carry the journey’s operational map: prepare commands, worktree, prompt, expected observations, and recent run measures (wall time, tokens/paths when present on the JOURNEY heading).

**Acceptance Criteria:**

- [x] A **Steckbrief template** (path pinned) defines 1–3 vertical slides (`----`) for one lesson-backed exercise, covering at least: (1) intro / prepare commands, (2) `*WORKTREE*` (or equivalent summary), (3) `*PROMPT TO TEST*` plus `*EXPECTED OBSERVATIONS*`, and a place for last-run measures when the JOURNEY heading carries them (`Minimum Runtime`, `Last Token Usage`, results/material links).
- [x] A script and/or Claude skill regenerates or refreshes Steckbrief markdown from `workshop/JOURNEY.md` (and optional overrides) so individual slide tweaks are not lost without a documented merge rule (overwrite flags or a hand-edited region). The skill description triggers on Steckbrief / journey-slide / lesson-backed exercise language.
- [x] Look-and-feel refinements stay inside the existing HIVEMIND theme (no second CSS stack); Steckbrief slides use the same separator conventions as `_template.md` / existing exercises. The test asserts template markers, a fixture generation run, and skill file presence. It does not start Claude.

**Implementation Details:**

- Template: `presentation/bridge/steckbrief.md` (title strip with measures + hand region, then three `----` verticals: Prepare, Worktree, Prompt and observations).
- Generator: `scripts/presentation-bridge` fills the template from JOURNEY; preserves `<!-- hand:begin -->`…`<!-- hand:end -->` unless `--overwrite`. Optional binding `lead` overrides the intro paragraph.
- Skill: `.claude/skills/steckbrief/SKILL.md`.
- First live card: `refine1` ← `refine-1` (after `variance1` in Part 1).
- Tests: `tests/v17_steckbrief_test.py`.

## M3: Smoothness check for the composed deck (Status: IMPLEMENTED)

After theory exercises, lesson-backed Steckbriefs, and optional showcases are composed, someone (skill or agent) can judge whether the full software presentation still tells one coherent story.

**Acceptance Criteria:**

- [x] A Claude skill and/or agent definition (path pinned under `.claude/` or presentation material) reviews the **assembled** software deck(s) for narrative smoothness: theory→Steckbrief→showcase pairing, consistent exercise framing (lesson-backed called out only where useful), broken includes, orphan agenda entries, and abrupt topic jumps—outputting ordered findings, not only a pass/fail bit.
- [x] A deterministic pre-check (script or `just` recipe) fails on mechanical breaks (missing exercise file for a spine id, broken lesson-backing or showcase reference, build-deck failure, missing theme asset referenced by a relative path in a fixture) so the LLM skill is not the only gate.
- [x] The test asserts skill/agent files, the mechanical check recipe, and a fixture that fails the mechanical check. It does not require a live Claude session in CI.

**Implementation Details:**

- Skill: `.claude/skills/deck-smoothness/SKILL.md` (ordered findings on assembled `.build/` decks after the mechanical gate).
- Mechanical gate: `scripts/presentation-check` + `just present-check-smooth` (spine lesson files, journey bindings, optional `showcase: required`, relative `assets/` refs). Runs the bridge first unless `--skip-bridge`.
- Tests: `tests/v17_deck_smoothness_test.py`.

## M4: Port `tocmd` to Scala for high-level markdown compare (Status: ✅ DONE)

`scripts/tocmd` (Python today) lists ATX headings for navigation. Rework it as a Scala script so directors and agents can call it easily and use heading outlines to compare markdown files quickly at a high level (e.g. before/after a long lesson run).

**Acceptance Criteria:**

- [x] A Scala `tocmd` entrypoint (path and runner pinned in Implementation Details—e.g. scala-cli script or thin wrapper under `scripts/`) preserves the v5 contract: `tocmd [--lines] <path.md|directory>` prints ATX headings (`#`–`######`) in file order; directory mode prints sorted `*.md` with path labels when more than one file; missing path exits non-zero.
- [x] The same tool supports comparing two markdown paths at heading-outline level (exact flag/subcommand pinned in Implementation Details): equal outlines exit 0; differing outlines exit non-zero and print a concise heading-level diff (or ordered before/after lists) without requiring a full textual diff of bodies.
- [x] Outer docs or `just` expose how to invoke the Scala `tocmd` (and the compare mode). Existing skill references that call `scripts/tocmd` keep working or are updated to the new entrypoint in the same milestone. The test covers heading listing, `--lines`, directory multi-file labeling, and a fixture pair that fails compare. It does not start Claude. Root `flake.nix` stays untouched unless packaging already owns the Scala runner for this script.

**Implementation Details:**

- `scripts/tocmd` is a bash wrapper; logic lives in `scripts/tocmd.scala` (scala-cli, Scala 3.3.4, `@main def tocmd`). No root `flake.nix` change.
- List mode unchanged from v5: `scripts/tocmd [--lines] <path.md|directory>`.
- Compare mode: `scripts/tocmd --compare <path-a> <path-b>` (heading-outline LCS-style diff on stdout; exit 1 when different). Leading `--` is stripped so `just tocmd -- --compare a.md b.md` works.
- Recipe: `just tocmd *args` forwards to the wrapper. Skills still call `scripts/tocmd`.
- Tests: `tests/tocmd_test.py` (v5 contract + compare + just recipe).

## M5: Lesson showcase via `EXPLANATION.md` into the deck (Status: IMPLEMENTED)

Long-running lessons leave results worth showing after the Steckbrief. Those narratives are lesson-specific and live with the results tree; the deck only pulls them in when a lesson-backed exercise opts in.

**Acceptance Criteria:**

- [x] Each lesson that opts into showcase keeps a curated `EXPLANATION.md` under its results tree at `workshop/results/<lesson-id>/EXPLANATION.md` (path pinned). The file is human-authored narrative for the deck (what to show from prior runs), not a dump of every timestamped run. At least one fixture or real lesson path demonstrates the layout.
- [x] A bridge/integration mechanism (tied to M2a/M2b or documented beside them—name pinned) can append or splice showcase slides **after** that lesson’s Steckbrief from `EXPLANATION.md` (or a marked section of it) into the assembled exercise markdown. Lessons without `EXPLANATION.md` build without showcase slides.
- [x] Showcase content may reference high-level before/after structure (e.g. via Scala `tocmd` compare output or quoted outlines) when the explanation calls for it; the AC does not require every lesson to include a tocmd block. The test uses a fixture `EXPLANATION.md` + lesson-backed exercise and asserts the assembled deck places showcase material after the Steckbrief markers. It does not start Claude.

**Implementation Details:**

- Path: `workshop/results/<lesson-id>/EXPLANATION.md`. Opt-in by file presence; optional `<!-- showcase:begin -->`…`<!-- showcase:end -->` region (else whole file). Binding `showcase: required` makes absence a `presentation-check` failure.
- `scripts/presentation-bridge` appends EXPLANATION verticals after the Steckbrief (`<!-- showcase:from … -->`); each vertical owns one `## Results: …` title (no synthetic `## Showcase`). Gate: `scripts/slide-double-heading` via `presentation-check`. First live example: `workshop/results/refine-1/EXPLANATION.md` → `refine1`.
- Tests: `tests/v17_showcase_test.py`, `tests/slide_double_heading_test.py`.

## M6: Harden presentation npm dependencies (Status: PENDING)

`just present-install` currently reports a large `npm audit` surface (moderate/high) from `reveal-md` / `decktape` and their transitive tree (e.g. deprecated `puppeteer`/`glob`/`uuid`). Leave the port working; clean the lockfile later without breaking present/build/check.

**Acceptance Criteria:**

- [ ] `presentation/package.json` / lockfile are updated (or replacements chosen) so `npm audit` in `presentation/` reports **zero high/critical** findings, or each remaining high/critical is listed in Implementation Details with a documented accept-risk reason and an upstream tracking note.
- [ ] After the upgrade, `just present-install`, `just present-build`, and `just present-check` still succeed for the software spines (Part 1 and Part 2). Reveal-md major bumps are allowed if theme/scripts still load; any required theme or `.bin` edits stay in this milestone.
- [ ] A test or scripted check fails when high/critical audit counts exceed the accepted baseline (exact command pinned—e.g. `npm audit --audit-level=high` with allowlist file). It does not start a long-lived present server or Claude.

## Non-goals

- Porting the infrastructure deck or `workshops/infrastructure/` in this version.
- Replacing journey JOURNEY.md with slides as the source of truth for prompts/observations.
- Rewriting every existing software exercise into Steckbrief form (only lesson-backed exercises need Steckbrief; unbacked exercises stay as-is).
- Treating “lesson” as a second deck content type in spines or theme (lessons stay sandbox-side; exercises stay deck-side).
- Auto-generating `EXPLANATION.md` from every timestamped run (curation stays human; M5 only wires curated files into the deck).
- Clearing presentation `npm audit` findings in M1–M5 (deferred to M6).
- Editing root `flake.nix` solely to add Node or a new Scala runner unless a later outer packaging milestone requires it (Node may remain `npm ci`-local under `presentation/`; Scala `tocmd` may follow the existing `scripts/spec-check-scala` runner pattern).
