---
drawing: hitl-options.excalidraw
source_sha256: e1c526d470b6c563051e8126b86b2baecbd31867954657c64c77d8780aa99b57
generated_by: drawing-companions-skill
generated_at: 2026-09-30T14:03:37Z
---

<!-- generated:begin -->
## Summary

Wide AGUI / HITL options sketch: minimize / facilitate / simplify **the rest** for **the Human in the loop**.

Left: orange person with **Context / Prompt propagation** into **AGUI**, branching to **custom UI + CopilotKit** and **IDE + VSCode plugin**.

Center: blue agent → orange human with a loop back (same HITL cycle as `hitl`). Far right: blue and orange curved arrows.

Surface choice (custom UI vs IDE plugin) while the loop and “shrink the rest” message stay the same.
<!-- generated:end -->

<!-- curated:begin -->
## Ideas

Follow-up to *human in the loop*: once you know the goal is to shrink the
human rest, minimize / facilitate / simplify what they still have to review —
and pick (or build) a decision-making surface for that leftover.

Piggyback on existing NLP infrastructure when you can: IDE + VS Code plugin,
Cursor, Terminal UI with Claude Code, Claude Desktop + MCP — then bolt your
process-specific bits on top. UI-heavy review → prefer IDE + plugin. Sometimes
a self-contained static web page with all review context is enough; the human
decides there, and context/prompt propagation brings the decision back into
chat.

If that is not enough: custom UI + something that speaks to agents (e.g.
CopilotKit over AGUI), or IDE + VS Code plugin extended via AGUI. Today we
mostly use Claude Code and its share/extend mechanisms — keep the other
options in mind. Coding itself is a HITL process; you can pick the tools and
UIs and extend their abilities.
<!-- curated:end -->
