# 💡 Harness 1

**The Harness.** The program around the model. It sets four things: system prompt, context, tools, model.
Everything today changes one of these four.

----

## What is actually in there

<img src="assets/images/xkcd-1838-machine-learning.png" alt="a pile of linear algebra you stir until the answers look right" class="comic">

<p class="credit">xkcd 1838 “Machine Learning” · CC BY-NC 2.5 · xkcd.com/1838</p>

----

## Anatomy

- **Model**: Haiku, Sonnet or Opus
- **System prompt**: Claude Code's own instructions, fixed per session
- **Context**: all other text the model sees: `AGENTS.md`, your messages, files it read, tool output
- **Tools**: the actions the model can call: `Read`, `Edit`, `Bash`, …

----

## Pick the model per task

| model | per million tokens, in / out | use it for |
| --- | --- | --- |
| Haiku 4.5 | $1 / $5 | renames, boilerplate, search, summaries |
| Sonnet 5.5 | $2 / $10 | everyday coding |
| Opus 5.5 | $4 / $20 | ambiguous specs, hard bugs, design |

- Cheap for mechanical work, frontier for judgement
- Review at the writer's tier or above
- `/model` switches, `/usage` shows what the session spent

---

## 🛠️ Harness 1

Check that everything is set up.

1. `nix develop`
2. `claude`. Not logged in? `/login`.
3. `/status`: model, working dir.
4. `/context`: what fills the window before you typed anything?
5. Ask it to list every tool.
6. `/model`: switch to another model.
7. Ask it things. All working well?
