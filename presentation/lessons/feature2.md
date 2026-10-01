# 💡 Feature 2

**Find the Case It Got Wrong.** The agent produces plausible code fast.
Finding the input that breaks it is the work. That case drives the next three blocks.

----

## The loop from Commands 2, at speed

- `/refine`, review the plan, `/implement`
- Run the check
- Read the diff as if someone else wrote it

----

## Where plausible code goes wrong

- Two fields that must not both be set
- A `String` that is really an identifier
- A case handled by returning a default
- An exception where the type said nothing could fail

----

## The question

- Which input makes this wrong?
- Write it as a failing test before arguing about the fix

---

## 🛠️ Feature 2

End the block with a failing test. The fix is the next three blocks.

1. `/refine` and `/implement` the next backlog feature.
2. Read the diff. Find one case it gets wrong.
3. Write the test that fails on it. Watch it fail.
4. One sentence: which rule would have made this case impossible?

**Done when**

- [ ] feature implemented, check green
- [ ] one failing test names a real defect
- [ ] a candidate rule, written down
