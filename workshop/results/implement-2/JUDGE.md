# Judge

You judge the result trees of this lesson. Each tree is its own `## <stamp>` section, with the spec and `build.sbt` the run wrote under it — judge only that copy. A `# Given to the participant` section, if present, is the starting material the participant saw before the lesson ran, not a result; do not quote from it. The heading list of the spec is the outline.

The participant is told four things: a hello world, a basic create/read implementation, a runnable application, and tests for the new functionality. A run of the application, or of its test suite, is not part of this material — judge only what the spec itself states.

1. M2 of the spec is `(Status: IMPLEMENTED)`, and that milestone has a headless `**Implementation Details:**` line naming a Cats Effect entry point (an `IOApp`) and a greeting.
2. M3 of the spec is `(Status: IMPLEMENTED)`, and that milestone has a headless `**Implementation Details:**` line naming both the domain `Todo` model and the YAML-backed store used by `add`/`list`.

`(Status: PENDING)` or a missing `**Implementation Details:**` line fails the milestone it belongs to. A `### Implementation Details` heading fails that claim too.

The verdict is pass only when both claims pass. Each claim quotes one line from the spec and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
