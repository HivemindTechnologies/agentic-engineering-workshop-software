---
name: steckbrief
description: >-
  Sync lesson-backed Steckbrief slides from workshop/JOURNEY.md into the
  reveal-md deck. Use when editing Steckbrief cards, journey-slide bindings,
  lesson-backed exercises, presentation/bridge bindings, or when a director
  asks to refresh prepare / worktree / prompt slides from the journey.
---

# /steckbrief — Sync journey Steckbriefs into the deck

Lesson-backed exercises are ordinary deck **exercises** (`presentation/lessons/<id>.md`)
whose body is a **Steckbrief** derived from a journey **lesson**. Do not invent a
second slide kind. Steckbrief exercise files use a `lesson-` prefix
(`lesson-refine1`, `lesson-skills1`) so they never clash with theory slides.

## Source of truth

| Piece | Path |
|-------|------|
| Bindings | `presentation/bridge/bindings.yaml` |
| Template | `presentation/bridge/steckbrief.md` |
| Generator | `scripts/presentation-bridge` |
| Journey | `workshop/JOURNEY.md` |

## Workflow

1. Confirm the binding (`exercise`, `lesson`, optional `name` / `lead`).
2. Run from the repo root:

```sh
python3 scripts/presentation-bridge
# or open the deck (rebuilds by default):
just present
```

3. Open `presentation/lessons/<exercise>.md`. Generated verticals cover
   prepare+worktree (two-column), and `*PROMPT TO TEST*` /
   `*EXPECTED OBSERVATIONS*`, plus last-run measures when the JOURNEY heading
   carries them.
4. Put facilitator-only tweaks between `<!-- hand:begin -->` and `<!-- hand:end -->`.
   Those markers survive the next sync. Use `--overwrite` only when the hand region
   should be wiped back to the template stub.
5. Keep separators (`----` vertical, `---` horizontal) aligned with
   `presentation/lessons/_template.md`. No second CSS theme.

## Anti-patterns

- Hand-editing generated Steckbrief body outside the hand region (next sync clobbers it)
- Renaming the exercise id away from `^(?:[a-z]+-)*[a-z]+\d+[a-z]?$` (breaks `build-deck`)
- Duplicating JOURNEY prompts in spine markdown instead of binding + sync
