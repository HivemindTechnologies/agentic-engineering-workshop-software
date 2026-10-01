# Judge

You judge the result trees of this lesson. You are given a heading list extracted from each spec, and the full text of each spec. The heading lists are the outlines. Use those lists for every claim about structure. Do not invent a heading that is not in the list.

The participant is told three things. Judge them in this order.

1. The structure should stabilize and not vary that much anymore. Compare the heading lists. Pass this claim when the trees share the same top-level sections at the same depth, including the milestone headings. A renamed word is not a split. A section present in one tree and absent in another is a split, and this claim fails.
2. The spec stays inside the paragraph. Pass when every tree has the commands add, list, done, and remove, the store file todos.yaml, and just check, and no tree specifies color, a table, or Markdown.
3. The direction might still go somewhere unexpected, such as mutable state or exceptions. Report what you find, with a quote, or say that none of the trees did. This claim does not decide the verdict.

The verdict is pass only when claim 1 and claim 2 both pass. Each claim quotes one line from a spec and names the tree, except a report that no tree took an unexpected direction.

End your answer with one line, alone, either:

```
verdict: pass
```

or:

```
verdict: fail
```
