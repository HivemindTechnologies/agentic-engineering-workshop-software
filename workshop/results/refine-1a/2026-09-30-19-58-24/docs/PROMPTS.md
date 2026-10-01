# Prompts

Append-only, written by `.claude/hooks/log-prompt.sh`. Do not edit past entries.

## 2026-09-30T17:58:27Z · 987d984b

```text
# refine-1a: The same prompt, now under /refine (last: PASS 2026-09-29-02-27-21)
Minimum Runtime: 01:00
Last Token Usage: 135.1k
[Results](workshop/results/refine-1a/2026-09-29-02-27-21)
[Material](workshop/material/refine-1a/)
[develop](develop/)

The prompt is the refine-1 request with `/refine` in front. The command says to ask when a criterion would otherwise be a guess.

```sh
just prepare refine-1a
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── docs/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/refine a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI. Scala 3, pure FP, Cats, and just check runs the tests. Commands are add, list, done, and remove. The store is one YAML file, todos.yaml, read and written with org.virtuslab::scala-yaml, in the current directory. No color, no table, no Markdown.

Write the spec from that paragraph. Do not ask, and do not add a criterion the paragraph does not state.
```

*EXPECTED OBSERVATIONS*
- It writes the spec from the paragraph.
- It does not add color, a table, or Markdown.
```
