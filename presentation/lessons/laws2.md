# 💡 Laws 2

**A Law Holds for Inputs Nobody Wrote Down.** An example test covers the three cases you thought of, and a generator writes code that passes exactly those three.
A property states the rule for every input. You write the law, the agent writes the implementation.

----

## The Test It Can Write Around

- An example test names its inputs, so the code can name them back
- `if (n == 3) 33 :: 33 :: 34 :: Nil` passes and is not a split
- Plausible code special-cases in subtler ways
- A property picks the input after the code is written

----

## Three Piles, Not Two

- **Compiler**: the build fails; an illegal state has no constructor
- **Law**: the build fails on an input nobody wrote; a rule over values
- **Reviewer**: someone notices, sometimes

----

## Four Shapes That Cover Most Rules

- **Round trip**: `parse(render(x)) == x`
- **Conservation**: the shares sum to the total, exactly
- **Model**: agrees with the obvious slow version
- **Metamorphic**: reorder the expenses, and the balances stay the same

```scala
property("a split gives back exactly the total") {
  forAll(genMoney, Gen.choose(1, 12)) { (total, n) =>
    assertEquals(Split.evenly(total, n).reduce(_ + _), total)
  }
}
```

----

## The Generator Is the Gate

- `Gen.choose(1, 12)` decides what the law is worth
- Narrow the generator, and a wrong implementation goes green
- A law over `Gen.const(100)` tests one input, like an example test
- Review the generator first, the assertion second

----

## What a Failure Hands You

- Shrinking reports the smallest breaking input: `total = 1, n = 3`
- One line, the same every run once the seed is pinned
- The agent can act on that alone, without you
- Pin the counterexample as an example test, then fix

---

## 🛠️ Laws 2

Take the rule the compiler could not state and give it to a generator.

1. Name the rule Types 2 could not encode. One sentence, about values, not types.
2. You write the law: one `property`, one assertion. The agent writes the generator and the implementation.
3. Run it. Read the shrunk counterexample out loud, then pin it as an example test.
4. Ask the agent to make the suite green without fixing the defect. Watch what it narrows.
5. Add the property to `just check`. Run it against the commit before Types 2.

**Done when**

- [ ] one law you wrote, over input you did not write
- [ ] a shrunk counterexample, pinned as an example test
- [ ] one sentence on how this property could be made vacuous
- [ ] the law fired on old code, and you saw the output
