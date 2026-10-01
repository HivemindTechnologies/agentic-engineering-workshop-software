---
drawing: quality-gates.excalidraw
source_sha256: e971f6b8a64b0535d97cceae32592ac42d00c4d6f5d2d6ae89c7f4990cce34ec
generated_by: drawing-companions-skill
generated_at: 2026-09-30T14:03:37Z
---

<!-- generated:begin -->
## Summary

Top: **AI** (robot) **generates** jagged **code Mountains**.

Middle: orange title **Quality Gates** — six Swiss-cheese slices in a dashed orange frame, labeled **Linter · compiler · CPD · CC · conventions · tests**. Many arrows in, one arrow out.

Bottom: orange **Reduce Code for** a pair of glasses (human review).

Layered deterministic gates thin AI mountains of code down to what a human can read.
<!-- generated:end -->

<!-- curated:begin -->
## Ideas

Closing piece of the story: AI generates mountains of code fast. Be deliberate
about which quality gates you stack — Swiss-cheese slices, each filtering out
invalid states (non-compiling, impure, imperfect, off-standard). Every slice
shrinks what is left for a human to review. Only look at the mountain once all
gates have passed.

Go further when it helps: run it and inspect the results (e.g. UI behaviour)
before reading the code. Not always required, but often the right order —
behaviour first, code as a final quality review once it is done.
<!-- curated:end -->
