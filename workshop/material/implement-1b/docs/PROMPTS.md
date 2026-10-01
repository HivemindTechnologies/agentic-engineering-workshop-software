# Prompts

Append-only, written by `.claude/hooks/log-prompt.sh`. Do not edit past entries.

## 2026-09-28T16:53:12Z · 630192d8

```text
## implement-1: Implement the SPEC (last: FAIL judge 2026-09-28-18-47-55)

Implement the SPEC one milestone at a time. The implement command accepts any of these:

- /implement @docs/specs/SPEC.v1-todo-list-cli-mvp.md M1
- /implement v1.M1
- /implement M1
- /implement M1, M2
- /implement M1-M3

```sh
just prepare implement-1
just claude
```

*PROMPT TO TEST*
```
/implement M1
```

*EXPECTED OBSERVATIONS*
- The changes should be implemented, and the SPEC should flip the status of the milestone to "IMPLEMENTED".
- The implementation details paragraph should be added to the milestone section.
- The changes should be committed to the git repository.
- The changes should not be pushed to the remote repository.
- You should be asked if the changes can be marked as done.
- If you say yes, it should create another commit flipping the status of the milestone to "DONE" and all acceptance criteria should be checked.
```
