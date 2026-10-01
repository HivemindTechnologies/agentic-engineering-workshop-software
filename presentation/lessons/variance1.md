# 💡 Variance 1

**The Same Prompt Twice.** Two fresh sessions, one prompt, two different programs.

----

## Two runs, one prompt

- **Open question**: layout, naming, error handling differ; the prompt never decided them
- **Distraction**: drifts toward the noise in the window
- **Contradiction**: two rules conflict, it picks one silently
- **Hallucination**: an API that does not exist

----

## The review burden

What a human must read and believe before a change lands.

- Generating got cheap; reading did not
- Gates shrink it, guardrails do not

---

## 🛠️ Variance 1

Same prompt, two sessions.

1. Two terminals with `nix develop`.
2. `just claude` in each. Paste into both:
   > Write a Scala CLI that counts words in a file. Just the code.
3. Compare the two programs. What differs?
4. `/clear` in both. Paste the same prompt plus:
   > Interview me relentlessly about every aspect of this plan until we reach a shared understanding.
5. Give both the same answers. Compare again.
