# 🏝️ Quality Gates 3

**Have the specs being checked deterministically.** For now the specs are structured by the mercy of the llm gods and their attention span, or our ability to not specify contradictory requirements or too large gaps. Lets add a new quality gate that checks the structure of the specs to increase familiarity across team members for greater communication. We keep using the old spec and will use the spec check with the altered skills to bring it into alignment with the new structure.

<!-- journey: quality-gates-3 -->
<!-- backing-lesson: quality-gates-3 -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 03:56
- Last Token Usage: 2148.2k
- Results: `workshop/results/quality-gates-3/2026-09-30-03-19-22`
- Material: `workshop/material/quality-gates-3/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Quality Gates 3

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare quality-gates-3
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
│   └── spec-check-scala/
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

## Quality Gates 3

*PROMPT TO TEST*

```plaintext
add `just spec-check` as a new pre commit hook, try commit and fix the
violations if any
```

*EXPECTED OBSERVATIONS*

- The pre commit hook should be installed
- The commit should have failed at first
- The spec should be updated to the new structure
- The spec check should pass after the violations are fixed
- The commit should succeed in the end

