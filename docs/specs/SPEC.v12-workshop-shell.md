# SPEC.v12: Workshop shell banners and status

The outer `just` list, `nix develop`, and `just sandbox` look like any other shell. `just prepare` prints the lesson section with no break from the rebuild noise above it. The participant who wants a wall-clock hint has to open `workshop/results/status.yaml` or run Python. This spec puts a recognisable banner on each shell surface, frames the lesson after prepare, stores a human-readable runtime next to the lesson in `workshop/JOURNEY.md`, and makes `just status` a yq view of that YAML.

`just prepare` stays shell and awk. It does not call Python and it does not call yq. The harness that already writes `(last: …)` is what writes the runtime lines. Recorded trees under `workshop/results/` stay as they are; only the journey headings, the justfile, the flake shell hook, and the status recipes change.

The banner source is the HIVEMIND block below. Each surface that prints it may add one short tag line under the art so the outer shell, the develop shell, and prepare are distinguishable. The art itself is the same bytes in every surface.

```
 ██╗  ██╗██╗██╗   ██╗███████╗███╗   ███╗██╗███╗   ██╗██████╗
 ██║  ██║██║██║   ██║██╔════╝████╗ ████║██║████╗  ██║██╔══██╗
 ███████║██║██║   ██║█████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║
 ██╔══██║██║╚██╗ ██╔╝██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
 ██║  ██║██║ ╚████╔╝ ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
                              agentic engineering workshop
```

## M1a: Outer shell banner on `just` (Status: ✅ DONE)

`just` with no recipe is the outer harness list. It prints the banner, then a tag that names the outer shell, then the recipe list.

**Acceptance Criteria:**

- [x] A file under the repository holds the banner art as the exact seven lines above, including the leading space on each art line and the `agentic engineering workshop` line.
- [x] `just` with no arguments prints that art, then a tag line that contains `outer`, then the same recipe list `just --list` would print. The tag line is not one of the seven art lines.
- [x] The test captures `just` stdout from the repository root. It does not start Claude.

**Implementation Details:**

- The art is `workshop/banner.txt`. `scripts/banner <kind>` prints a blank line, the six art lines, then `agentic engineering workshop` left-aligned and `<kind>` right-aligned on one line, then a blank line. The default recipe runs `scripts/banner "outer shell"` and then `just --list`.

## M1b: Develop shell banner on `nix develop` (Status: ✅ DONE)

Entering the flake shell is the develop tooling surface. Its hook prints the banner and a tag that names the develop shell.

**Acceptance Criteria:**

- [x] `flake.nix` `shellHook` prints the same banner art as M1a, then a tag line that contains `develop shell`, after the existing cache exports.
- [x] The hook does not call Python and does not call yq.
- [x] The test is a search of `flake.nix` for the banner script path and for the `develop shell` tag. It does not start Claude and it does not require a live `nix develop`.

**Implementation Details:**

- `shellHook` runs `scripts/banner "develop shell"`. `pkgs.yq-go` is added for M3; the hook itself does not call it.

## M1c: Sandbox banner on `just sandbox` (Status: ✅ DONE)

`just sandbox` is the interactive shell inside `develop/`. It prints the banner with a sandbox kind before the sandboxed bash starts.

**Acceptance Criteria:**

- [x] `just sandbox` prints the same banner art as M1a and a tag line that contains `sandbox shell` before it starts the sandboxed shell.
- [x] The recipe does not call Python and does not call yq to print the banner.
- [x] The test is a search of the justfile `sandbox` recipe, or a dry capture that stops before the interactive shell. It does not start Claude.

**Implementation Details:**

- The `sandbox` recipe runs `scripts/banner "sandbox shell"` before `nono` starts bash.

## M1d: Prepare frames the lesson with the banner (Status: ✅ DONE)

After the rebuild, the lesson section is easy to miss in the scrollback. Prepare prints blank lines, the banner, a short tag, then the lesson section as it does today.

**Acceptance Criteria:**

- [x] `just prepare <lesson>` still rebuilds `develop/` (or applies `keep=yes`) and still prints that lesson's `# <slug>:` section from `workshop/JOURNEY.md` via awk, as in v9.M7.
- [x] After the rebuild work and before the lesson section, stdout contains at least two blank lines, then the banner art, then a tag line, then the lesson section. The tag line is not part of the journey file.
- [x] The `prepare` recipe body does not invoke `python`, `python3`, or `yq`.
- [x] The test runs `just prepare` against a temporary work directory as today's prepare tests do, and asserts the blank lines, the banner, and the section. It does not start Claude.

**Implementation Details:**

- `frame_lesson` runs `scripts/banner prepare`, then the awk section. Listing lessons with no argument is unchanged.

## M2: Journey carries a human-readable runtime for prepare (Status: ✅ DONE)

The participant should see how long the last scripted run took without opening `status.yaml`. The harness that already writes `(last: …)` also writes two lines under the heading. Prepare prints them because they are part of the section. Prepare does not compute them.

**Acceptance Criteria:**

- [x] When `scripts/lesson-status heading` writes a `(last: …)` mark for a lesson whose newest in-range session has a wall-clock record, it also writes a line `Minimum Runtime: mm:ss` immediately under that heading. `mm:ss` is the wall seconds as zero-padded minutes and seconds (90 seconds is `01:30`).
- [x] When that session has a known `length`, the same write also adds `Last Token Usage: X.Xk` on the next line, where `X.Xk` is `length / 1000` printed with one decimal place and a trailing `k`.
- [x] When wall seconds or length is absent, the corresponding line is omitted. A second heading write replaces the previous runtime lines for that lesson and does not leave duplicates.
- [x] `just prepare <lesson>` prints those lines when they are present in the section. The prepare recipe does not read `status.yaml`, does not call Python, and does not call yq to obtain them.
- [x] The test feeds a fixture journey and a fixture results tree with a known wall event and length, runs `heading`, and asserts the two lines. A second case with absent wall omits `Minimum Runtime`. It does not start Claude.

**Implementation Details:**

- `runtime_lines` reads the newest in-range `session.jsonl`. Heading deletes any existing `Minimum Runtime:` / `Last Token Usage:` lines under that heading before inserting the fresh ones.

## M3: `just status` displays status.yaml through yq (Status: ✅ DONE)

Today `just status` only rewrites `workshop/results/status.yaml` and prints nothing. The participant wants to read that file from the shell. Display moves onto `just status`; the silent rewrite gets a clearer name.

**Acceptance Criteria:**

- [x] `just status` prints the contents of `workshop/results/status.yaml` using `yq`. It does not rewrite the file.
- [x] `just status <lesson>` prints only that lesson's entry from the same file using `yq`, and exits non-zero when the lesson id is absent from the file.
- [x] The silent rewrite that today's `just status` performed is available as `just status-write`, and `just validate` still writes the same file after its lesson loop. `flake.nix` lists `yq` among the develop shell packages.
- [x] The test runs the display recipes against a fixture `status.yaml` and asserts the printed YAML. It does not start Claude.

**Implementation Details:**

- `just status` runs `yq '.'` on the file, or `yq -e` with a lesson select. `just status-write` keeps the silent `lesson-status yaml` rewrite. The flake package is `pkgs.yq-go` (the `yq` binary).
