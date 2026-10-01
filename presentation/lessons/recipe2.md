# 💡 Recipe 2

**You Already Run This Stack. The Question Is What the Agent May Drive.** You already have plan output, schema validation and drift detection.
New: they become the agent's interface, and the only record of what it did.

----

## Natural language on a real cluster

<img src="assets/images/turnoff-us-natural-language.jpeg" alt="an operator asks in plain language whether the containers are healthy and gets told his own health is deteriorating" class="comic">

<p class="credit">Daniel Stori · turnoff.us/geek/natural-language · CC BY-NC-SA 4.0</p>

----

## Plan output is the review surface

- The agent proposes a diff of declared state
- You read the plan output
- A person decides the apply, separately

----

## Gates that bound an agent

- Schema validation: rejects what the API server accepts but nobody wants
- Manifest lint: catches patterns your team agreed against
- Drift detection: finds hand edits, the agent's included

----

## Which rule earns a gate

- **Worth writing**: corrected twice in review, and a machine can decide it
- **Already covered**: `plan` or the schema rejects it anyway
- **Leave it**: it would fire on legitimate manifests, so the team disables it

----

## The runbook rule

- Every command in it ran while it was written
- The agent drafts it; running it makes it true
- A runbook nobody executed is a guess with formatting

---

## 🛠️ Recipe 2

Work the remaining exercises inside the sandbox, and decide where the human belongs.

1. Add schema validation to CI. Watch a broken manifest fail it.
2. Hand edit one resource in the cluster. Let drift detection find it.
3. Write a runbook for one recurring job, running each command as you write it. Mark in `AGENTS.md` which commands the agent may run without asking.

**Done when**

- [ ] CI rejected a manifest the API server would accept, and you saw the output
- [ ] the drift check found the hand edit
- [ ] a runbook with every command run, and the allowed ones listed

**Material:** `workshops/infrastructure/exercises/`
