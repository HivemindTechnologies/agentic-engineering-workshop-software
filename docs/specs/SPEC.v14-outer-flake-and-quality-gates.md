# SPEC.v14: Outer harness flake and deeper quality gates

The wet dress rehearsal handout already ships a prebuilt root `flake.nix` on participant machines. Changing that flake forces a rebuild and risks breaking the day. **Root `flake.nix` stays frozen.** Anything the outer harness needs beyond what that handout already provides — portable `python3`, `jq`, `yq`, and the rest of the scripts' prerequisites — moves into a second flake under `outer/`, kept slightly out of sight so participants still enter the familiar root develop shell.

Separately, the workshop will run out of material if it stops at "add a pre-commit hook and scalafmt." The next curriculum layer is an intentionally flawed, more advanced todo-list codebase and a ladder of **deterministic quality gates**: duplication, complexity, dead code, wartremover, coverage thresholds, architectural package rules, and eventually domain-modelling lessons (opaque types, smart constructors, refined types). Prefer **Scala / JVM / sbt-native** tools first. Node and `jscpd` come later as an optional ecosystem, not the foundation.

## M1a: `outer/flake.nix` holds outer-shell prerequisites (Status: PENDING)

The outer just recipes and Python scripts assume tools that are awkward to require as global host packages. A dedicated flake under `outer/` lists them without touching the root flake.

**Acceptance Criteria:**

- [ ] `outer/flake.nix` exists and provides a default `devShell` whose packages include at least: `python3`, `jq`, `yq-go` (the `yq` binary), and every other outer-shell tool this repository's harness recipes currently invoke that is not guaranteed by the frozen root flake (named in Implementation Details when implemented).
- [ ] The root `flake.nix` file bytes are unchanged by this milestone (no edit, no reformat-only commit that rewrites it).
- [ ] Entering the outer shell does not require rebuilding or substituting the root develop shell.
- [ ] The test is a search of `outer/flake.nix` for those package names, plus a check that root `flake.nix` matches a frozen fixture or git-recorded baseline for this milestone. It does not start Claude.

## M1b: Weave the outer flake into the harness (Status: PENDING)

Directors and CI need a clear way to use `outer/` without discovering Nix by accident mid-workshop.

**Acceptance Criteria:**

- [ ] A documented entry path exists for the outer shell (for example `nix develop ./outer`, a root just recipe that fails clearly if the outer shell is missing tools, and/or `.envrc` composition that can load outer without replacing the root flake's develop packages). Implementation Details name the chosen path.
- [ ] `just test`, `just status`, and the other outer recipes either run inside that outer environment or print an actionable message naming the outer flake when a required binary is missing.
- [ ] README (or the journey preamble) states that participants on handout machines keep using root `nix develop` for the sandbox, and that `outer/` is for harness authors / directors.
- [ ] Root `flake.nix` remains untouched.
- [ ] The test covers the entry path and the missing-binary message (fixture or dry run). It does not start Claude.

## M2: Root flake freeze is enforced (Status: PENDING)

Handout machines must not silently require a flake rebuild. The freeze from the preamble becomes a gate.

**Acceptance Criteria:**

- [ ] A check fails when root `flake.nix` differs from a committed baseline (for example `outer/root-flake.baseline.nix` or a hash file under `outer/`), unless a director deliberately refreshes that baseline.
- [ ] The check is runnable as a just recipe. It may join pre-commit once the baseline exists.
- [ ] Refreshing the baseline is a deliberate command, never automatic on ordinary harness edits.
- [ ] The test tampers with a fixture copy of the baseline check and asserts failure. It does not start Claude.

## M3: Advanced flawed todo material for quality-gate lessons (Status: PENDING)

Before new gates mean anything, the participant tree needs code that fails them on purpose: duplication, needless complexity, dead paths, and layering violations — with at least one clean path to fix each class of smell.

**Acceptance Criteria:**

- [ ] New workshop material (lesson deltas and/or a post-skills journey segment) lands an advanced todo-list tree that already compiles and has tests, and that deliberately contains at least three smell classes among: duplicated logic, high cyclomatic complexity, dead code, a package-layering violation, and a codec/domain-type constructed outside the agreed constructors.
- [ ] Each smell class has a short director note in the journey or material stating which gate will catch it and what a good fix looks like at the lesson level (not a full solution dump in `develop/`).
- [ ] The material does not depend on editing root `flake.nix`.
- [ ] The test asserts the material paths exist and that a named marker or fixture lists the intended smell classes. It does not start Claude.

## M4: JVM and sbt quality gates first (Status: PENDING)

New gates use Scala/Java tooling the develop shell can already host or add via project plugins — not Node.

**Acceptance Criteria:**

- [ ] The advanced segment's `just check` (or an additive recipe the journey names) runs at least three of: a cyclomatic-complexity gate, a JVM/Scala copy-paste or duplication detector, a dead-code or unused-code detector, wartremover (or equivalent), scalafmt/scalafix-style lint, and stricter scalac options. Each gate fails the build with a clear message when the flawed material from M3 is unchecked.
- [ ] Gates are deterministic: same tree, same pass/fail. No LLM judge inside the gate.
- [ ] Node / `jscpd` is not required for this milestone.
- [ ] The test runs the gates against a fixture tree (or the committed flawed material) and asserts fail-then-pass when a documented minimal fix is applied. It does not start Claude.

## M5: Architectural constraint gates (Status: PENDING)

Beyond file metrics: package A must not call package B; codecs and domain types must go through package C. Prefer rules backed by the compiler or a small internal checker over prose-only conventions.

**Acceptance Criteria:**

- [ ] At least one architectural rule is enforced automatically on the advanced tree (examples: `todo.render` must not import `todo.store`; domain types are constructed only via smart constructors / opaque wrappers in an agreed package).
- [ ] Violation fails `just check` (or the named gate recipe) with a message that names the rule and the offending path or symbol.
- [ ] The flawed M3 material includes one intentional violation that this gate catches; a documented fix makes the gate pass.
- [ ] The test covers fail and pass fixtures. It does not start Claude.

## M6: Domain-modelling journey slice (Status: PENDING)

Quality gates open the door to teaching Scala modelling: opaque types, smart constructors, and optionally refined types — fixing smells by making illegal states unrepresentable rather than by deleting lines only.

**Acceptance Criteria:**

- [ ] At least one new journey lesson (after the current skills segment, or clearly marked as an advanced track) asks the participant to replace a smell with opaque types and/or smart constructors, with expected observations that mention the compiler-enforced boundary.
- [ ] The lesson prompt and material stay inside the frozen root flake's toolchain (sbt, scalac). Refined types, if used, are optional and named as an extension, not a hard host dependency of the handout flake.
- [ ] Expected observations for that lesson are written so M5-style gates or compile failures demonstrate success without an LLM.
- [ ] The test is a search of the journey/material for the lesson id and the opaque/smart-constructor wording, plus a compile/gate fixture if one ships with the lesson. It does not start Claude.

## M7: Node and jscpd only after the JVM ladder (Status: PENDING)

Cross-language duplication detection is useful later. It must not become a prerequisite for M4–M6.

**Acceptance Criteria:**

- [ ] `outer/flake.nix` (or a clearly optional overlay) can provide Node when directors opt in, without changing root `flake.nix`.
- [ ] A jscpd (or equivalent) recipe exists behind an explicit just target, documented as optional, and is not part of the default `just check` for the advanced segment until a later decision flips that.
- [ ] The journey does not require Node for any lesson before this milestone is DONE.
- [ ] The test asserts the optional recipe is present and that default check does not invoke it. It does not start Claude.
