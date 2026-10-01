# 💡 Types 2

**The Compiler Is the Reviewer It Cannot Talk Past.** You know sealed hierarchies and opaque types.
What changed is why: a convention that lives in a review comment is only a suggestion to a generator that writes faster than you read.

----

## The reviewer that never gets tired

<img src="assets/images/xkcd-1537-types.png" alt="a weakly typed language cheerfully returning nonsense for every operation" class="comic">

<p class="credit">xkcd 1537 “Types” · CC BY-NC 2.5 · xkcd.com/1537</p>

----

## Two piles

- Enforced: the build fails
- Remembered: a reviewer notices, sometimes
- Agent-written code drifts in the second pile

----

## What the generator does to a convention

- It learned from a million repos with other conventions
- `AGENTS.md` moves the odds; the compiler decides the outcome
- A promoted rule retires its review comment for good

----

## Promote one

- "ids are not names" → an opaque type
- "this state cannot happen" → a sealed hierarchy
- "validate at the edge" → a smart constructor

---

## 🛠️ Types 2

Move your rule from the remembered pile to the enforced pile.

1. Name the convention the defect broke.
2. Change the types so breaking it does not compile.
3. Delete the defensive checks that are now unreachable.
4. Ask the agent to reintroduce the old behaviour. Watch the compiler refuse.

**Done when**

- [ ] the old defect is a compile error
- [ ] at least one runtime check disappeared
- [ ] the agent failed to write the wrong version when asked
