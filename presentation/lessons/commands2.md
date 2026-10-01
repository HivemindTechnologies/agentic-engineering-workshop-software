# 💡 Commands 2

**Spec-Driven Development, Hands-On.** Part 1 showed the loop in theory (Spec 1). Now it runs on a real request, and you are the gate.

----

## Recap

- A plan in a file: goal, constraints, checkable criteria
- One criterion, one test
- `/refine` → **you review** → `/implement` → **you confirm**

---

## 🛠️ Commands 2

A one-liner lands in chat: *"we should let people export their data"*.

1. `/refine` it into one plan with 3 to 5 checkable criteria.
2. Reject something in your own plan: vague criterion, missing constraint, wrong scope.
3. Fresh session, plan file only: ask for the two weakest criteria. Triage both, apply what survives.
4. `/implement`: a failing test per criterion, then code.

**Done when**

- [ ] one plan changed before any code ran
- [ ] one test per criterion, suite green
- [ ] every criterion checked against the actual result
