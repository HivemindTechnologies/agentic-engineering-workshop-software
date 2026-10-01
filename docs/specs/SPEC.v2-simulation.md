# SPEC.v2: Simulation

A simulation is one participant turn with nobody at the keyboard. It sends that lesson's prompt to Claude inside the current `develop/`, in the same sandbox as `just claude`, then copies out the files the lesson is expected to leave behind. Preparing a tree and simulating a prompt are separate. See v1 for the sandbox.

## M1: One prompt, one stamped tree (Status: ✅ DONE)

One directory per run, named with the local time `YYYY-MM-DD-HH-MM-SS`, so later runs sort after earlier ones. The lesson is the parent directory. A run does not carry a separate lesson file.

**Acceptance Criteria:**

- [x] `just simulate <lesson>` reads the single fenced block under `*PROMPT TO TEST*` for that lesson in `workshop/JOURNEY.md`. A lesson with no such block fails before Claude starts.
- [x] The run writes `workshop/results/<lesson>/<stamp>/session.jsonl` with the stdout stream, whether or not the expected files appear.
- [x] On success the recipe copies each expected path from `develop/` into that stamp directory, preserving the relative path. `develop/` is left as the session finished.
- [x] refine-1, refine-1a, refine-2, and refine-4 expect `docs/specs/SPEC.v1-todo-list-cli-mvp.md`. A lesson with no expected paths fails before Claude starts.

## M2: Prepare is optional (Status: ✅ DONE)

`prep` defaults to true. The lesson argument chooses the prompt and the expected paths. It chooses the tree only when prep runs.

**Acceptance Criteria:**

- [x] `just simulate <lesson>` runs `just prepare <lesson>` and then sends that lesson's prompt.
- [x] `just simulate <lesson> prep=no` skips prepare and sends that same prompt. The token `prep=no` is accepted as one positional argument.
- [x] `prep=no` with no `develop/.git` fails before Claude starts.
- [x] `just prepare refine-4` followed by `just simulate refine-1 prep=no` sends the refine-1 prompt against the refine-4 tree.

## M3: A missing file fails and keeps the log (Status: ✅ DONE)

**Acceptance Criteria:**

- [x] When an expected path is absent in `develop/`, the recipe exits non-zero, prints `FAIL simulate <lesson>`, `expected:`, `received: missing`, and `why:` as the final assistant reply, and still leaves `session.jsonl` in the stamp directory.
- [x] When every expected path is present and Claude exits 0, the recipe prints `PASS simulate <lesson>` and `saved` plus the stamp path.
- [x] The prompt is one user message on stdin, then stdin is closed. The Claude flags are `-p --input-format stream-json --output-format stream-json --verbose --permission-mode bypassPermissions --permission-prompts none`.
- [x] The process is `nono run` with working directory `develop/` and `CLAUDE_CONFIG_DIR` at `develop/.claude-home`.
