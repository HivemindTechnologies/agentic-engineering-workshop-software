# 💡 Observe 2

**Telemetry as Agent Input.** Debugging is reading signals and forming a hypothesis. An agent does that well if you hand it the signals.
One incident: a one-line complaint, a proven cause, a check that would have caught it.

----

## Pick the signals it reads

<img src="assets/images/turnoff-us-tail-f-without-grep.png" alt="a developer buried under an endless stream of unfiltered log output" class="comic">

<p class="credit">Daniel Stori · turnoff.us/geek/tail-no-grep · CC BY-NC-SA 4.0</p>

----

## What to hand it

- The log window around the error
- The spans for one trace id
- Structured logs beat prose; a trace beats a log

----

## Frame the incident

- Bad: "the service is broken, fix it"
- Good: "errors on scoring since 14:02, three request logs, one trace, the cluster looks healthy"
- Give it symptom, timeline, and what you ruled out

----

## Stop when it is proven

- It proposes a hypothesis, checks it against code and telemetry, revises
- You steer: "you assumed the cache is warm, check"
- It ends in a failing test, then the fix

---

## 🛠️ Observe 2

Take incident 01 from complaint to check.

1. `just incident 1`, reproduce it once by hand, capture the log window.
2. Fresh session: frame it. Symptom, timeline, log excerpt, one thing ruled out.
3. Demand a hypothesis before any code change. It verifies until the cause is proven.
4. Agent writes the failing test, then the fix. Commit both together.

**Done when**

- [ ] a written hypothesis preceded any code change
- [ ] the cause shown by a command someone else can rerun
- [ ] a check fails before the fix and passes after

**Material:** `workshops/infrastructure/incidents/01-scoring-flaky`
