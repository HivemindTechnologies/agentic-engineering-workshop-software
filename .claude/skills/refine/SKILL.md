---
name: refine
description: Write or change a spec in docs/specs, run scripts/spec-check, then stop for review. Commit only after the user agrees.
---

# /refine — Refine Milestone or Spec

Create reviewable documentation in spec files. Agent proposes changes, user reviews, then agent commits. Focus on getting documentation right - commit is minor.

## Format

Each milestone: heading (`## M<N>: <Title>`), optional description, **Acceptance Criteria** (required). **Implementation Details** added after implementation, not during refinement. Do not add '###' nor 'M<N>:' to the **Implementation Details** subsection.

Labels must be headless bold with a colon inside the markers: `**Acceptance Criteria:**` / `**Implementation Details:**`.

Headless subsections stay in this order: criteria, then details, each label alone on its line, details never before criteria.

## Milestone IDs

Pattern: `M\d+` optionally followed by either a letter postfix (`M2a`, `M2implement-1`) **or** one or more hyphenated lesson-bound slugs (`M2-implement-1`, `M2-quality-gates-3`). Each hyphen slug starts with a letter or digit. Groups (H2, e.g. `## M1 — ...`) are the bare `M\d+` form.
Individual milestones (H3, e.g. `### M1a — ...`) require a postfix; letter-first and hyphen-slug forms are both valid — the hard rule is only that `M<digits>` stays unambiguous to parse.
A single letter (`M1a`) is the default; a slug (`M3orders`), a country code (`M2de`), or a lesson id (`M2-implement-1`) are equally valid if that's what fits the project.

Numbering is local to each spec file, not a global counter — `SPECS.v1.md` and `SPECS.v2.md` each start their own `M0`/`M1` independently, so `M1a` in v1 and `M1a` in v2 are unrelated milestones.
When referring to a milestone anywhere the spec version could be ambiguous — commit messages, cross-spec references, conversation summaries — use the fully-qualified form `v<N>.M<id>` (e.g. `v1.M4c`, `v2.M1`, `v16.M2-implement-1`).
Within a single spec file's own milestone headings, the bare `M<id>` form is fine; the version is already implied by the file.

## Flat by default, nested only when it earns it

**A milestone is a single H2.** `## M1: <Title>` with its own status and Acceptance Criteria, bare ID, no postfix. This is the normal shape and what you write unless you have a specific reason not to.

Promote a milestone to a **group** (H2 with no criteria of its own, plus two or more H3 children) only when the work genuinely splits into parts that are implemented, reviewed and statused **separately** — e.g. `M0` splitting into `M0a` parent POM and `M0b` Compose stack, which land in different commits and can be DONE at different times.

A group with exactly one child is always wrong. `## M1` containing only `### M1a` is the same milestone written twice; collapse it to `## M1`. If you find yourself writing an H2 whose only content is one H3, that's the signal the milestone was never a group.

Do not invent a split the user did not ask for. Splitting is a decision to surface for review, not a default to apply — when a milestone looks borderline, write it flat and say in your proposal that it could be split, rather than splitting it pre-emptively.

## Milestone Status

Every heading that owns Acceptance Criteria ends with `(Status: <STATE>)` — one wrapper for all states, no exceptions. That is the H2 for a flat milestone (`## M1: Title (Status: PENDING)`) and each H3 for a grouped one. A group H2 owns no criteria and therefore carries no status; its state is whatever its children say.
`DONE` is the only state that also carries a checkmark, `(Status: ✅ DONE)`, since it's the one worth standing out; every other state stays plain text — reusing the checkmark anywhere else would make `✅` ambiguous about what's actually finished and reviewed.
States, roughly in the order a milestone moves through them: `PENDING` (not started) → `IMPLEMENTING` (work started, not finished — exists so a killed session leaves a record of where things stood, not silence) → `IMPLEMENTED` (code done and Implementation Details written, not yet reviewed) → `DONE` (an IMPLEMENTED milestone that's been reviewed).
Off that path: `PARTIALLY_DONE` (some but not all Acceptance Criteria met), `SKIPPED` (decided against), `POSTPONED` (deferred).
Exact format and states are validated by `scripts/spec-check`. That script is the source of truth, not this file.

## Acceptance criteria ↔ tests

Phrase each AC so `/implement` can map it to a unit test or fixture integration test. A new criterion is written as `- [ ]`.

## Workflow

Agent proposes → user reviews → agent commits.

After writing or editing a spec, run `scripts/spec-check` on that file before stopping for review.

Before editing a spec, run `scripts/tocmd` on that file to list its headings. Use `scripts/tocmd --lines` when you need the line number of a milestone.
