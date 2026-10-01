# 💡 Plugin 1

**Local to Team.** A skill or command that lives on one laptop helps one person.
Package it for one-step install, carry it to Cursor, and maintain it.

----

## What one install brings

<img src="assets/images/turnoff-us-npm-install.png" alt="one npm install turns into a wave labelled dependencies that sweeps the developer off the planet" class="comic">

<p class="credit">Daniel Stori · turnoff.us/geek/npm-install · CC BY-NC-SA 4.0</p>

----

## Our own plugin: `my-plugin`

```text
my-plugin/
  .claude-plugin/plugin.json   name, version, description, author
  skills/<name>/SKILL.md       every skill in the repository
  commands/refine.md           /my-plugin:refine
  commands/implement.md        /my-plugin:implement
```

- Use it now: `claude --plugin-dir ./my-plugin`
- Check it: `claude plugin validate ./my-plugin`

----

## `plugin.json`

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "author": { "name": "Hivemind Technologies" }
}
```

- `name`: the prefix, as in `/my-plugin:refine`
- `version`: installs update only when it changes
- `author`: one named owner

----

## What can be inside

| Path | Adds |
| --- | --- |
| `skills/<name>/SKILL.md` | skills, loaded by their description |
| `commands/<name>.md` | slash commands a human starts |
| `agents/<name>.md` | subagents |
| `hooks/hooks.json` | commands run on events, e.g. after every edit |
| `.mcp.json` | MCP servers |
| `bin/` | executables on the agent's `PATH` |

----

## A git repo is a marketplace

1. Add `.claude-plugin/marketplace.json` at the repo root

```json
{
  "name": "agentic-engineering-workshop-software",
  "owner": { "name": "Hivemind Technologies" },
  "plugins": [{ "name": "my-plugin", "source": "./my-plugin" }]
}
```

2. `claude plugin validate .`
3. `git push`
4. Install it

```text
/plugin marketplace add HivemindTechnologies/agentic-engineering-workshop-software
/plugin install my-plugin@agentic-engineering-workshop-software
```

----

## The same files in Cursor

- `AGENTS.md` moves unchanged
- Cursor loads skills from `.claude/skills/` too, matched by the same description
- `disable-model-invocation: true` makes a skill a command in both tools
- A plugin needs a second manifest: `.cursor-plugin/plugin.json`

----

## Extract or duplicate

A library breaks **loudly**: the compiler goes red.<br>
A plugin breaks **silently**: reworded prose, nothing goes red.

- Extract when call sites share knowledge, not when they look alike
- Three similar skills beat one wrong abstraction
- Still learning what works? Keep it local: edit, rerun, no release
- Knobs multiply: forty variables make a worse interface

----

## What sharing costs, in files

| | what it is | size |
| --- | --- | --- |
| `my-plugin/commands/` | `/refine` and `/implement` | 2 files, 52 lines |
| `xp-clean-code` | Hivemind's own: XP and clean-code rules | 3 plugins, 6 `SKILL.md`, 2133 lines |
| `obra/superpowers-marketplace` | a public marketplace of agent skills | 4 plugins, the core one alone 20+ skills |

----

## Installing a public plugin

<div class="plugin-row">

<img src="assets/images/superpowers-logo.svg" alt="Superpowers logo" class="plugin-logo">

<div>

**`obra/superpowers`**<br>
*An agentic skills framework & software development methodology that works.*

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

</div>
</div>

<div class="plugin-row">

<img src="assets/images/face_smile.svg" alt="Hivemind logo" class="plugin-logo">

<div>

**`HivemindTechnologies/xp-clean-code`**<br>
*Plugins that bring Extreme Programming and Clean Code discipline to AI-assisted development.*

```text
/plugin marketplace add HivemindTechnologies/xp-clean-code
/plugin install xp-clean-code@xp-clean-code
```

</div>
</div>

----

## A plugin is a supply chain

Hooks, `bin/` and `` !`command` `` lines in a skill run as you.<br>
A hook or a `` !`command` `` runs before the model can object.

- **s1ngularity**, Aug 2025: poisoned `nx` npm releases stole tokens and drove the installed `claude`, `gemini` and `q` CLIs to hunt for secrets; over 2,000 verified secrets leaked
- **Clawsights**, 2026: a skill that sends `gh auth token` to its server. Claude refused it; rewritten as `` !`command` `` lines, it ran before Claude saw it

**That is why the agent runs in the sandbox.** Whatever a plugin starts inherits the box: no `~/.ssh`, and with the strict profile no host outside the allowlist.

---

## 🛠️ Plugin 1

A skill is worth what the next person can install.

1. Package what you built as `my-plugin/`, with a manifest: a skill, a command, an agent, a hook.
2. Validate it, load it with `--plugin-dir`, let a task use it.
3. Write owner, version and deprecation path into its `README.md`.

---

## Take the sandbox home

```sh
# ~/.bashrc or ~/.zshrc
alias claude='nono run --profile nolabs-ai/claude -- claude'
```

- From tonight, every `claude` you start runs in nono's Claude profile
- And tomorrow, write or extend your own nono profile
