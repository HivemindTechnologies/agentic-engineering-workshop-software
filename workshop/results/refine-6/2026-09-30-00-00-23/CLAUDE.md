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

## Layout

```
docs/rules/     ways of working
docs/specs/     one file per spec version
docs/PROMPTS.md every prompt, in order
.claude/        commands, hooks, settings
```

Do not rediscover the tree with broad `find` or walk git history unless the prompt asks. Prefer reading `docs/rules/WOW.md` and the named spec path directly.
