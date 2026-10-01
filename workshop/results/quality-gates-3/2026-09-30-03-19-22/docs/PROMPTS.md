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

## 2026-09-28T20:07:20Z · 64af4c06

```text
## implement-1b: Mark the milestone as done

To complete the workflow mark the milestone as done after your review.

```sh
just prepare implement-1b
just claude
```

*PROMPT TO TEST*
```
mark done and commit
```

*EXPECTED OBSERVATIONS*
- The milestone should be marked as "DONE"
- The changes should be committed to the git repository
```

## 2026-09-28T20:13:54Z · 2f07bf7f

```text
## implement-2: Implement real function with next two milestones

```sh
just prepare implement-2
just claude
```

*PROMPT TO TEST*
```
/implement M2 + M3
```

*EXPECTED OBSERVATIONS*
- There is a hello world in the application
- There is a basic implementation of the create and read todos functionality
- The resulting application is runnable
- The generated code contains tests for the new functionality
```

## 2026-09-28T20:37:32Z · 46b841b3

```text
## quality-gates-1: Introduce a pre commit hook to run just check

To make sure the code is always in a good state it is advisable to introduce a pre commit hook to run just check.

```sh
just prepare quality-gates-1
just claude
```

*PROMPT TO TEST*
```
Add a pre commit hook to run just check on every commit.
```

*EXPECTED OBSERVATIONS*
- The pre commit hook is available on the local git repository
```

## 2026-09-28T20:49:11Z · 684a837c

```text
## refine-7: Rerefine the spec to add a scalafmt quality gate

To showcase the ability to refine an existing and inflight SPEC add a scalafmt quality gate.
It also demonstrates to change the ordering and number of milestones.

```sh
just prepare refine-7
just claude
```

*PROMPT TO TEST*
```
/refine @docs/specs/SPEC.v1-todo-list-cli-mvp.md insert a scalafmt quality gate as pre commit hook as the new M4 and push the other milestones down
```

*EXPECTED OBSERVATIONS*
- The SPEC should be updated with the new quality gate as inserted milestone M4
- The implemented milestones M1-M3 should stay where they were
- The old M4 is moved down to M5
```

## 2026-09-29T00:11:58Z · 7b964505

```text
## quality-gates-2: Run just check on every commit (last: PASS 2026-09-28-22-57-32)

Implement the new milestone M4

```sh
just prepare quality-gates-2
just claude
```

*PROMPT TO TEST*
```
/implement M4
```

*EXPECTED OBSERVATIONS*
- When we change the formatting of the code on purpose the pre commit hook catches it and fails the next commit attempt
<!-- director: we need to make the just file evolve gradually and not contain the scalafmt right away, that is part of the previous lesson and implementation of the milestone, so the initial just file inside the sandbox should focus on tests only until we add the scalafmt angle on refine-7 -->
```

## 2026-09-29T00:16:20Z · 3f5ca96b

```text
## skills-1: Make the claude commands into skills

Commands behave differently in Cursor than in Claude.
Claude always loads something to auto load the commands and treat it as a skill.
Therefore they occupy some upfront context on the first run.
We will turn the commands now into skills and then we will see that they auto load themselfs without you having to remember they exist.

```sh
just prepare skills-1
just claude
```

*PROMPT TO TEST*
```
make the claude commands /refine and /implement into skills, each as .claude/skills/<name>/SKILL.md, and add a short frontmatter description to each skill including the "refine" and "implement" keywords for each accordingly
```

*EXPECTED OBSERVATIONS*
- The .claude/commands should no longer contain the refine.md and implement.md commands
- The .claude/skills directory should contain refine/SKILL.md and implement/SKILL.md
- The refine skill has a frontmatter description that includes the "refine" keyword
```

## 2026-09-30T01:19:24Z · c107c929

```text
# quality-gates-3: Have the specs being checked deterministically

For now the specs are structured by the mercy of the llm gods and their attention span, or our ability to not specify contradictory requirements or too large gaps. Lets add a new quality gate that checks the structure of the specs to increase familiarity across team members for greater communication. We keep using the old spec and will use the spec check with the altered skills to bring it into alignment with the new structure.

<!-- director: we take the same material from after completing skills-2 and add the scala spec check to the material for this lesson so that it becomes executable via just spec-check and have both refine and implement reference it and basically take the outer shells variation but with the changed call or we both align them to use just spec-check on the outer and the develop shell so that the skills look the same even if we may use the python variant on the just spec-check variation and the commit hook so this introduces rather a lot in a single lesson -->

*PROMPT TO TEST*
```
add `just spec-check` as a new pre commit hook, try commit and fix the violations if any
```

*EXPECTED OBSERVATIONS*
- The pre commit hook should be installed
- The commit should have failed at first
- The spec should be updated to the new structure
- The spec check should pass after the violations are fixed
- The commit should succeed in the end
```
