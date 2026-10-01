---
name: deck-smoothness
description: >-
  Review the assembled software reveal-md deck(s) for narrative smoothness.
  Use when checking theory→Steckbrief→showcase pairing, lesson-backed exercise
  framing, orphan agenda entries, broken includes, or abrupt topic jumps after
  just present-build / presentation-check.
---

# /deck-smoothness — Judging the composed software deck

Run the mechanical gate first; this skill is the narrative pass, not a substitute.

```sh
just present-check-smooth   # deterministic breaks only
just present-build          # assemble .build/deck-software-part*.md
```

Then read the **assembled** decks (not only the spines):

- `presentation/.build/deck-software-part1.md`
- `presentation/.build/deck-software-part2.md`

## What to look for

1. **Theory → Steckbrief → showcase** — after a theory exercise (e.g. Variance 1), a
   lesson-backed Steckbrief should follow when the journey is meant to land there;
   showcase slides (from `EXPLANATION.md`) sit after the Steckbrief verticals when
   present.
2. **Exercise framing** — every deck unit is an exercise; call out lesson-backed
   cards only where it helps directors, not as a second slide kind.
3. **Broken includes / orphans** — spine menu ids that never appear in the body,
   agenda names with no matching exercise, `<!-- backing-lesson -->` without a
   JOURNEY section, showcase markers without content.
4. **Abrupt jumps** — topic changes with no bridge sentence or divider; Part 1
   superficial quality-gate vocabulary vs Part 2 Scala depth (see SPEC.v17 spin).

## Output

Ordered findings (severity first), each with:

- location (deck file + nearby heading / exercise id)
- what feels off
- a concrete fix suggestion

Do **not** return only pass/fail. If the deck is smooth, say so in one short
paragraph after an empty findings list.
