# 💡 Spec 1

**Spec-Driven Development.** A vague request becomes a spec with checkable acceptance criteria; a human reviews it, then the agent implements it.
Reviewing a spec costs minutes. Reviewing code from a wrong spec costs a day.

----

## The changeflow flips

<img src="assets/images/new-world.svg" alt="old world: requirements, then code, then documentation, one human at each step; new world: requirements, then documentation, then code, with a human and agents at each step and three agents at the code" class="drawing">

----

## Two commands

| command | writes | stops for |
| --- | --- | --- |
| `/refine` | a spec: milestones, each with acceptance criteria | **you review the spec** |
| `/implement` | a failing test per criterion, then the code | **you confirm it is done** |

One spec per version: `docs/specs/SPEC.v<N>-<goal>.md`, committed.

----

## Who writes the spec

<img src="assets/images/pos.svg" alt="the AI helps a product owner with domain expertise and an engineer with technology expertise to create a new spec or refine the old one" class="drawing">
