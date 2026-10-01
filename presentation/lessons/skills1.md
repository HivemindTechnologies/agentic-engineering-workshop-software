# 💡 Skills 1

**Skills and Commands.** Two kinds of file hold how your team works: a skill is loaded by the model when its description matches, a command is started by a human.
Both are plain Markdown in the repository, reviewed like code.

----

## Anatomy of a `SKILL.md`

<!-- `text`, not `markdown`: the highlighter reads the line above `---` as a heading. -->
```text
---
name: working-in-a-git-worktree
description: Use when starting a feature in a git repository,
  when committing that work, or when a failed approach has to be replaced
---

# Working in a Git Worktree

One feature, one worktree ...
```

- `description`: the only part read before loading, so it does the matching
- Body: the procedure, most important first

----

## Command or skill

Both are a Markdown file with instructions. The difference is who starts it:

- **Command**: only you, e.g. `/refine`
- **Skill**: the agent, when the task matches

A command is a skill with `disable-model-invocation: true`.

----

## Prose has no compiler

<img src="assets/images/monkeyuser-273-natural-language-instructions.png" alt="an AI machine on a rooftop fires a laser at the city; a developer at the laptop: here's the problem, you wrote evil instead of eval" class="comic">

<p class="credit">MonkeyUser · “Natural Language Instructions” · monkeyuser.com/2024/natural-language-queries</p>
