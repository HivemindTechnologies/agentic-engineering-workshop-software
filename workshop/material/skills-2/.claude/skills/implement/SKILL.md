---
name: implement
description: Use to implement a milestone — build one milestone against its committed spec, commit it, then commit the human's review separately. Trigger on "implement", "implement the milestone", or requests to build code from a spec's acceptance criteria.
---

# implement — Implement a Milestone

Work from a committed spec in `docs/specs/`. Without one, run `refine` first.

## Workflow

1. **Select.** Name the milestone (`v1.M3`). Read all of its acceptance criteria before touching anything.
2. **Start.** Set the heading to `(Status: IMPLEMENTING)`, so a killed session leaves a record rather than silence.
3. **Map criteria to tests.** One criterion, one test. Name the test after the behaviour so the suite reads as the spec. Prefer unit tests; where a criterion needs the filesystem or a process, use a fixture, never a live network.
4. **Watch each test fail.** A test that has never been red proves nothing. Then write the code until it passes, and nothing beyond it. 5. **Verify.** Run `just check`: format, compile with `-Werror`, the full suite. Every criterion has a passing test or a command whose output you can paste.
6. **Document.** Set `(Status: IMPLEMENTED)` and add a headless `**Implementation Details:**` subsection under the milestone — no `###`, no `M<N>:` — with decisions, deviations from the spec, and anything the reviewer should look at first.
7. **Commit the work.** See Commits.
8. **Ask.** Report what you ran and what it printed, then ask the user to confirm the milestone. Do not mark it done.
9. **Commit the review.** Only after the user says "done", "complete" or an equally explicit confirmation: set `(Status: ✅ DONE)` and commit that
   change on its own.

## Commits

At least two commits per milestone, in conventional format.

- **Implementation, one or more.** Tests and code together, green under `just check`. Split into several commits when a piece can land green on its own; never split so that a commit does not build.

  ```
  feat(v1.M3): create and read todos
  test(v1.M3): store round-trip property
  ```

  The spec edits from steps 2 and 6 travel with the implementation commit, as does `docs/PROMPTS.md` if the hook appended to it.

- **Review, exactly one, separate.** Nothing but the status change to
  `✅ DONE`. It records that a human looked.

  ```
  docs(spec): v1.M3 reviewed
  ```

  Never fold the review into an implementation commit, and never make it before the user has confirmed.

## Rules

- Never mark a milestone done without explicit confirmation. Passing tests are your claim; the human's word is the verdict.
- If a criterion turns out wrong or impossible, stop and say so. Amend the spec through `refine` rather than building something else quietly.
- Anything the spec does not ask for does not get built.
- When an approach fails, revert to a clean base and start the next one. Do not patch over the wreckage.
