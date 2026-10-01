# Prompts

Append-only, written by `.claude/hooks/log-prompt.sh`. Do not edit past entries.

## 2026-09-29T22:00:27Z · 9b2ec4d8

```text
# refine-6: More ideas for further refinements in new SPECs (last: PASS 2026-09-29-02-37-48)
Minimum Runtime: 00:26
Last Token Usage: 125.3k
[Results](workshop/results/refine-6/2026-09-29-02-37-48)
[Material](workshop/material/refine-6/)
[develop](develop/)

Further ideas how to refine the prompt before running it. These ideas usually flow in naturally as you start refining or later also start implementing. You could have known all the details upfront and refine your initial prompt, or refine the resulting initial SPEC, that is up to you.

- Add a specific cli parsing library as a requirement
- Define the synopsis of the CLI
- Specify the way the data is persisted, file based, sqlite, remote database, s3...
- Defaults via ENV vars, config files, cli ARGS and their precedence
- Filtering, sorting, priorities, due dates, tags, etc.

```sh
just prepare refine-6
just claude
```

*PROMPT TO TEST*
```
/refine @docs/specs/SPEC.v1-todo-list-cli-mvp.md add cli parsing lib decline as the preferred library for parsing cli arguments in M3
```

*EXPECTED OBSERVATIONS*
- You should be asked if the changes are fine and should be committed.
- The SPEC should be updated the requested changes.
- Nothing else should be changed.
```
