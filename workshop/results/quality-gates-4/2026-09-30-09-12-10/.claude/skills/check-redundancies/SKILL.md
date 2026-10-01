---
name: check-redundancies
description: Run the copy/paste redundancy gate (PMD CPD) and surface top findings ordered by size times occurrences. Use when asked about redundancy, copy-paste, CPD, or duplicated Scala blocks.
---

# /check-redundancies

The gate is PMD's copy/paste detector (CPD, pinned in `scripts/check-redundancies-cpd/build.sbt`) run through the JDK and sbt. The first run builds it and fetches the pinned PMD jars once; later runs are offline.

1. Run `just check-redundancies` (default verbosity `quiet`, minimum 50 tokens) from the app/lesson root.
2. Read the JSON report (`snapshots/redundancy-report.json` by default): `finding_count`, then the findings.
3. Present findings ordered by **impact = lines × occurrences** (the tool already sorts this way). Show file:start for each location.
4. For each top finding, propose one concrete refactor: parameterize a function, introduce an abstraction, push code up/down the call hierarchy, or localize responsibility in the domain model.
5. Re-run after fixes with `just check-redundancies --fail-on-findings`; it exits non-zero while findings remain. Use `verbosity=verbose` to see the duplicated snippet.
6. Removing the duplication is the goal. Only when a duplicate is intentional, silence exactly that region with `// CPD-OFF` ... `// CPD-ON` around it, or exclude a path with `--allow '**/generated/**'`, and say why (M4d).
