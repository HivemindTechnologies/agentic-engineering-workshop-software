# 💡 Drill 2

**Two Runs, One Difference. Then the Rollback.** The same incident twice, with and without the domain skill.
Then revert the fix and watch your check go red.

----

## The A/B

- Same incident, same prompt, same model
- `just claude` twice, the skill copied in between
- One skill file is the whole difference

----

## What to compare

- Which signal it looked at first
- How many wrong turns before the cause
- Whether the run ended in a check

----

## Then the rollback

- Remove the fix, keep the check
- The check goes red, on purpose
- Restore it, and it goes green

---

## 🛠️ Drill 2

Run the comparison, then walk the rollback.

1. `just incident 2`, then `just claude`. Note where it went.
2. `cp -r ../../my-plugin/skills/diagnosing-from-telemetry .claude-home/skills/`, then `just claude`, same prompt, fresh session.
3. Write down the one difference that mattered.
4. Revert the fix, watch your check fail, restore it, watch it pass.

**Done when**

- [ ] both runs recorded, the difference named
- [ ] the check failed on the reverted state
- [ ] the agent restored it, you reviewed the restore as a diff

**Material:** `workshops/infrastructure/incidents/02-scoring-slow-on-large-events`, `drills/rollback.md`
