# Presentation bridge — lesson-backed Steckbriefs

Every unit in the reveal-md deck is an **exercise** (`presentation/lessons/<id>.md`,
id shape `[lesson-]<word><digits>[letter]?` so `build-deck` can splice it — e.g.
`harness1`, `lesson-refine1a`, `lesson-skills1`). Steckbriefs use the `lesson-`
prefix so they never overwrite theory slides. A **lesson** is a sandbox
hands-on unit in `workshop/JOURNEY.md`. Lessons are not a second slide kind: some
exercises are optionally **backed** by a lesson and rendered as a **Steckbrief**.

## Bindings

Edit `bindings.yaml`:

```yaml
- exercise: lesson-refine1
  lesson: refine-1
  name: Refine
  lead: optional director note (kept here only; never rendered)
```

List that exercise id in a spine’s `<!-- lessons -->` menu. Then:

```sh
just present            # rebuild=yes (default): bridge → build-deck → serve .build/
just present rebuild=no # serve existing .build/ without reassembling
just present-build      # assemble only (no server)
```

`presentation/.bin/build-deck` always runs `scripts/presentation-bridge` first.
Template: `steckbrief.md` — title uses **🏝️** (sandbox / journey-backed), not 💡.
Three verticals reuse `## <Name> <n>`: title measures, then prepare+worktree
in a two-column layout (`*PREPARE*` left, `*WORKTREE*` right), then
`*PROMPT TO TEST*` / `*EXPECTED OBSERVATIONS*`. Last-run measures sit on the
title strip.

When `workshop/results/<lesson-id>/EXPLANATION.md` exists, the bridge appends its
marked region (`<!-- showcase:begin -->`…`<!-- showcase:end -->`, or the whole
file) as further verticals after the Steckbrief. Each vertical needs **one**
title (`## Results: …` etc.) — do not add a blanket `## Showcase` heading; the
theme brackets every h1/h2 and a second title doubles on one slide. Gate:
`scripts/slide-double-heading` (wired into `just present-check-smooth`).

## Hand edits

Keep local tweaks between `<!-- hand:begin -->` and `<!-- hand:end -->`. Sync
preserves that region unless you pass `--overwrite` to `presentation-bridge`.

Skills: `.claude/skills/steckbrief/SKILL.md`, `.claude/skills/deck-smoothness/SKILL.md`.
Mechanical gate: `just present-check-smooth`.
