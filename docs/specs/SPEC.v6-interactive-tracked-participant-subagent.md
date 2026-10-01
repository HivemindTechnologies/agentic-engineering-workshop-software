# SPEC.v6: Participant metrics

The participant is the agent in the sandbox. Verifying a journey item is one sequence: prepare, simulate, judge, print one line. The agent definition comes after that sequence exists. The line says whether the item worked, and it always shows the interactions and the length of that run. Those two numbers are the quality record. The harness does not turn them into a pass or a fail. A lesson's `JUDGE.md` may. The instructor is v7 and is not part of this spec.

`verdict: pass` means the journey item worked. `verdict: fail` means it did not. The prose around that line is free. A high interaction count or a long trace is not, by itself, a failed verdict.

A comparison needs more than one tree. That need is not a property of the lesson. `forks` says how many trees this command should produce, and omitting it produces one. `depth` says how many requests each of those trees may contain. The two counts are independent. The forks run one after another. Overlap in time is not part of this behavior. M8, which would have run them together, is postponed.

## M1: Verify one lesson, or every lesson (Status: ✅ DONE)

`just prepare`, `just simulate`, and `just judge` stay single-lesson commands. `just validate` is the sequence. The participant is the same boundary as v1.M1.

**Acceptance Criteria:**

- [x] `just validate <lesson>` writes a new cutoff for that lesson, prepares it, runs the participant once, judges the trees at or after that cutoff, and prints one status line. One tree is enough to judge. The two-tree minimum in v3.M2 does not apply to this command.
- [x] `just validate` with no lesson does that for every lesson in journey order and prints a line after each lesson. A lesson that did not work does not stop the rest. The command exits non-zero after the last line when any lesson did not work.
- [x] The participant's working directory is `develop/`. From inside the run, `workshop/` and the outer Git history are not readable. The run is given that lesson's fenced block under `*PROMPT TO TEST*`. Tool uses are in `session.jsonl`.
- [x] With no `max`, the participant receives one prompt and stdin closes, as in v2.M3. `max=<n>` is the cap defined in M5.
- [x] A lesson with no expected paths prints `not run` and does not start Claude. `just validate refine-1a` does not prepare or simulate `refine-1`.

**Implementation Details:**

- A lesson with no expected path is not prepared. `just validate refine-3` prints `not run` and does not start Claude.
- After prepare, simulate is `prep=no`, so the named lesson is prepared once. A named lesson does not prepare any other lesson.
- `just judge <lesson> min=1` is the one-tree judge. `just judge` with no `min` still requires two trees.
- `depth=` is passed through to `just simulate` and is the cap from M5. `max=` is rejected. `runs=` is no longer a parameter.

## M2: Interactions and length come from the trace (Status: ✅ DONE)

Both numbers are read from a stamp directory that already exists. Nothing in this milestone starts Claude.

**Acceptance Criteria:**

- [x] `interactions` is the `num_turns` field of the last `type=result` event in `session.jsonl`. When `num_turns` is absent, it is the count of `type=assistant` events.
- [x] `length` is the sum of `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens` on that result event. When that usage object is absent, the value is `absent`. It is never stored as zero in place of a missing object.
- [x] A run that stopped because `max` was reached before the expected paths existed records `capped=yes`. Any other run omits `capped`.
- [x] The same session log produces the same three values on a second read.
- [x] A fixture log with a known `num_turns` and usage object yields those numbers, and a fixture with no usage object yields `length=absent`.

**Implementation Details:**

- `scripts/lesson-status measures` prints the three values. `capped=yes` is a JSON line `{"type":"capped"}` in that log. `scripts/participant-session` writes that line when `max` is reached before the expected paths exist.
- The status line uses the newest in-range `session.jsonl`.

## M3: The status line shows the verdict and the measures (Status: ✅ DONE)

One line per lesson. The verdict is whether the item worked. The measures are printed on that same line even when the judge ignored them.

**Acceptance Criteria:**

- [x] The line is the lesson name, then the verdict word, then `interactions=` and `length=`. A capped run adds `capped=yes` at the end. Example shape: `refine-1 PASS interactions=4 length=12043`.
- [x] The verdict word is `PASS` when the newest in-range judgement contains a line `verdict: pass`, `FAIL judge` when the judgement is missing that line or contains `verdict: fail`, `FAIL simulate` when an expected path is missing, and `not run` when the lesson was not started.
- [x] When a trace exists, `interactions` and `length` are present on a `FAIL` line and on a `not run` line that still has a stamp. They are omitted only when the lesson has no `session.jsonl` at or after the cutoff.
- [x] The prompt given to the judge includes, per tree, that tree's `interactions` and `length`. A `JUDGE.md` that never mentions them still produces a line that shows them.
- [x] `just summary` prints these lines from the trees on disk and does not start Claude. `just validate` prints the same shape of line for each lesson it ran.

**Implementation Details:**

- `just summary` and the line after each validated lesson call `scripts/lesson-status lines`.
- The judge prompt contains `measures: interactions=… length=…` for each tree that has a session log.
- A lesson with no expected path stays `not run` even when a stamp exists, and the measures are still printed.

## M4: The participant agent is defined in .claude/agents (Status: ✅ DONE)

M1 through M3 prepare, measure, and judge from the outside. This milestone names the agent that does the work inside the sandbox. The judge stays outside. The agent does not replace it.

The result trees, the cutoff, and the judgement are gathered in the outer repository. The agent cannot read them. Some expected observations are about those outer facts. The agent is not given those to check. It is given the lesson text, it runs the initial prompt, and it follows the recommendations in that text until the work inside `develop/` is finished.

**Acceptance Criteria:**

- [x] `.claude/agents/participant.md` exists in the harness. Its frontmatter sets `name: participant` and a `description`. The body is the system prompt.
- [x] The body tells the agent to execute the lesson prompt it is given, to follow the recommendations in that same text, and to finish that work in the working directory.
- [x] The body does not tell the agent to open `workshop/`, `workshop/results/`, a judgement, or the outer Git history, and it does not tell the agent to write `verdict: pass` or `verdict: fail`.
- [x] Before Claude starts, the harness copies that file to `develop/.claude/agents/participant.md`. The sandbox cannot read the outer `.claude/`. The session runs as `participant` with working directory `develop/`.
- [x] The message is the lesson section that was passed in: the prompt and the expected observations written in that section. It is not a path under `workshop/`.
- [x] `permissionMode` is `bypassPermissions`. A scripted run has no approval surface, so `acceptEdits` denies `sbt` and `git`. nono remains the sandbox. The agent file does not set its own `maxTurns`. The cap is the harness `max` in M5.

**Implementation Details:**

- `.claude/agents/participant.md` is the agent. `scripts/participant-session install` copies it to `develop/.claude/agents/participant.md` before Claude starts. `just simulate` starts `claude --agent participant` with working directory `develop/`.
- The message is the whole lesson section, from its `##` heading through the next `##`. That includes the prompt and the expected observations. M1 sent only the fenced block under `*PROMPT TO TEST*`. This milestone replaces that message. The message is the section text, not a path under `workshop/`.

## M5: One session can hold more than one request (Status: ✅ DONE)

v2.M3 records one user message and then closes stdin. The stdout stream of that one shot is `session.jsonl`. A later request needs another process. The participant in M4 cannot finish a lesson that takes a follow-up, and M2 cannot count those follow-ups, until the same process stays open and the same file keeps the whole exchange.

**Acceptance Criteria:**

- [x] A run with no `max` is unchanged from v2.M3: one user message, stdin closed, one `session.jsonl`.
- [x] A run with `max=<n>` keeps that process open. Each further prompt is another user message on the same stdin. Stdin closes after the expected paths exist, or after n user messages have been sent, whichever comes first. The next message is not sent.
- [x] Every event of that process is appended to the one `session.jsonl` for the stamp. A second process is not started for a follow-up inside the same run.
- [x] M2 reads that file. A session that sent three user messages reports `interactions` from that log, not from a single-message log.
- [x] `just validate <lesson>` is still one session per lesson. The messages inside it are the requests from this milestone.

**Implementation Details:**

- `scripts/participant-session run` owns the loop and writes the one `session.jsonl`. A fake process stands in for Claude in the tests, so the loop is checked without a live session.
- With no `max`, the script writes one user message and closes stdin. With `max=<n>`, it waits for a `type=result` event, then sends another user message on the same stdin until the expected paths exist or n messages have been sent. The follow-up text is "The expected files are still missing. Finish the prompt in this directory."
- When the cap is reached first, the script appends `{"type": "capped"}` to that same log. `just validate` passes `depth=` through to `just simulate`. M6 renamed the flag from `max`.

## M6: Fork depth and fork count are separate parameters (Status: ✅ DONE)

M1 and M5 call the session cap `max`. That name is the depth of one fork: how many user messages that one process may receive. A second count is how many such forks to run. A lesson does not store either count. One fork is enough for a lesson whose single tree decides the verdict. More than one fork is how a caller asks for trees that can be compared. The forks run one after another. That serial loop stays, because M8 is postponed.

**Acceptance Criteria:**

- [x] `depth=<n>` is the cap M5 called `max=<n>`. `just simulate <lesson> depth=2` allows two user messages in that one session. With no `depth`, the session is one user message and then stdin closes.
- [x] `max=<n>` exits non-zero before Claude starts and tells the caller to use `depth=`.
- [x] `forks` is a parameter of `just validate`, not of `just simulate`. Omitting it, and `forks=1`, run one fork in `develop/`. `just simulate` rejects `forks=`.
- [x] `just validate <lesson> forks=2 depth=3` runs two forks, the second starting only after the first has finished. Each fork has its own stamp directory and its own `session.jsonl`. Each fork allows at most 3 user messages. The second fork starts from the prepared tree, so a file written by the first fork is not already present.
- [x] The journey does not record a fork count for a lesson. The same lesson with no `forks` still produces one tree.
- [x] When `forks` is greater than 1, the judge in that validate requires that many in-range trees. `forks=1` keeps the one-tree judge from M1.
- [x] The status line stays the M3 line. Its `interactions` and `length` are still taken from the newest in-range session. The other forks are trees the judge receives, not extra numbers on the line.
- [x] Two forks that resolve to the same stamp directory fail before the second fork writes. The first fork's tree is left in place.

**Implementation Details:**

- `depth=` is the session cap. `max=` exits before Claude starts and prints `use depth=`. The session script flag is `--depth`.
- `forks` is parsed only by `just validate`. `just simulate` rejects it. Omitting `forks`, and `forks=1`, still run one session in `develop/`.
- `forks` greater than 1 calls `scripts/lesson-forks`. Between forks it resets `develop/` to the prepared commit with `git reset --hard` and `git clean`, leaving `.claude-home` and `.claude` in place. The second fork therefore does not see a file the first fork wrote.
- Each fork's stamp is the clock plus the fork index in seconds. If that directory already exists, that fork is not started and the earlier tree is left as it was.
- `scripts/lesson-forks judge-min` prints `1` when there is one fork and the fork count otherwise. `just validate` passes that value to `just judge`.
- The status line is still the M3 line from the newest in-range session. The journey stores no fork count.

## M7: A proof shows whether two forks can overlap (Status: ✅ DONE)

M6 already produces the trees a comparison needs, one after another. Overlap is only a question of wall time. One shared `develop/`, one shared Claude config directory, and a stamp name that is unique per second are the reasons two live processes may not be able to run together. This milestone measures that. It does not change `just validate`. A `PASS parallel` does not reopen M8.

**Acceptance Criteria:**

- [x] `just prove-parallel <lesson>` is a separate command. It starts two participant processes whose lifetimes overlap. `just validate` after this milestone still runs forks one after another.
- [x] Each process has its own working directory and its own Claude config directory. Neither working directory is the other's, and neither is the shared `develop/` of a `forks=1` run.
- [x] A test with two fake processes, and no Claude, writes two session logs in two stamp directories. A file created by one process is absent from the other process's directory. The command prints `PASS parallel` for that pair.
- [x] The command prints `FAIL parallel` and exits non-zero when a process fails to start, when the two working directories are the same path, or when both logs would be written into one stamp directory. The first log that was written is kept.
- [x] One live run of the command is the proof that Claude and nono can overlap. Its `PASS parallel` or `FAIL parallel` line is kept under `workshop/results/<lesson>/`. The automated test does not call Claude.

**Implementation Details:**

- `scripts/prove-parallel` copies the source tree twice and gives each copy its own config directory, taken from `.claude-home` when that directory exists. The two `participant-session` processes are started before either is joined. Neither working directory is `develop/`.
- The verdict line is written to `workshop/results/<lesson>/<stamp>-parallel.txt`. The two trees live under `proofs/`, so `lesson-status` does not count them as lesson stamps.
- The automated test uses a fake process. `just prove-parallel <lesson>` is the live command, and this change did not run it.
- `just validate` does not call `prove-parallel`. A pass from this command does not reopen M8.
- The spike served its purpose and was removed from the working tree. Two separate trees can be started together, and that left the serial validate loop unchanged. `just prove-parallel` and `scripts/prove-parallel` are not part of the harness anymore. The implementation remains in git history at `9427dba`.

## M8: Overlapping forks replace the serial loop when the proof passed (Status: POSTPONED)

Comparison needs several trees. It does not need those trees to be produced at the same time. M6 runs the forks one after another, and that is the behavior we are keeping. This milestone is not started.

**Acceptance Criteria:**

- [ ] `just validate` does not grow a parallel path from this milestone. `forks` greater than 1 stays the serial loop in M6.
- [ ] A `PASS parallel` from M7 does not by itself change `just validate`.
- [ ] Reopening this milestone is a separate decision. Until then the criteria below are not implemented.
- [ ] The deferred behavior, if it is reopened, is: n forks at the same time, each in its own working directory and config directory, each capped by `depth`, n stamp directories, the judge requiring n trees, and the M3 status line unchanged. `forks=1` stays one process in `develop/`.

**Implementation Details:**

- Verdict: stay sequential. Several forks are several prepared trees, run one after another, so the judge can compare them. Overlap would only shorten the wall clock.
- Decision: postpone M8 completely. Do not implement overlapping forks. M7 served its purpose and its command was removed from the working tree. That proof does not start this milestone.
- The obstacles that made overlap a separate question stay recorded here. One `develop/` would be written by both processes. One Claude config directory is unsafe to share. A stamp name is unique per second, so two forks that finish in the same second collide. None of those are solved by running the second fork later, and none of them need to be solved while the loop stays serial.
