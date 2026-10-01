# CLAUDE.md

## Layout

```
README.md          project intro
justfile           just check / test / fmt
.claude/           hooks and settings
docs/PROMPTS.md    append-only prompt log
docs/specs/        write specs here (create the directory if needed)
```

Do not rediscover the tree with broad `find` or `ls -R`. Read these paths directly. Write the spec under `docs/specs/` from the user prompt; do not dig through git history for earlier specs unless the prompt says to.

## Checks

```sh
just check       # scalafmt, compile with -Werror, tests — the one gate
sbt compile      # the first reviewer
sbt test
sbt scalafmtAll
```
