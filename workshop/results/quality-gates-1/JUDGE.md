# Judge

You judge the result trees of this lesson. This lesson does not change the spec, so each tree gives you its final reply instead: the participant's own account of what it did.

The participant is told one thing: a pre commit hook that runs `just check` on every commit. Judge whether the final reply supports that.

1. The reply names a hook file it added (a script that runs `just check`, or an equivalent scalafmt/compile/test sequence) and states that this repository's git config now runs it on commit — not only that the file was written, but that it was wired up locally (e.g. `core.hooksPath` set, or the hook installed some other way it names).

A reply that only describes a script without saying it was activated in this repository fails the claim. A reply that says the hook could not be verified, or that skips saying it now runs on commit, fails the claim.

The verdict is pass only when that claim passes for every tree. The claim quotes the relevant part of each tree's final reply and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
