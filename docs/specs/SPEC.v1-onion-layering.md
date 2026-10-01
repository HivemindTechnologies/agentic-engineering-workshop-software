# SPEC.v1: Onion layering

The workshop is two trees. The outer repository is the harness. `develop/` is the participant's project, created on demand, and it is the only tree the sandbox can see.

## M1: The sandbox starts in develop/ (Status: ✅ DONE)

The sandbox used to start in this repository. nono grants `$WORKDIR`, so a start here granted `workshop/` and the Git history that already contains the lessons. A deny rule for `workshop/` does not remove that directory from `ls` of its parent. The sandbox therefore starts in a directory that never contained the material.

**Acceptance Criteria:**

- [x] `just sandbox` and `just claude` set the working directory to `develop/`.
- [x] `nono.json` allows `$WORKDIR` and has no deny rule. The outer `.cache/` is an extra `--allow` on those two recipes. `.sandbox_history` is an extra `--allow-file` on `just sandbox`.
- [x] From inside that sandbox, `ls ..`, `cat ../workshop/JOURNEY.md`, and `git -C .. log` fail.
- [x] `develop/` is gitignored by the outer repository. `develop/.git` has no remote. `develop/.claude-home` is wiped with `develop/` on every prepare.

## M2: Prepare rebuilds from deltas (Status: ✅ DONE)

`just prepare <lesson>` always starts over. Lessons with no files are empty deltas: only the prompt in `workshop/JOURNEY.md` changes. A later lesson includes every earlier delta.

**Acceptance Criteria:**

- [x] `just prepare` with no argument prints the lesson names, in order: `refine-1`, `refine-1a`, `refine-2`, `refine-3`, `refine-4`, `refine-5`, `refine-6`, `implement-1`.
- [x] `just prepare <lesson>` deletes `develop/`, runs `git init -b main`, copies `workshop/material/00-base/` in, commits that tree as `base`, applies each delta through the named lesson as its own commit, and prints that lesson from `workshop/JOURNEY.md`.
- [x] The file deltas are exactly: `refine-1a` copies `.claude/commands/refine.md`, `refine-4` copies `docs/rules/WOW.md`, `refine-5` copies `CLAUDE.md`, `refine-6` copies `docs/specs/SPEC.v1-todo-list-cli-mvp.md`, `implement-1` copies `.claude/commands/implement.md`. `refine-1`, `refine-2`, and `refine-3` copy nothing.
- [x] Each material directory is copied with `cp -a workshop/material/<lesson>/. develop/`. `just prepare refine-5` therefore contains base, then the refine-1a, refine-4, and refine-5 commits.

## M3: One shell, two justfiles (Status: ✅ DONE)

One flake and one `.envrc`, both outer. The inner justfile ships inside `00-base` because the participant is told to run `just check`.

**Acceptance Criteria:**

- [x] `flake.nix` is the only flake. Its dev shell provides JDK 21, sbt, scalafmt, just, nono, jq, and Claude Code.
- [x] `nix develop` is entered in the outer repository. The sandbox is a child of that shell, so `sbt` and `java` are already on `PATH`.
- [x] `.envrc` points `COURSIER_CACHE` and `SBT_OPTS` at the outer `.cache/`. Those variables stay set after `cd develop`. nono is given read-write on `.cache/` and on nothing else outside `develop/`.
- [x] `just` inside the sandbox runs the justfile from `00-base` (`build`, `test`, `fmt`, `check`) and cannot read the outer justfile.
