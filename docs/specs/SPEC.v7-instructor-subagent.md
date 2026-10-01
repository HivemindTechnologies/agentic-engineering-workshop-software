# SPEC.v7: Instructor

The instructor is an agent in the outer repository. `workshop/JOURNEY.md` is its file. The director defines the table of contents, and with it the direction of the story: which lessons exist, their order, their headlines, and their content. The instructor keeps that journey intact and supports it. It does not add a lesson, remove a lesson, or reorder the lessons. A minor correction at that level is allowed only when the command names it explicitly. Support inside a lesson may be a few follow-up questions, or a small change so a participant is not stuck. The instructor stays on a few principles.

The hard goal is a workshop that runs from the first lesson to the last without a participant getting stuck. A lesson is smooth when its expected observations are what that lesson's judge can decide, and the latest judgement is `verdict: pass`. That is what "presentable" means. The instructor changes that lesson when it is not smooth.

A journey that is easy to follow is a soft goal. The instructor keeps a prompt sequence going, and sometimes starts a new segment. When to do which is hard to judge, so that choice does not pass or fail the workshop. M1 is the board of those distances. Every later milestone reads that report. It does not compute a second distance. v6's status line is the input for smoothness. M2 records the wall-clock time of a scripted participant run beside `interactions` and `length`, before the instructor runs, so the first of those runs already has it. That time is a lower bound for a human. Nothing in v6 depends on this spec.

## M1: Each prompt has a distance to the previous and the next (Status: ✅ DONE)

This comes first. The rest of the spec uses this report when it talks about segments. The numbers are an aid for the director and the instructor. They are not a gate.

**Acceptance Criteria:**

- [x] `just prompt-distance` runs a script. It reads the fenced prompt under `*PROMPT TO TEST*` in `workshop/JOURNEY.md`. It does not edit that file, it does not prepare `develop/`, and it does not start Claude.
- [x] `just prompt-distance <lesson>` prints one line, that lesson only. `just prompt-distance` with no lesson prints the whole board: one line per lesson, in journey order, and nothing else mixed into those lines.
- [x] A printed line holds that lesson's own distances: the similarity to the previous lesson's prompt and to the next lesson's prompt. The first lesson has no previous. The last lesson has no next. Each number is a sign and four decimal places, so every number occupies the same width. `absent` is padded to that same width. Predecessor distances are not printed. They are written to `workshop/prompt-distance.txt`, one line per lesson, with each earlier lesson named on that line.
- [x] The similarity is the cosine similarity of the embeddings of the two texts. One report uses one embedding function. A fixture whose embeddings are known produces those similarities. Identical vectors are similarity 1. Orthogonal vectors are similarity 0. The automated test supplies the vectors. It does not call an embedding service.
- [x] On the whole board, a new segment starts before a lesson whose similarity to the previous lesson is strictly below the mean of all previous-neighbor similarities. When every such similarity equals that mean, the journey is one segment. The segment ranges are printed after the lines. A single lesson prints no segment ranges.
- [x] A low similarity does not fail the command. The command exits non-zero only when a named lesson has no fenced prompt, or the lesson is unknown.

**Implementation Details:**

- `scripts/prompt-distance` reads the fenced prompt. `just prompt-distance` and `just prompt-distance <lesson>` call it. Neither prepares `develop/` nor starts Claude.
- Tests pass known vectors with `--vectors`. The command's own embedding is a local token hash, so one report uses one function and does not call a service.
- A similarity prints as a sign and four decimal places, seven characters: `+1.0000`, `+0.0000`, `-0.3939`. `absent` is right-aligned in that same width.
- A printed line is the lesson, then `previous=` and `next=`. The predecessor columns are only in `workshop/prompt-distance.txt`, written beside `workshop/JOURNEY.md` and gitignored. The first lesson's previous field is `absent`. The last lesson's next field is `absent`.
- Segment lines are `segment <first> <last>` after the board lines. A named lesson prints one line and no segment lines.
- A new segment starts where the similarity to the previous lesson is strictly below the mean of those previous-neighbor similarities.

## M2: Scripted run time is the baseline for a human (Status: ✅ DONE)

The participant agent runs are coordinated and scripted. The wall-clock time of those runs is the least time a human needs to go through the same lessons. It is the baseline for planning the workshop. It sits with the measures that are already on the status line. It is recorded before the later milestones start those runs, so the first run already carries it.

**Acceptance Criteria:**

- [x] A scripted participant run records `wall_seconds` as the elapsed time from process start to process exit, rounded up to the next whole second. The record is kept with that run's `session.jsonl`. A second read of the same record yields the same number.
- [x] The status line keeps `interactions=` and `length=` as in v6. When the run has a wall-clock record, the line adds `wall_seconds=` after `length=`. Example shape: `refine-1 PASS interactions=4 length=12043 wall_seconds=90`.
- [x] When a trace exists and the wall-clock record is missing, the value is `wall_seconds=absent`. It is never stored as zero in place of a missing record. The measures are omitted only when the lesson has no `session.jsonl` at or after the cutoff, as in v6.
- [x] The newest in-range session supplies the lesson's `wall_seconds`, the same session that supplies `interactions` and `length`. The workshop baseline is the sum of those per-lesson values, printed once after the status lines. A lesson with `wall_seconds=absent` is left out of the sum.
- [x] The sum is a lower bound for planning. The harness does not fail a lesson because `wall_seconds` is high, and it does not fail a lesson because the record is absent.
- [x] A fixture with a known elapsed time yields that `wall_seconds`. The test does not start Claude.

**Implementation Details:**

- `scripts/participant-session` appends `{"type": "wall", "wall_seconds": N}` to `session.jsonl` after the process exits. `N` is the monotonic elapsed time, rounded up with `math.ceil`.
- `scripts/lesson-status measures` prints `wall_seconds=` after `length=` and before `capped=yes`. A trace with no wall event prints `wall_seconds=absent`.
- `lines` prints `baseline wall_seconds=<sum>` once after the status lines. Lessons with `wall_seconds=absent` are left out of the sum. When none contribute, the sum is 0. That 0 is the sum, not a stored missing record.
- A high value or an absent record does not by itself make a lesson FAIL. A `FAIL simulate` or `FAIL judge` line still exits non-zero.

## M3: The instructor is an agent over the journey (Status: ✅ DONE)

The agent description carries the direction and the principles. The journey file is the only story it edits. When it judges a segment, it reads the M1 report.

**Acceptance Criteria:**

- [x] `.claude/agents/instructor.md` exists. Its frontmatter sets `name: instructor`, a `description`, and `permissionMode: acceptEdits`. The body is the system prompt. The file does not set `maxTurns`.
- [x] The body names `workshop/JOURNEY.md` as the file it supports. It says the director owns the table of contents: the lessons, their order, their headlines, and their content. It says the instructor keeps that table intact. A minor correction to a lesson's presence, order, or headline is allowed only when the instructor states that correction explicitly. Support inside a lesson may be a few follow-up questions or a small change to the prompt or the expected observations.
- [x] The body states the direction: the lessons walk from a plain refine prompt, through `/refine` and settled choices, toward implementation.
- [x] The body states these principles: one short prompt per lesson, keep a prompt sequence until a new segment is warranted, a stuck participant is a reason to support that lesson, and smooth means the judge recorded `verdict: pass`. It says the M1 similarities are evidence for the segment judgment. A similarity is not a pass or a fail.
- [x] The body does not tell the instructor to write under `develop/`, to write `verdict: pass` or `verdict: fail`, or to do the participant's work.
- [x] The harness does not copy `instructor.md` into `develop/`.

**Implementation Details:**

- `.claude/agents/instructor.md` is the system prompt. It does not set `maxTurns`.
- The harness copies `.claude/agents/participant.md` into `develop/`. It does not copy `instructor.md`.

## M4: A smooth lesson is one the judge can pass (Status: ✅ DONE)

This is the hard goal. The instructor does not grade the lesson. The judge does. The instructor's move, when the lesson is not smooth, is a small change to that same lesson.

**Acceptance Criteria:**

- [x] A lesson is smooth when it has a `JUDGE.md` and the newest in-range judgement contains a line `verdict: pass`. The observations in that lesson are the observations that judge is asked to decide.
- [x] A lesson with no `JUDGE.md` is not smooth and is not a failure. The instructor leaves it, and reports it as not yet judged.
- [x] When a lesson is not smooth, the instructor supports that lesson: a few follow-up questions, or a small change to its fenced prompt or its expected observations, and it names the lesson. That support is not a new lesson, a removed lesson, or a new headline. It does not add a fact to a later lesson in order to make an earlier lesson pass.
- [x] When a lesson is already smooth, the instructor leaves that lesson's prompt and observations as written.
- [x] The workshop is presentable when every lesson that has a `JUDGE.md` is smooth.

**Implementation Details:**

- A lesson is smooth when `workshop/results/<lesson>/JUDGE.md` exists and `scripts/lesson-status verdict` prints `pass`. That word is the newest in-range judgement. The harness does not compare observation wording with the judge prompt. When the lesson is smooth, the command leaves the prompt and the observations as written.
- No `JUDGE.md` prints `<lesson> not yet judged` and does not fail the command.
- A lesson that is not smooth is named. The command does not edit that section and does not edit a later lesson. It prints why it left the section unchanged. The agent text tells the instructor to support that lesson inside the section.

## M5: One prompt per lesson, and the segment is a judgment (Status: ✅ DONE)

A journey that is easy to follow keeps one prompt sequence for as long as it still fits, and starts a new segment when it no longer does. That boundary is the instructor's judgment. The distances come from M1. This milestone does not turn them into a pass or a fail.

**Acceptance Criteria:**

- [x] Each lesson has one `*PROMPT TO TEST*` block. That block is the prompt. Follow-up questions, when the instructor chooses them, sit in the same lesson outside that block. They are not a second prompt.
- [x] The instructor may keep the current prompt sequence or start a new segment. The agent description says that this choice is the instructor's judgment, informed by that lesson's M1 line: similarity to the previous prompt and to the next prompt. Predecessor similarities are in `workshop/prompt-distance.txt`.
- [x] `just instruct` does not fail because of how similar two prompts are, or because of where a segment falls. It shows the M1 line for each lesson it visits. It does not compute another distance.

**Implementation Details:**

- `scripts/instruct` exits before editing when a visited lesson has a count of `*PROMPT TO TEST*` lines other than one. Follow-up text outside that block is not a second prompt.
- The agent text says that keeping the sequence or starting a segment is the instructor's judgment, informed by that lesson's M1 line. Predecessor similarities stay in `workshop/prompt-distance.txt`.
- The command prints the report from `scripts/prompt-distance`. It does not compute a second distance. Similarity and segment placement do not change the exit code.

## M6: Instruct one lesson, or every lesson (Status: ✅ DONE)

The director runs the instructor the way `just validate` runs a lesson: one named lesson, or the whole journey in order.

**Acceptance Criteria:**

- [x] `just instruct <lesson>` reads that lesson in `workshop/JOURNEY.md`, the M1 line for that lesson, and the latest validate result for it. The instructor's working directory is the outer repository. The command does not prepare `develop/` and does not write under `develop/`.
- [x] `just instruct` with no lesson does that for every lesson in journey order. A lesson that is not smooth does not stop the rest. The M1 report for the whole journey is printed once, and each lesson is visited with its own line from that report.
- [x] After the command, the lesson ids and their order are the director's table of contents. A headline change other than the `last:` mark is a minor correction, and the command prints it explicitly as a TOC correction. A lesson that was already smooth is otherwise unchanged. A lesson that was not smooth has support confined to that lesson's section, or the command prints why it left the section unchanged.
- [x] The command exits non-zero when any lesson that has a `JUDGE.md` is still not smooth. A lesson with no `JUDGE.md` does not by itself fail it. A low M1 similarity does not fail it.
- [x] The command does not start the participant and does not start the judge.

**Implementation Details:**

- `just instruct` and `just instruct <lesson>` run `scripts/instruct` on `workshop/JOURNEY.md` and `workshop/results`. The working directory is the outer repository. The command does not prepare `develop/`, does not write under `develop/`, and does not start Claude.
- With no lesson, the M1 report is printed once, then every lesson is visited in journey order with its own line from that report. A lesson that is not smooth does not stop the rest.
- The exit status is non-zero when any visited lesson that has a `JUDGE.md` is not smooth. A headline change other than the `last:` mark, including a change of lesson order, is printed as `TOC correction:`. The harness itself only writes `last:` marks.

## M7: The journey heading shows the last validate result (Status: ✅ DONE)

This is a soft goal for the director. The heading carries the last result so a lesson that needs care is visible in the journey itself. The instructor reads that mark. It does not invent it.

**Acceptance Criteria:**

- [x] A lesson heading may end with `(last: PASS)`, `(last: FAIL simulate)`, `(last: FAIL judge)`, or `(last: not run)`. When the lesson has a tree at or after its cutoff, the mark adds that newest tree's stamp, as in `(last: PASS 2026-09-28-18-30-29)`. The word is the verdict word from that lesson's status line. The lesson id still begins the heading, as in `## refine-1:`.
- [x] `scripts/lesson-status heading` writes the mark. `just validate` calls it after each lesson it visits, including a lesson it does not simulate. The instructor agent does not write a `last:` mark.
- [x] `just instruct <lesson>` refreshes that lesson's mark before it decides whether the lesson is smooth. `just instruct` with no lesson refreshes each lesson it visits.
- [x] A missing `last:` mark does not fail M4. The section extractor and `just prepare` still find the lesson by the `## <lesson>:` prefix. `just prompt-distance` still finds the fenced prompt.

**Implementation Details:**

- The mark is the status word, then the newest in-range tree stamp when one exists. `just validate` writes it after printing that lesson's status line. A lesson with no in-range tree is `(last: not run)` with no stamp.
- `just instruct` uses the same writer, then reads `scripts/lesson-status verdict`. A missing mark does not make the lesson fail. The heading still begins `## <lesson>:`, so the section extractor and `just prompt-distance` still find it. `just prepare` finds the lesson by id.
- The instructor agent is told not to write a `last:` mark that the status line does not show.
