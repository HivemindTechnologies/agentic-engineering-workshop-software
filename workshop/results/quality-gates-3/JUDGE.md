# Judge

You judge the result trees of this lesson.

The participant is told to add `just spec-check` as a new pre-commit hook, try a commit, and fix any structure violations until the check and the commit succeed.

Judge these claims on each tree:

1. A git hook is wired so commits run `just spec-check` (the file names `just spec-check`, or an equivalent invocation of the sandbox Scala/Python structure checker), not only `just check` alone.
2. The product spec under `docs/specs/SPEC.v1-todo-list-cli-mvp.md` (or the tree's SPEC.v1*.md) has milestone headings and checkbox acceptance criteria that the structure checker accepts — statuses and boxes agree; labels are the exact `**Acceptance Criteria:**` / `**Implementation Details:**` lines.

The verdict is pass only when both claims pass for every tree. Quote the hook line and the spec heading evidence; name the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
