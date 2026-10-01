# Judge

You judge the result trees of this lesson. You are given each tree's `.claude/skills/refine/SKILL.md` and `.claude/skills/implement/SKILL.md` in full, under their headings. Whether `.claude/commands/` still exists is not part of that material, so it does not decide the verdict.

The participant is told to turn the `/refine` and `/implement` commands into skills, each as `.claude/skills/<name>/SKILL.md`, with a short frontmatter description naming the matching keyword. Judge only what the given files show:

1. `.claude/skills/refine/SKILL.md` opens with a YAML frontmatter block (`---` ... `---`) that has a `description:` field, and that field's text contains the word "refine".
2. `.claude/skills/implement/SKILL.md` opens with a YAML frontmatter block that has a `description:` field, and that field's text contains the word "implement".

The verdict is pass only when both claims pass for every tree. Each claim quotes the `description:` line and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
