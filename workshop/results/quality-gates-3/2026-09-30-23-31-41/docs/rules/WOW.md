# Ways of Working (WOW)

Conventions for this codebase.

## Core principles

- **Pure FP** — no mutable `var`; state changes through pure functions, effects in `IO` at the edge.
- **Fail fast** — no swallowed errors, no continuing after invalid state; guard clauses and assertions for nontrivial assumptions.
- **Make illegal states unrepresentable** — opaque types, enums and smart constructors in Scala 3.
- **Outcomes in the return type** — `Option` and `Either` for expected failure; exceptions are defects.
- **A pure core** — the domain takes values and returns values; I/O, clock and randomness stay at the boundary.

## Stack

- **Scala 3.3.4** on **sbt**. Pin that version in `build.sbt`; do not probe Maven for a newer Scala.
- **Cats** `cats-core` **2.12.0** and **Cats Effect** `cats-effect` **3.5.7**.
- **munit** **1.0.3** for tests, with `munit-cats-effect` **2.0.0** for `IO` and `munit-scalacheck` **1.0.0** for properties.
- **YAML** via `org.virtuslab::scala-yaml` **0.3.0**. No other YAML library.
- Do not `curl` Maven metadata or search.maven.org to discover versions — use the pins above.

## Quality

- **TDD** — failing test first, watched failing, then made to pass.
- **BDD** — test names state the observable behaviour, so the suite reads as the spec.
- **One behaviour per test** — a failure names the rule that broke.
- **No mocks** — pass a function where a test needs a collaborator.
- **Diagrams** — Mermaid, not ASCII art.

## Code style

- Top-down file layout: high-level logic at the top, helpers at the bottom.
- Constants at the top of the file instead of magic numbers.
- Push conditionals out to the caller where it keeps the happy path flat.
- Remove the old code when replacing an implementation.
- One small commit per step.

## Checks

```sh
sbt compile      # the first reviewer
sbt test
sbt scalafmtAll
```

The compiler is the first quality gate; the tests cover what types cannot state. Both give the same verdict for the same source, every run.
