# todo-list-cli

Workshop harness. The participant's project is not this directory. `just prepare` builds it in `develop/`, and the sandbox can see only that directory.

## Start

```sh
nix develop           # JDK, sbt, scalafmt, just, nono, Claude Code
just                  # recipes
just prepare          # lesson names
just prepare refine-1 # empty project, then the prompt
just claude           # Claude Code inside develop/
```

`just sandbox` is the same boundary with a plain shell. The design is in `docs/specs/SPEC.v1-onion-layering.md`. The prompts are in `workshop/JOURNEY.md`.
