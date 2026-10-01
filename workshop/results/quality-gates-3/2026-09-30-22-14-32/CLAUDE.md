# CLAUDE.md

## Rules

Read `docs/rules/WOW.md` before writing or changing code. It is binding. 

## Checks

```sh
just check       # scalafmt, compile with -Werror, tests — the one gate
sbt compile      # the first reviewer
sbt test
sbt scalafmtAll
```

Run `just install-hooks` once per clone so `just check` also runs as a pre-commit hook.

## Layout

```
docs/rules/     ways of working
docs/specs/     one file per spec version
docs/PROMPTS.md every prompt, in order
.claude/        commands, hooks, settings
.githooks/      git hooks (`just install-hooks` to enable)
```
