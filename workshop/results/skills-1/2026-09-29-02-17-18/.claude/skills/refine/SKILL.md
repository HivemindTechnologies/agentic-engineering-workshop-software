---
name: refine
description: Use this skill to refine a spec — write or change a spec, get it reviewed, and commit the docs change.
---

# refine — Refine a Spec or Milestone

Produce reviewable documentation in a spec file. The agent proposes, the user reviews, then the agent commits. Get the words right; the commit is the small part. No code is written in this skill.

## Where

Specs live in `docs/specs/SPEC.v<N>-<goal>.md`. `<goal>` is a short kebab-case statement of what the spec is for, so `ls docs/specs` alone tells the reader what each version does — `SPEC.v1-initial-setup-of-mvp.md`, not `SPEC.v1.md`. A new spec gets the next version number; a change to an existing spec edits that file.

## Format

Each milestone: heading (`## M<N>: <Title> (Status: <STATE>)`), optional description, `**Acceptance Criteria:**` (required). `**Implementation Details:**` is added by the implement skill, never here. Both labels are headless bold with the colon inside the markers.

Flat by default. A milestone is one H2 with a bare id (`M1`). Promote to a group (H2 without criteria, two or more H3 children with a postfix such as `M1a`) only when the parts are implemented and reviewed separately. A group with one child is the same milestone written twice — collapse it. Do not invent a split the user did not ask for; when borderline, write it flat and say it could be split.

Milestone ids: `M\d+([A-Za-z][A-Za-z0-9_-]*)?`. Numbering is local to the spec file. Where the spec could be ambiguous — commit messages, references across specs — use `v<N>.M<id>`.

## Status

Every heading that owns acceptance criteria ends in `(Status: <STATE>)`.  `PENDING` → `IMPLEMENTING` → `IMPLEMENTED` → `✅ DONE`. Off the path:  `PARTIALLY_DONE`, `SKIPPED`, `POSTPONED`. Only `DONE` carries the checkmark.  The refine skill writes `PENDING`; the other states belong to the implement skill.  
## Acceptance criteria

Each criterion is something a test, a command or a diff can fail. "Handles errors gracefully" is not a criterion; "an empty name is rejected and the message names the field" is. Fewer criteria that are genuinely checkable beat many that sound thorough. Phrase them so the implement skill can name the test for each one.

## Workflow

1. Read the request and any existing spec it touches.
2. Ask when the request is ambiguous. A guess written down as a criterion is worse than a question.
3. Write or edit the spec file. Nothing else changes.
4. Stop. Show the user where the file is and what to look at. The user reviews the file, not the chat.
5. After the user says the spec is right, commit it. One commit, spec files only, conventional format:

   ```
   docs(spec): v1 initial setup of mvp, build system, hello world, minimal features for MVP
   docs(spec): v1.M3 tighten the acceptance criteria
   ```

The commit is the artifact of the review. A spec that was never committed was never reviewed.
