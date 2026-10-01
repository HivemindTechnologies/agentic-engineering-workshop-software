# Prompts

Append-only, written by `.claude/hooks/log-prompt.sh`. Do not edit past entries.

## 2026-09-29T22:34:40Z · 0ffb9015

```text
# refine-1: First non standard refine prompt (last: PASS 2026-09-29-11-38-24)
Minimum Runtime: 00:24
Last Token Usage: 145.8k
[Results](workshop/results/refine-1/2026-09-29-11-38-24)
[Material](workshop/material/00-base/)
[develop](develop/)

Try this prompt a few times, in a fresh session each time (`just prepare refine-1` again).

*PROMPT TO TEST*
```
create a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI. Scala 3, pure FP, Cats, and just check runs the tests. Commands are add, list, done, and remove. The store is one YAML file, todos.yaml, read and written with org.virtuslab::scala-yaml, in the current directory. No color, no table, no Markdown.
```

*EXPECTED OBSERVATIONS*
- The spec stays inside that paragraph: the four commands, todos.yaml, and just check.
- The spec states org.virtuslab::scala-yaml and todos.yaml.
- It does not add color, a table, or Markdown.
```
