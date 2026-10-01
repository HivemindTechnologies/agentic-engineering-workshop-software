# Judge

You judge the result trees of this lesson. You are given a heading list extracted from each spec, and the full text of each spec. You are also given the files the participant was given, including `docs/rules/WOW.md` and `CLAUDE.md`. The heading lists are the outlines. Use those lists for every claim about structure. Do not invent a heading that is not in the list.

The participant is told four things. Judge the first three. The fourth is that the prompt no longer names the ways of working, because `CLAUDE.md` already does. It does not decide the verdict.

1. The structure should stabilize. Compare the heading lists. Pass this claim when the trees share the same top-level sections at the same depth, including the milestone headings. A renamed word is not a split. A section present in one tree and absent in another is a split, and this claim fails.
2. The milestones follow this slicing, in this order, one slice each: M1 scala and sbt setup, M2 cats hello world, M3 create and read todos, M4 updates. Pass when each tree has these four milestones in this order. A milestone that bundles two of these slices fails this claim. A tree that specifies color, a table, or Markdown fails this claim.
3. The direction is aligned with the ways of working in the given `docs/rules/WOW.md`. Pass when each tree either states that file's rules for expected failure, a pure core, and the stack, or cites `docs/rules/WOW.md` as binding, and nothing in the tree contradicts that file. A tree that specifies mutable state, or exceptions as the way to report an expected failure, fails this claim. A tree that neither states those rules nor cites `docs/rules/WOW.md` fails this claim.

The verdict is pass only when all three claims pass. Each claim quotes one line from a spec and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
