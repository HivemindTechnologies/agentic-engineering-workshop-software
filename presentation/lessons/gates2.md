# 💡 Gates 2

**Each Gate Buys Back a Piece of Review.** You have CI.
Today's question: what do you check by reading that a machine could check, so review keeps up with more diffs?

----

## Name what you read for

- Style and naming
- Layering and dependency direction
- Coverage of the new path
- Intent: is this the right problem?

----

## Pick one and mechanise it

- A custom lint ban for this codebase
- A dependency rule for the layering
- A coverage floor that only moves up
- No clock in the core, so the suite stays deterministic

----

## Then hand over the next feature

- Same loop, same model, gate now active
- Compare with the Feature 2 diff
- What the gate catches, you stop reading for

---

## 🛠️ Gates 2

Replace one thing you read for with one thing the build checks.

1. Name a review comment you have written more than twice.
2. Implement it as a gate: lint rule, dependency rule, or coverage floor.
3. Run it against the commit before Types 2. Keep the red output.
4. `/refine` and `/implement` the next feature with the gate active. Compare diffs.

**Done when**

- [ ] the gate rejected real code, and you saw the output
- [ ] it runs in CI
- [ ] the review comment it retires, in one sentence
