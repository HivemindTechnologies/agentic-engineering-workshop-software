---
name: deterministic-gates
description: >-
  Peel non-determinism by composing deterministic quality gates from the
  recipe catalog. Use when designing evals, CI checks, skill acceptance,
  reducing judge flake, freezing invariants, or moving probabilistic judgment
  into code and fixtures.
---

# /deterministic-gates — Peel until it is a check

We do not eliminate non-determinism. We peel it until enough of it is a check.
Hard problems stay hard. Slice them so subproblems become inspectable.

**Goal:** deterministic surface goes up; probabilistic remainder goes down.

## Resources (required)

Read before inventing anything. Do not invent catalog fields.

| File | Role |
|------|------|
| [catalog.yaml](catalog.yaml) | Recipe registry (`entries[]`) |
| [catalog.schema.yaml](catalog.schema.yaml) | Exact keys every entry uses |

Pedagogy in the catalog: **look → dig → peel → freeze → repeat.**

## When to use

- A quality claim is still a vibe, a prompt hope, or an LLM judge with no floor
- CI / skill evals flake and the flake has no name yet
- The user asks for gates, evals, invariants, fixtures, or to “make it deterministic”
- A stack is too judge-heavy and needs cheaper layers first

## Workflow

Copy and track:

```
Peel progress:
- [ ] 1. Name the control plane
- [ ] 2. Inventory what is already a check
- [ ] 3. Pick 2–4 recipes from the catalog
- [ ] 4. Order the stack (cheap / invariant first)
- [ ] 5. State first probe + harvest + uninstall
- [ ] 6. Propose concrete artifacts (script, schema, fixture, baseline)
```

### 1. Name the control plane

Write one sentence that still means pass/fail after ten different model runs.
If you cannot, start with recipe `stable-control-plane` before any sensor.

### 2. Inventory

List what already fails in code (schema, lint, tests, grep, fixtures) vs what
still needs a human or judge. Prefer moving items from the second list to the first.

### 3. Select recipes

Open [catalog.yaml](catalog.yaml). Match the problem to `category` and `aliases`.
Respect `not_the_same_as`. Prefer:

1. framing / structure / code-quality / consistency (freeze)
2. similarity (discover, then freeze fixtures)
3. ensembles (temporary sensors only)

Default stack shape: recipe `compose-two-to-four`.
Usual peel: invariants and metrics over judges; similarity + known corpus to
harvest fixtures; quorum only while a criterion is flaky; uninstall quorum when
the flake has a name in code.

### 4. Order the stack

Cheap and deterministic first. Example order:

1. `schema-boundary` / `linters-local-rules` / project tests
2. noisy sensor (`noisy-signal-gate`, `extract-then-compare`, weak judge)
3. harvest → `known-ambiguity-corpus` / `pattern-lock` / ratchet
4. drop the sensor when the freeze covers the pain (`quorum-then-uninstall`)

Never put `llm-as-judge` before a parse/schema floor.

### 5. Probe, harvest, uninstall

For each chosen recipe, fill from the catalog fields:

| Field | Use as |
|-------|--------|
| `typical_first_use` | What to do this session |
| `harvest_after_repeats` | What to freeze after 2–3 noisy passes |
| `uninstall_when` | Stop rule for that layer |
| `what_it_freezes` / `what_stays_stochastic` | Honest split for the user |

### 6. Deliverables

Stop with a short plan the user can approve. For each layer:

- **recipe id** (from the catalog)
- **artifact** to add or change (path if known: script, schema, fixture, baseline)
- **what it freezes**
- **what stays stochastic**
- **uninstall when**

Do not implement gates until the user asks. Prefer one invariant + one sensor
over a dashboard of judges.

## Anti-patterns

- Prompt instructions presented as a control plane
- Judge-first with no schema/lint/test floor
- Standing quorum/panel in CI with no harvest plan
- Raw cosine / similarity as a pass/fail verdict
- More than four active layers without an uninstall note
- Inventing catalog keys or recipes not in [catalog.yaml](catalog.yaml)

## Example (shape only)

Problem: skill output is “JSON-ish” and a judge scores helpfulness on parse failures.

Stack:

1. `schema-boundary` — validate; retry once; else fail (skip judge)
2. `invariant-first` — required keys present
3. leftover judge only on on-topic content (`llm-as-judge`), uninstall when fixtures cover the flips

Remainder: semantics on already-valid payloads.
