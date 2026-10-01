# 🏝️ Quality Gates 4

**Quiet the app under a redundancy gate.** The app grew steep features and now carries copy/paste debt. Wire the redundancy gate, run the skill, and refactor until the quiet report is empty.

<!-- journey: quality-gates-4 -->
<!-- backing-lesson: quality-gates-4 -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 01:51
- Last Token Usage: 485.3k
- Results: `workshop/results/quality-gates-4/2026-09-30-09-12-10`
- Material: `workshop/material/quality-gates-4/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Quality Gates 4

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare quality-gates-4
just claude
```

</div>
<div class="column">

*WORKTREE*

```plaintext
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   ├── skills/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── scripts/
│   ├── check-redundancies-cpd/
│   ├── spec-check-scala/
│   └── check-redundancies
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

</div>
</div>

----

<!-- .slide: class="steckbrief-prompt-obs" -->

## Quality Gates 4

*PROMPT TO TEST*

```plaintext
check redundancies in the app sources and refactor until just
check-redundancies --fail-on-findings is quiet
```

*EXPECTED OBSERVATIONS*

- A redundancy report exists and lists findings ordered by size × occurrences (or is empty after fixes).
- The skill proposes a concrete refactor (parameterize, abstract, push responsibility) for at least one finding.
- After fixes, the quiet baseline has zero actionable findings (allowlisted items documented).

