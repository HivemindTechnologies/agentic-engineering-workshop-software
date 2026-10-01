# 🏝️ Quality Gates 2

**Run just check on every commit.** Implement the new milestone M4

<!-- journey: quality-gates-2 -->
<!-- backing-lesson: quality-gates-2 -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 02:56
- Last Token Usage: 954.7k
- Results: `workshop/results/quality-gates-2/2026-09-29-02-11-56`
- Material: `workshop/material/quality-gates-2/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Quality Gates 2

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare quality-gates-2
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

## Quality Gates 2

*PROMPT TO TEST*

```plaintext
/implement M4
```

*EXPECTED OBSERVATIONS*

- When we change the formatting of the code on purpose the pre commit hook catches it and fails the next commit attempt
<!-- director: we need to make the just file evolve gradually and not contain the scalafmt right away, that is part of the previous lesson and implementation of the milestone, so the initial just file inside the sandbox should focus on tests only until we add the scalafmt angle on refine-7 -->

