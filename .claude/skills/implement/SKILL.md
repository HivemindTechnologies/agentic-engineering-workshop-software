---
name: implement
description: Implement one milestone from a spec in docs/specs. Map each acceptance criterion to a test, then run scripts/spec-check. Mark the milestone done only after the user confirms.
---

# /implement — Implement Milestone

Follow the spec-driven development workflow.

## Workflow

1. **Select Milestone**: Identify which milestone (e.g. `v4.M1a`) to implement from the active spec file
2. **Review Acceptance Criteria**: Read all acceptance criteria for the milestone carefully. Run `scripts/tocmd --lines` on the active spec to locate the milestone heading.
3. **Map AC → tests**: Add unit tests (preferred) and/or fixture-based integration tests that document each AC (no live network in CI)
4. **Implement**: Write code following TDD principles and project rules
5. **Verify Acceptance Criteria**:
   - Check each acceptance criterion via those tests and/or automated scripts
   - Run the relevant test suites
   - Ensure all criteria are met
   - Set a criterion's box to `- [x]` only after that criterion's test passes, and leave `- [ ]` otherwise.
6. **Document Implementation Details**: Add a headingless **Implementation Details:** subsection without '###' nor 'M<N>:' documenting any differences from the original spec, architectural decisions, or notable implementation choices. Headless subsections stay in this order: criteria, then details, each label alone on its line, details never before criteria.
7. **Show how to try it**: Before asking the user to mark the milestone done, end the reply with one block per milestone just implemented. Name the milestone as `v<N>.M<id>`. List at most five shell commands that show the new behavior. Do not pad the list to five. Name the spec path and the test or script path to open next. Do not mark the milestone done.
8. **User Confirmation**: Only when the user explicitly confirms the milestone is complete, mark it as done
9. **Mark as Done**: Update the leaf heading to `(Status: ✅ DONE)` — **ONLY after user explicitly confirms completion**

## Important Rules

- **Never mark a milestone as done without explicit user confirmation**
- The user must say "done", "complete", "milestone is done", or similar explicit confirmation
- Do not assume completion based on code implementation alone
- All acceptance criteria must be verified before requesting user confirmation
- Use TDD: write tests first, then implement
- Follow all project rules (pure FP, DDD, typeclasses, etc.)
- Create commits regularly using conventional commit format
- Run `scripts/spec-check` on the spec file after editing it

## Example

After implementing M1 and verifying all acceptance criteria, ask:
"All acceptance criteria for M1 have been verified. Please confirm if M1 is complete, and I will mark it as done in the spec file."

Only after the user confirms should you update:

```markdown
### M1a: First route (Status: ✅ DONE)
```
