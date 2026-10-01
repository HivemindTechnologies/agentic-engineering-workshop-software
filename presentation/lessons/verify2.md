# 💡 Verify 2

**The First Quality Gate.** With a test suite the agent closes its own loop: run, read the failure, fix, re-run.
Today one rule moves to rung six of the Context 1 ladder, and the agent writes the check.

----

## Why gates beat diligence

<img src="assets/images/quality-gates.svg" alt="generated code, quality gates, human review" class="drawing">

----

## Watch it fail

1. One acceptance criterion, one test
2. Run it, confirm it fails for the right reason
3. Then implement
4. A test that passes before the code exists tests nothing

----

## The undo you will need

- Every agent change is one `git revert` away, or it was not one change
- Revert the fix, keep the check: it goes red on purpose
- Restore the fix: it goes green
- One branch per plan keeps the undo a single command

----

## A false positive costs more than a missing rule

- A gate that is often wrong gets switched off
- A gate that never fires is decoration
- Run it against old code before trusting it

---

## 🛠️ Verify 2

TODO
