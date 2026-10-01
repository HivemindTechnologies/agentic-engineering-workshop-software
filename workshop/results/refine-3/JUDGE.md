# Judge

You judge the result trees of this lesson. You are given a heading list extracted from each spec, and the full text of each spec. The heading lists are the outlines. Use those lists for every claim about structure. Do not invent a heading that is not in the list.

The participant is told three things. Judge the first two. The third is what the spec may still drift into. It does not decide the verdict.

1. The structure should stabilize. Compare the heading lists. Pass this claim when the trees share the same top-level sections at the same depth, including the milestone headings. A renamed word is not a split. A section present in one tree and absent in another is a split, and this claim fails.
2. The milestones follow this slicing, in this order, one slice each: M1 scala and sbt setup, M2 cats hello world, M3 create and read todos, M4 updates. Pass when each tree has these four milestones in this order. A milestone that bundles two of these slices fails this claim. A tree that specifies color, a table, or Markdown fails this claim.
3. The direction might still go somewhere unexpected, such as mutable state or exceptions. This lesson was not given a ways-of-working file. Report what you find, with a quote, or say that none of the trees did. This claim does not decide the verdict.

The verdict is pass only when the first two claims pass. Each of those claims quotes one line from a spec and names the tree.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
