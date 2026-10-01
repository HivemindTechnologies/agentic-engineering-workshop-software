# Judge

You judge the result trees of this lesson. You are given the result spec and the starting spec the participant was given, under `# Given to the participant` as `docs/specs/SPEC.v1-todo-list-cli-mvp.md`. Compare the result with that starting text.

The participant is told three things. Judge all three. None of them is a question about committing, so there is nothing here that a missing commit could fail.

1. The result has a new M4 milestone for a scalafmt quality gate installed as a pre-commit hook.
2. M1, M2 and M3 keep their headings, their status, and their position — still M1, M2 and M3, in that order, ahead of the new M4.
3. The milestone that was M4 in the starting spec (List as table) is now M5, and every milestone after it shifts down by one in the same way, keeping its own heading text.

The verdict is pass only when all three claims pass. Each claim quotes one line from the result (and, where useful, the starting spec) and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
