# SPEC.v18: Drawing companions — interpret, checksum, curate

Excalidraw figures under `docs/drawings/` are dense visual arguments. Agents and directors need a **sidecar markdown** next to each drawing that says what it shows, stays honest about which file bytes that reading was based on, and still leaves room for human notes that a regenerate must not casually wipe.

**Notation.**

- **Drawing** — a source file `docs/drawings/<stem>.excalidraw` (not the exported SVG under `docs/drawings/output/`).
- **Companion** — `docs/drawings/<stem>.md` beside that drawing (same stem). Example: `hard-easy.excalidraw` ↔ `hard-easy.md`.
- **Source checksum** — a content hash of the drawing file bytes (algorithm pinned in Implementation Details; default expectation is SHA-256 hex), stored in the companion so staleness is mechanical.
- **Stale** — companion exists but its recorded source checksum ≠ the current drawing’s checksum (drawing changed since last interpret).
- **Missing** — drawing has no companion yet.
- **Generated body** — the machine-written summary of what the drawing shows; safe to rewrite on reinterpret.
- **Curated ideas** — a human-owned section in the companion for intent, talking points, and corrections; regenerate/reinterpret must preserve it unless the operator explicitly opts into overwriting that section.

**Model.** Generate companions **once** for drawings that lack them (bootstrap / missing only). Later, **reinterpret on demand** via an outer-shell skill (and optional scripted helpers). Curate ideas in the companion anytime. A status/check path reports missing and stale without implying an automatic rewrite of curated files.

## M1: Companion file contract and checksum (Status: IMPLEMENTED)

Pin the pairing, frontmatter, and section shape so generate/check/skill all agree before any bulk write.

**Acceptance Criteria:**

- [x] Every companion path is exactly `docs/drawings/<stem>.md` for drawing `docs/drawings/<stem>.excalidraw` (same directory, same stem; not under `output/`).
- [x] Each companion has YAML frontmatter that records at least: the drawing basename (or relative path), the source checksum, and a generation marker (timestamp and/or tool id). Field names are pinned in Implementation Details.
- [x] The companion body has a clearly delimited **generated** summary region and a clearly delimited **curated ideas** region (heading names or HTML comment markers pinned). A documented rule states that reinterpret updates only the generated region by default.
- [x] A small fixture or unit test asserts: given a fixture drawing + companion, checksum mismatch is detectable as stale; matching checksum is not stale; wrong stem pairing fails the contract check. It does not start Claude.

**Implementation Details:**

- Frontmatter keys: `drawing` (basename), `source_sha256` (hex), `generated_by`, `generated_at` (UTC `YYYY-MM-DDTHH:MM:SSZ`).
- Regions: `<!-- generated:begin/end -->` and `<!-- curated:begin/end -->`. Reinterpret updates generated + checksum fields only by default.
- Library/CLI: `scripts/drawing-companions` (`companion_path_for`, `parse_companion`, `is_stale`, `contract_errors`, `render_companion`).
- Test: `tests/v18_drawing_companions_test.py` (`DrawingCompanionsM1`).

## M2: Generate-missing and stale status (Status: IMPLEMENTED)

Directors need a deterministic outer path to bootstrap companions once and to see which companions no longer match their drawings—without silently overwriting curated ideas.

**Acceptance Criteria:**

- [x] A script and/or `just` recipe (names pinned) can **create companions only where missing** for every `docs/drawings/*.excalidraw`, writing a valid M1-shaped file whose source checksum matches the drawing at write time. Existing companions are left untouched by the default “generate missing” path.
- [x] A status/check path (same tool with a flag, or a sibling recipe—pinned) lists **missing** and **stale** companions and exits non-zero when any are found (or prints a clear board and exits non-zero only with an explicit `--fail` / check mode—behavior pinned). It does not rewrite files.
- [x] Default generate-missing may leave a stub/placeholder summary when no LLM is available (allowed and documented); full prose interpretation is owned by M3. The test covers missing→create, “do not overwrite existing,” and stale detection on a fixture tree. It does not start Claude. Root `flake.nix` stays untouched.

**Implementation Details:**

- CLI: `scripts/drawing-companions generate-missing [dir]`, `status [--fail] [dir]`, `checksum <drawing>`.
- Recipes: `just drawing-companions-generate`, `just drawing-companions-status` (exit 0 board), `just drawing-companions-check` (`status --fail`).
- Bootstrap: ran generate-missing once for all current `docs/drawings/*.excalidraw` stubs.
- Test: `DrawingCompanionsM2` in `tests/v18_drawing_companions_test.py`.

## M3: Outer skill — interpret, reinterpret, add ideas (Status: IMPLEMENTED)

The outer shell gets a Claude skill that turns a drawing into (or refreshes) its companion on demand, and that helps the author append ideas without fighting the checksum contract.

**Acceptance Criteria:**

- [x] A Claude skill lives under `.claude/skills/` (path pinned) whose description triggers on drawing / excalidraw / companion / interpret / reinterpret / “what does this drawing show” language.
- [x] The skill workflow: (1) read the named `.excalidraw` (and existing companion if any), (2) write or refresh the **generated** summary so it describes what the drawing shows, (3) set/update the source checksum to the current drawing bytes, (4) **preserve** the curated-ideas region unless the user explicitly asks to clear or replace it, (5) support an explicit **reinterpret** path when the companion is stale or the user wants a fresh reading.
- [x] The skill documents how to **add the user’s own ideas** into the curated region (append/edit) without requiring a full regenerate, and how checksum/status from M2 relates to “this prose may be out of date.”
- [x] The test asserts skill file presence, required workflow phrases (checksum, preserve curated ideas, reinterpret), and that it references the M1 path/contract. It does not start a live Claude session in CI.

**Implementation Details:**

- Skill: `.claude/skills/drawing-companions/SKILL.md` (`/drawing-companions`).
- Test: `DrawingCompanionsM3` in `tests/v18_drawing_companions_test.py`.

## Non-goals

- Auto-regenerating every companion on every drawing save or git hook in this version (on-demand + generate-missing only; hooks may come later).
- Treating exported SVGs under `docs/drawings/output/` as drawings that need companions.
- Requiring `.mmd` / Mermaid sources to have the same companion contract in this version (may follow later).
- Using the companion as the slide/deck source of truth (decks still embed SVG/assets; companions are interpretation aids).
- Editing root `flake.nix` for this feature set.
- Guaranteeing LLM-quality summaries inside the deterministic generate-missing path (stubs allowed; skill owns rich reinterpretation).
