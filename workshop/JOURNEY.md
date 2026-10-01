
Prepare a lesson from the harness root, then start Claude. Each prepare rebuilds `develop/` from the beginning through that lesson.

```sh
just prepare refine-1
just claude
```

# refine-1: First non standard refine prompt (last: FAIL simulate 2026-09-30-00-35-48)
Minimum Runtime: 00:29
Last Token Usage: 99.0k
[Results](workshop/results/refine-1/2026-09-30-00-35-48)
[Material](workshop/material/00-base/)
[develop](develop/)

Try this prompt a few times, in a fresh session each time (`just prepare refine-1` again).

*WORKTREE*
```
.
├── .claude/
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
create a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI. Scala 3, pure FP, Cats, and just check runs the tests. Commands are add, list, done, and remove. The store is one YAML file, todos.yaml, read and written with org.virtuslab::scala-yaml, in the current directory. No color, no table, no Markdown.
```

*EXPECTED OBSERVATIONS*
- The spec stays inside that paragraph: the four commands, todos.yaml, and just check.
- The spec states org.virtuslab::scala-yaml and todos.yaml.
- It does not add color, a table, or Markdown.

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

# refine-2: First real refine prompt (last: PASS 2026-09-29-02-28-32)
Minimum Runtime: 02:18
Last Token Usage: 344.7k
[Results](workshop/results/refine-2/2026-09-29-02-28-32)
[Material](workshop/material/00-base/)
[develop](develop/)

```sh
just prepare refine-2
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

These choices are settled, so write the spec:
- Commands are add, list, done, and remove.
- The store is todos.yaml in the current directory.
- just check is the test gate. The workflow file lands with the first code milestone.
- No color, no table, no Markdown.
```

*EXPECTED OBSERVATIONS*
- Won't ask anymore, because the choices are settled.
- The structure should stabilize and not vary that much anymore.
- Nor is the structure in which the app will be built always making perfect sense if we take a look at the order of the milestones and the sizes of each.
- Yet the directions it takes might go in unexpected directions, e.g. mutable state, exceptions, etc.

# refine-3: Refine prompt XP style with milestones as tiny tasks (last: PASS 2026-09-29-02-31-13)
Minimum Runtime: 02:27
Last Token Usage: 254.0k
[Results](workshop/results/refine-3/2026-09-29-02-31-13)
[Material](workshop/material/00-base/)
[develop](develop/)

```sh
just prepare refine-3
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

These choices are settled, so write the spec:
- Commands are add, list, done, and remove.
- The store is todos.yaml in the current directory.
- just check is the test gate. The workflow file lands with the first code milestone.
- No color, no table, no Markdown.

M1 scala and sbt setup
M2 cats hello world
M3 create and read todos
M4 updates
```

*EXPECTED OBSERVATIONS*
- The structure should stabilize and not vary that much anymore.
- Now the milestones are more manageable and follow your slicing proposal for each unit of work.
- Yet the directions it takes might go in unexpected directions, e.g. mutable state, exceptions, etc.

# refine-4: Refine prompt with referencing ways of working (last: PASS 2026-09-29-11-39-09)
Minimum Runtime: 01:41
Last Token Usage: 203.6k
[Results](workshop/results/refine-4/2026-09-29-11-39-09)
[Material](workshop/material/refine-4/)
[develop](develop/)

```sh
just prepare refine-4
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
│   ├── rules/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/refine a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI. Scala 3, pure FP, Cats, ways of working in @docs/rules/WOW.md, and just check runs the tests. Commands are add, list, done, and remove. The store is one YAML file, todos.yaml, read and written with org.virtuslab::scala-yaml, in the current directory. No color, no table, no Markdown.

These choices are settled, so write the spec:
- Commands are add, list, done, and remove.
- The store is todos.yaml in the current directory.
- just check is the test gate. The workflow file lands with the first code milestone.
- No color, no table, no Markdown.

M1 scala and sbt setup
M2 cats hello world
M3 create and read todos
M4 updates
```

*EXPECTED OBSERVATIONS*
- The structure should stabilize and not vary that much anymore.
- Now the milestones are more manageable and follow your slicing proposal for each unit of work.
- The direction is now more aligned with the ways of working you have defined in the WOW.md
- The usage of the refine command has become kind of verbose to remember and repeat it

# refine-5: Rerun with refined CLAUDE.md including the WOW.md (last: PASS 2026-09-29-02-35-41)
Minimum Runtime: 01:26
Last Token Usage: 206.5k
[Results](workshop/results/refine-5/2026-09-29-02-35-41)
[Material](workshop/material/refine-5/)
[develop](develop/)

```sh
just prepare refine-5
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
│   ├── rules/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/refine a docs/specs/SPEC.v1-todo-list-cli-mvp.md for a todo list CLI. Scala 3, pure FP, Cats, and just check runs the tests. Commands are add, list, done, and remove. The store is one YAML file, todos.yaml, read and written with org.virtuslab::scala-yaml, in the current directory. No color, no table, no Markdown.

These choices are settled, so write the spec:
- Commands are add, list, done, and remove.
- The store is todos.yaml in the current directory.
- just check is the test gate. The workflow file lands with the first code milestone.
- No color, no table, no Markdown.

M1 scala and sbt setup
M2 cats hello world
M3 create and read todos
M4 updates
```

*EXPECTED OBSERVATIONS*
- The structure should stabilize and not vary that much anymore.
- Now the milestones are more manageable and follow your slicing proposal for each unit of work.
- The direction is now more aligned with the ways of working you have defined in the WOW.md
- Now the refine command does not need to mention the WOW.md anymore as it is already included in the CLAUDE.md

# refine-6: More ideas for further refinements in new SPECs (last: PASS 2026-09-30-00-00-23)
Minimum Runtime: 00:56
Last Token Usage: 159.1k
[Results](workshop/results/refine-6/2026-09-30-00-00-23)
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

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/refine @docs/specs/SPEC.v1-todo-list-cli-mvp.md add cli parsing lib decline as the preferred library for parsing cli arguments in M3
```

*EXPECTED OBSERVATIONS*
- You should be asked if the changes are fine and should be committed.
- The SPEC should be updated the requested changes.
- Nothing else should be changed.


# implement-1: Implement the SPEC (last: PASS 2026-09-30-00-01-44)
Minimum Runtime: 01:57
Last Token Usage: 520.8k
[Results](workshop/results/implement-1/2026-09-30-00-01-44)
[Material](workshop/material/implement-1/)
[develop](develop/)

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

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── .gitignore
├── CLAUDE.md
├── justfile
└── README.md
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

*EXPLORE COMMANDS*
From `develop/` after `/implement M1` (toolchain only — no todo CLI yet):

```sh
just check
sbt -batch compile
sbt -batch test
sbt -batch scalafmtCheckAll
```



# implement-1b: Mark the milestone as done (last: PASS 2026-09-29-02-43-17)
Minimum Runtime: 02:13
Last Token Usage: 556.6k
[Results](workshop/results/implement-1b/2026-09-29-02-43-17)
[Material](workshop/material/implement-1b/)
[develop](develop/)

To complete the workflow mark the milestone as done after your review.

```sh
just prepare implement-1b
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
mark done and commit
```

*EXPECTED OBSERVATIONS*
- The milestone should be marked as "DONE"
- The changes should be committed to the git repository

*EXPLORE COMMANDS*
From `develop/` after the milestone is marked done in the SPEC:

```sh
just check
scripts/spec-check docs/specs/SPEC.v1-todo-list-cli-mvp.md
rg 'Status:' docs/specs/SPEC.v1-todo-list-cli-mvp.md
```



# implement-2: Implement real function with next two milestones (last: PASS 2026-09-29-07-21-14)
Minimum Runtime: 08:50
Last Token Usage: 2719.2k
[Results](workshop/results/implement-2/2026-09-29-07-21-14)
[Material](workshop/material/implement-2/)
[develop](develop/)

```sh
just prepare implement-2
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
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

*EXPLORE COMMANDS*
From `develop/` once M2+M3 exist (cwd = sandbox):

```sh
just check
sbt -batch run
sbt -batch 'run list'
sbt -batch 'run add "Buy milk"'
sbt -batch 'run add "Walk the dog"'
sbt -batch 'run list'
cat todos.yaml
```



# quality-gates-1: Introduce a pre commit hook to run just check (last: PASS 2026-09-29-07-30-16)
Minimum Runtime: 01:30
Last Token Usage: 899.7k
[Results](workshop/results/quality-gates-1/2026-09-29-07-30-16)
[Material](workshop/material/quality-gates-1/)
[develop](develop/)

To make sure the code is always in a good state it is advisable to introduce a pre commit hook to run just check.

```sh
just prepare quality-gates-1
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
Add a pre commit hook to run just check on every commit.
```

*EXPECTED OBSERVATIONS*
- The pre commit hook is available on the local git repository

*EXPLORE COMMANDS*
From `develop/` after the hook is installed (cwd = sandbox). Fail-then-pass:

```sh
# 1) break a test assertion, then:
touch test123 && git add test123 && git commit -m "expect fail"   # expect fail
# 2) restore the test / delete the break, then:
git add -A && git commit -m "expect success"   # expect success
rm -f test123
```

# refine-7: Rerefine the spec to add a scalafmt quality gate (last: PASS 2026-09-29-07-31-59)
Minimum Runtime: 01:21
Last Token Usage: 244.3k
[Results](workshop/results/refine-7/2026-09-29-07-31-59)
[Material](workshop/material/refine-7/)
[develop](develop/)

To showcase the ability to refine an existing and inflight SPEC add a scalafmt quality gate.
It also demonstrates to change the ordering and number of milestones.

```sh
just prepare refine-7
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/refine @docs/specs/SPEC.v1-todo-list-cli-mvp.md insert a scalafmt quality gate as pre commit hook as the new M4 and push the other milestones down
```

*EXPECTED OBSERVATIONS*
- The SPEC should be updated with the new quality gate as inserted milestone M4
- The implemented milestones M1-M3 should stay where they were
- The old M4 is moved down to M5

# quality-gates-2: Run just check on every commit (last: PASS 2026-09-29-02-11-56)
Minimum Runtime: 02:56
Last Token Usage: 954.7k
[Results](workshop/results/quality-gates-2/2026-09-29-02-11-56)
[Material](workshop/material/quality-gates-2/)
[develop](develop/)

Implement the new milestone M4

```sh
just prepare quality-gates-2
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
/implement M4
```

*EXPECTED OBSERVATIONS*
- When we change the formatting of the code on purpose the pre commit hook catches it and fails the next commit attempt
<!-- director: we need to make the just file evolve gradually and not contain the scalafmt right away, that is part of the previous lesson and implementation of the milestone, so the initial just file inside the sandbox should focus on tests only until we add the scalafmt angle on refine-7 -->

*EXPLORE COMMANDS*
From `develop/` after M4 scalafmt gate exists:

```sh
# mess up formatting in a Scala file, then:
git add -A && git commit -m "format break"   # expect pre-commit / just check to fail
just fmt && git add -A && git commit -m "format fixed"   # expect success
```

# skills-1: Make the claude commands into skills (last: PASS 2026-09-29-02-17-18)
Minimum Runtime: 00:51
Last Token Usage: 212.9k
[Results](workshop/results/skills-1/2026-09-29-02-17-18)
[Material](workshop/material/skills-1/)
[develop](develop/)

Commands behave differently in Cursor than in Claude.
Claude always loads something to auto load the commands and treat it as a skill.
Therefore they occupy some upfront context on the first run.
We will turn the commands now into skills and then we will see that they auto load themselfs without you having to remember they exist.

```sh
just prepare skills-1
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
make the claude commands /refine and /implement into skills, each as .claude/skills/<name>/SKILL.md, and add a short frontmatter description to each skill including the "refine" and "implement" keywords for each accordingly
```

*EXPECTED OBSERVATIONS*
- The .claude/commands should no longer contain the refine.md and implement.md commands
- The .claude/skills directory should contain refine/SKILL.md and implement/SKILL.md
- The refine skill has a frontmatter description that includes the "refine" keyword


# skills-2: Test the skills auto loading (last: PASS 2026-09-29-02-22-07)
Minimum Runtime: 02:17
Last Token Usage: 189.8k
[Results](workshop/results/skills-2/2026-09-29-02-22-07)
[Material](workshop/material/skills-2/)
[develop](develop/)

Commands behave differently in Cursor than in Claude.
Claude always loads something to auto load the commands and treat it as a skill.
Therefore they occupy some upfront context on the first run.
We will turn the commands now into skills and then we will see that they auto load themselfs without you having to remember they exist.

```sh
just prepare skills-2
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   ├── skills/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
refine v1 to include a new milestone covering the ansi coloring, it should using colors for different status of the todos, white for not started, green for done, and yellow for in progress.
```

*EXPECTED OBSERVATIONS*
- The skill is loaded automatically just because we use the "refine" keyword mentioned in the description frontmatter of the refine skill
- The new milestone is added to the SPEC


# quality-gates-3: Have the specs being checked deterministically (last: PASS 2026-09-30-03-19-22)
Minimum Runtime: 03:56
Last Token Usage: 2148.2k
[Results](workshop/results/quality-gates-3/2026-09-30-03-19-22)
[Material](workshop/material/quality-gates-3/)
[develop](develop/)

For now the specs are structured by the mercy of the llm gods and their attention span, or our ability to not specify contradictory requirements or too large gaps. Lets add a new quality gate that checks the structure of the specs to increase familiarity across team members for greater communication. We keep using the old spec and will use the spec check with the altered skills to bring it into alignment with the new structure.

<!-- director: we take the same material from after completing skills-2 and add the scala spec check to the material for this lesson so that it becomes executable via just spec-check and have both refine and implement reference it and basically take the outer shells variation but with the changed call or we both align them to use just spec-check on the outer and the develop shell so that the skills look the same even if we may use the python variant on the just spec-check variation and the commit hook so this introduces rather a lot in a single lesson -->

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   ├── skills/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── scripts/
│   └── spec-check-scala/
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

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

*EXPLORE COMMANDS*
From `develop/`:

```sh
just spec-check
# break a SPEC heading or criteria box on purpose, re-run, then fix until:
just spec-check
```

# quality-gates-4: Quiet the app under a redundancy gate (last: PASS 2026-09-30-09-12-10)
Minimum Runtime: 01:51
Last Token Usage: 485.3k
[Results](workshop/results/quality-gates-4/2026-09-30-09-12-10)
[Material](workshop/material/quality-gates-4/)
[develop](develop/)

The app grew steep features and now carries copy/paste debt. Wire the redundancy gate, run the skill, and refactor until the quiet report is empty.

```sh
just prepare quality-gates-4
just claude
```

*WORKTREE*
```
.
├── .claude/
│   ├── commands/
│   ├── hooks/
│   ├── skills/
│   └── settings.json
├── .githooks/
│   └── pre-commit
├── .github/
│   └── workflows/
├── docs/
│   ├── rules/
│   ├── specs/
│   └── PROMPTS.md
├── project/
│   ├── build.properties
│   └── plugins.sbt
├── scripts/
│   ├── check-redundancies-cpd/
│   ├── spec-check-scala/
│   └── check-redundancies
├── src/
│   ├── main/
│   └── test/
├── .gitignore
├── .scalafmt.conf
├── build.sbt
├── CLAUDE.md
├── justfile
└── README.md
```

*PROMPT TO TEST*
```
check redundancies in the app sources and refactor until just check-redundancies --fail-on-findings is quiet
```

*EXPECTED OBSERVATIONS*
- A redundancy report exists and lists findings ordered by size × occurrences (or is empty after fixes).
- The skill proposes a concrete refactor (parameterize, abstract, push responsibility) for at least one finding.
- After fixes, the quiet baseline has zero actionable findings (allowlisted items documented).

*EXPLORE COMMANDS*
From `develop/` (or the lesson app tree):

```sh
just check-redundancies verbosity=normal
just check-redundancies --fail-on-findings
```
