# 💡 Review 2

**The Review Cascade.** Gates judge what a machine can verify, an agent pass judges what only prose can state, the human judges intent.
Each stage takes only what the previous one could not judge.

----

## What you are reviewing now

<img src="assets/images/xkcd-1513-code-quality.png" alt="code described as being written by someone who has never seen code but has heard it described" class="comic">

<p class="credit">xkcd 1513 “Code Quality” · CC BY-NC 2.5 · xkcd.com/1513</p>

----

## Three stages

| stage | judges | authority |
| --- | --- | --- |
| **CI gates** | what a machine can verify, every diff | blocks the merge |
| **An agent pass** | the same, plus what only prose can state | comments |
| **The human** | the plan, and intent | owns the merge |

----

## Agent: good at, bad at

| good at | bad at |
| --- | --- |
| missed error cases, unhandled nulls | is this the right feature? |
| tests that do not test the thing | does this fit the architecture? |
| inconsistent with nearby code | is the scope right? |
| security-sensitive patterns | taste |

----

## Diff size

- Review quality collapses past a few hundred lines
- A 1000-line PR gets rubber-stamped, by humans and agents alike
- Too big to review means too big for one change

----

## Why shape decides the effort

- 5 independent functions: **5** things to check
- 5 functions sharing one mutable store: **5 + up to 10** pairs
- Hidden inputs turn addition into multiplication

Give the change a top: one file naming the steps in domain words.

---

## 🛠️ Review 2

Review the open PR yourself, then with an agent, and compare.

1. Three minutes alone. Write your findings.
2. Give the agent the diff. Ask for issues ranked by severity, with file:line.
3. Triage its list: real, noise, already known. Note one thing each side missed.
4. Post a review: your intent comments plus the confirmed findings.

**Done when**

- [ ] both sets of findings written down
- [ ] every agent finding triaged
- [ ] one posted review combining both
