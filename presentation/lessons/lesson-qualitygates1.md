# 🏝️ Quality Gates 1

**Introduce a pre commit hook to run just check.** To make sure the code is always in a good state it is advisable to introduce a pre commit hook to run just check.

<!-- journey: quality-gates-1 -->
<!-- backing-lesson: quality-gates-1 -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 01:30
- Last Token Usage: 899.7k
- Results: `workshop/results/quality-gates-1/2026-09-29-07-30-16`
- Material: `workshop/material/quality-gates-1/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Quality Gates 1

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare quality-gates-1
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
│   └── settings.json
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
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

## Quality Gates 1

*PROMPT TO TEST*

```plaintext
Add a pre commit hook to run just check on every commit.
```

*EXPECTED OBSERVATIONS*

- The pre commit hook is available on the local git repository

