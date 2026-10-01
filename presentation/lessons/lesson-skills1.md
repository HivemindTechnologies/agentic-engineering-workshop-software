# 🏝️ Skills 1

**Make the claude commands into skills.** Commands behave differently in Cursor than in Claude. Claude always loads something to auto load the commands and treat it as a skill. Therefore they occupy some upfront context on the first run. We will turn the commands now into skills and then we will see that they auto load themselfs without you having to remember they exist.

<!-- journey: skills-1 -->
<!-- backing-lesson: skills-1 -->
<!-- steckbrief:generated -->

**Last run**

- Minimum Runtime: 00:51
- Last Token Usage: 212.9k
- Results: `workshop/results/skills-1/2026-09-29-02-17-18`
- Material: `workshop/material/skills-1/`
- develop: `develop/`

<!-- hand:begin -->
<!-- Optional hand edits between these markers survive `presentation-bridge`
     unless you pass `--overwrite`. Keep slide separators (`----` / `---`)
     consistent with lessons/_template.md. -->
<!-- hand:end -->

----

## Skills 1

<div class="two-column">
<div class="column">

*PREPARE*

```sh
just prepare skills-1
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

## Skills 1

*PROMPT TO TEST*

```plaintext
make the claude commands /refine and /implement into skills, each as
.claude/skills/<name>/SKILL.md, and add a short frontmatter description
to each skill including the "refine" and "implement" keywords for each
accordingly
```

*EXPECTED OBSERVATIONS*

- The .claude/commands should no longer contain the refine.md and implement.md commands
- The .claude/skills directory should contain refine/SKILL.md and implement/SKILL.md
- The refine skill has a frontmatter description that includes the "refine" keyword

