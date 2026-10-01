# `@` before a shebang recipe prints the script before it runs.
# On an ordinary recipe line, `@` hides that line.

default:
    @{{justfile_directory()}}/scripts/banner "outer shell"
    @just --list

# Harness tests, on the python installed on this machine.
# The Scala gate is `just check` inside develop/.
test:
    python3 -m unittest discover -s tests -p '*_test.py'

# Point this clone at hooks/pre-commit. Changes no other git config.
install-hooks:
    python3 scripts/install-hooks "{{justfile_directory()}}"

# Show workshop/results/status.yaml. With a lesson id, show that entry only.
status lesson="":
    #!/usr/bin/env bash
    set -euo pipefail
    file="{{justfile_directory()}}/workshop/results/status.yaml"
    lesson="{{lesson}}"
    if [[ -z "$lesson" ]]; then
      yq '.' "$file"
      exit 0
    fi
    yq -e ".lessons[] | select(.lesson == \"$lesson\")" "$file"

# Newest in-range run of every lesson. Prints nothing.
status-write:
    @python3 scripts/lesson-status yaml "{{justfile_directory()}}/workshop/results" "{{justfile_directory()}}/workshop/results/status.yaml"

strict := "false"
profile := justfile_directory() / (if strict == "true" { "nono-strict.json" } else if strict == "false" { "nono.json" } else { error("strict must be true or false, got: " + strict) })
sandbox := env_var_or_default("PREPARE_WORK", justfile_directory() / "develop")
record := env_var_or_default("PREPARE_RECORD", justfile_directory() / ".prepare-lesson")
material := justfile_directory() / "workshop" / "material"
cache := justfile_directory() / ".cache"
history := justfile_directory() / ".sandbox_history"

# Rebuild develop/ from base through <lesson>, then print that lesson.
# keep=yes applies only the deltas after the lesson recorded outside develop/.
[positional-arguments]
prepare lesson="" keep="":
    #!/usr/bin/env bash
    set -euo pipefail
    keep="{{keep}}"
    keep="${keep#keep=}"
    lesson=""
    for token in "$@"; do
      [[ -z "$token" ]] && continue
      case "$token" in
        keep=*) keep="${token#keep=}" ;;
        *)
          if [[ -n "$lesson" ]]; then
            echo "unexpected argument: $token" >&2
            exit 1
          fi
          lesson="$token"
          ;;
      esac
    done
    root="{{justfile_directory()}}"
    mapfile -t order < <("$root/scripts/lesson-order" "$root/workshop/JOURNEY.md")
    if [[ -z "$lesson" ]]; then
      printf '%s\n' "${order[@]}"
      exit 0
    fi
    if [[ -n "$keep" && "$keep" != "yes" ]]; then
      echo "unknown prepare flag: keep=$keep" >&2
      exit 1
    fi
    found=0
    for id in "${order[@]}"; do
      [[ "$id" == "$lesson" ]] && found=1
    done
    if [[ "$found" != 1 ]]; then
      echo "unknown lesson: $lesson" >&2
      echo "lessons: ${order[*]}" >&2
      exit 1
    fi

    work="{{sandbox}}"
    record="{{record}}"

    print_lesson() {
      awk -v lesson="$lesson" '
        $0 ~ "^# " lesson ":" { show = 1 }
        show && /^# / && $0 !~ "^# " lesson ":" { exit }
        show { print }
      ' "$root/workshop/JOURNEY.md"
    }

    frame_lesson() {
      "$root/scripts/banner" prepare
      print_lesson
    }

    if [[ "$keep" == "yes" ]]; then
      if [[ ! -s "$record" ]]; then
        echo "no recorded lesson; run: just prepare <lesson>" >&2
        exit 1
      fi
      recorded="$(tr -d '[:space:]' < "$record")"
      recorded_at=""
      target_at=""
      i=0
      for id in "${order[@]}"; do
        [[ "$id" == "$recorded" ]] && recorded_at="$i"
        [[ "$id" == "$lesson" ]] && target_at="$i"
        i=$((i + 1))
      done
      if [[ -z "$recorded_at" ]]; then
        echo "recorded lesson is unknown: $recorded" >&2
        exit 1
      fi
      if [[ "$target_at" -lt "$recorded_at" ]]; then
        echo "$lesson is before the recorded lesson $recorded" >&2
        exit 1
      fi
      if [[ "$target_at" != "$recorded_at" ]]; then
        started=0
        for id in "${order[@]}"; do
          if [[ "$started" == 1 ]]; then
            just _delta-"$id"
          fi
          [[ "$id" == "$lesson" ]] && break
          [[ "$id" == "$recorded" ]] && started=1
        done
        printf '%s\n' "$lesson" > "$record"
      fi
      frame_lesson
      exit 0
    fi

    rm -rf "$work"
    mkdir -p "$work"
    git -C "$work" init -b main
    cp -a "$root/workshop/material/00-base/." "$work/"
    git -C "$work" add -A
    git -C "$work" commit -m "base"

    for id in "${order[@]}"; do
      just _delta-"$id"
      [[ "$id" == "$lesson" ]] && break
    done
    printf '%s\n' "$lesson" > "$record"
    frame_lesson

_delta-refine-1:
    @true

_delta-refine-1a:
    cp -a {{material}}/refine-1a/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "refine-1a"

_delta-refine-2:
    @true

_delta-refine-3:
    @true

_delta-refine-4:
    cp -a {{material}}/refine-4/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "refine-4"

_delta-refine-5:
    cp -a {{material}}/refine-5/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "refine-5"

_delta-refine-6:
    cp -a {{material}}/refine-6/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "refine-6"

_delta-implement-1:
    cp -a {{material}}/implement-1/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "implement-1"

_delta-implement-1b:
    cp -a {{material}}/implement-1b/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "implement-1b"

_delta-implement-2:
    cp -a {{material}}/implement-2/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "implement-2"

_delta-quality-gates-1:
    cp -a {{material}}/quality-gates-1/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "quality-gates-1"

_delta-refine-7:
    cp -a {{material}}/refine-7/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "refine-7"

_delta-quality-gates-2:
    cp -a {{material}}/quality-gates-2/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "quality-gates-2"

_delta-skills-1:
    cp -a {{material}}/skills-1/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "skills-1"

# skills-1 asks the participant to remove these two commands; the delta
# repeats that removal so a rebuild lands on the same tree the participant left.
_delta-skills-2:
    rm -f {{sandbox}}/.claude/commands/refine.md {{sandbox}}/.claude/commands/implement.md
    cp -a {{material}}/skills-2/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "skills-2"

_delta-quality-gates-3:
    cp -a {{material}}/quality-gates-3/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "quality-gates-3"

_delta-quality-gates-4:
    cp -a {{material}}/quality-gates-4/. {{sandbox}}/
    git -C {{sandbox}} add -A
    git -C {{sandbox}} commit -m "quality-gates-4"

# Replace develop/ with a result stamp (v13.M6). Not a prepare flag.
[positional-arguments]
restore lesson stamp="":
    #!/usr/bin/env bash
    set -euo pipefail
    lesson=""
    stamp=""
    for token in "$@"; do
      if [[ -z "$lesson" ]]; then
        lesson="$token"
      elif [[ -z "$stamp" ]]; then
        stamp="$token"
      else
        echo "unexpected argument: $token" >&2
        exit 1
      fi
    done
    [[ -n "$lesson" ]] || { echo "usage: just restore <lesson> [stamp]" >&2; exit 1; }
    root="{{justfile_directory()}}"
    results="$root/workshop/results/$lesson"
    [[ -d "$results" ]] || { echo "no results for $lesson" >&2; exit 1; }
    if [[ -n "$stamp" ]]; then
      "$root/scripts/restore-result" "$results" "{{sandbox}}" "{{record}}" "$stamp"
    else
      "$root/scripts/restore-result" "$results" "{{sandbox}}" "{{record}}"
    fi

# Pruned directory tree (v13.M8). No lesson → current develop/. Lesson → newest
# in-range stamp (or named stamp). Same exclusions as capture-result-tree.
[positional-arguments]
tree lesson="" stamp="":
    #!/usr/bin/env bash
    set -euo pipefail
    lesson=""
    stamp=""
    for token in "$@"; do
      [[ -z "$token" ]] && continue
      if [[ -z "$lesson" ]]; then
        lesson="$token"
      elif [[ -z "$stamp" ]]; then
        stamp="$token"
      else
        echo "unexpected argument: $token" >&2
        exit 1
      fi
    done
    root="{{justfile_directory()}}"
    if [[ -z "$lesson" ]]; then
      python3 "$root/scripts/pruned-tree" "{{sandbox}}"
      exit 0
    fi
    results="$root/workshop/results/$lesson"
    if [[ -n "$stamp" ]]; then
      python3 "$root/scripts/pruned-tree" --results "$results" --stamp "$stamp"
    else
      python3 "$root/scripts/pruned-tree" --results "$results"
    fi

# sandbox and claude run in any develop/, even an empty one without git,
# so a free session needs no prepared lesson.
_develop:
    mkdir -p {{sandbox}}

# Shell inside develop/. bash --noprofile --norc reads no rc files.
# History is the harness file .sandbox_history, not ~/.bash_history, so prepare
# can delete develop/ and the shell-config denies stay quiet.
# --no-diagnostics skips the grant picker nono shows after those denies.
sandbox: _develop
    @{{justfile_directory()}}/scripts/banner "sandbox shell"
    mkdir -p {{cache}}
    touch {{history}}
    cd {{sandbox}} && HISTFILE={{history}} HISTSIZE=1000 HISTFILESIZE=2000 PS1='develop \$ ' nono run --no-diagnostics -p {{profile}} --allow {{cache}} --allow-file {{history}} -- bash --noprofile --norc

# Claude Code home for this lesson. Wiped with develop/.
# Seeds hasTrustDialogAccepted for the sandbox root (v13.M2a).
_claude-home: _develop
    {{justfile_directory()}}/scripts/nono-ensure-claude-dirs.sh
    {{justfile_directory()}}/scripts/claude-home-seed {{sandbox}}/.claude-home {{sandbox}}

# Claude Code inside the sandbox. Config stays in develop/.claude-home.
[positional-arguments]
claude *args: _claude-home
    mkdir -p {{cache}}
    cd {{sandbox}} && CLAUDE_CONFIG_DIR={{sandbox}}/.claude-home nono run --no-diagnostics -p {{profile}} --allow {{cache}} -- claude "$@"

# Send the lesson section at develop/. prep=true rebuilds that lesson first.
# prep=no keeps the current tree. depth=N keeps the same process open for follow-ups.
# See docs/specs/SPEC.v2-simulation.md and docs/specs/SPEC.v6-interactive-tracked-participant-subagent.md.
[positional-arguments]
simulate lesson prep="true":
    #!/usr/bin/env bash
    set -euo pipefail
    # positional-arguments delivers tokens like prep=no and depth=3 whole.
    prep="{{prep}}"
    prep="${prep#prep=}"
    lesson=""
    depth=""
    for token in "$@"; do
      case "$token" in
        prep=*) prep="${token#prep=}" ;;
        depth=*) depth="${token#depth=}" ;;
        max=*) echo "use depth=" >&2; exit 1 ;;
        forks=*) echo "forks is a parameter of just validate" >&2; exit 1 ;;
        true|yes|false|no)
          # just may pass the prep= default as a bare positional under [positional-arguments]
          prep="$token"
          ;;
        *)
          if [[ -z "$lesson" ]]; then
            lesson="$token"
          else
            echo "unexpected argument: $token" >&2
            exit 1
          fi
          ;;
      esac
    done
    [[ -n "$lesson" ]] || { echo "usage: just simulate <lesson> [prep=true|no] [depth=N]" >&2; exit 1; }
    if [[ -n "$depth" ]]; then
      [[ "$depth" =~ ^[0-9]+$ && "$depth" -ge 1 ]] || { echo "bad depth: $depth" >&2; exit 1; }
    fi
    root="{{justfile_directory()}}"
    work="$root/develop"
    steps="$root/workshop/JOURNEY.md"
    mapfile -t order < <("$root/scripts/lesson-order" "$steps")

    found=0
    for id in "${order[@]}"; do
      [[ "$id" == "$lesson" ]] && found=1
    done
    if [[ "$found" != 1 ]]; then
      echo "unknown lesson: $lesson" >&2
      echo "lessons: ${order[*]}" >&2
      exit 1
    fi

    case "$prep" in
      true|yes) ;;
      no|false) ;;
      *) echo "prep must be true or no, got: $prep" >&2; exit 1 ;;
    esac

    absent=()
    if ! paths_text=$("$root/scripts/lesson-forks" paths "$lesson"); then
      echo "no expected paths for $lesson yet" >&2
      exit 1
    fi
    mapfile -t paths <<< "$paths_text"

    prompt=$("$root/scripts/participant-session" section "$steps" "$lesson")
    if [[ -z "$prompt" ]]; then
      echo "no prompt for $lesson in $steps" >&2
      exit 1
    fi

    if [[ "$prep" == true || "$prep" == yes ]]; then
      just prepare "$lesson"
    elif [[ ! -d "$work/.git" ]]; then
      echo "no develop/ repository; run: just prepare <lesson>" >&2
      exit 1
    fi
    just _claude-home
    mkdir -p "{{cache}}"

    stamp=$(date +%Y-%m-%d-%H-%M-%S)
    dest="$root/workshop/results/$lesson/$stamp"
    "$root/scripts/lesson-forks" claim "$dest"
    echo "simulation $lesson -> $dest"

    "$root/scripts/participant-session" install --from "$root/.claude/agents/participant.md" --work "$work"
    args=(
      "$root/scripts/participant-session" run
      --work "$work"
      --log "$dest/session.jsonl"
      --message "$prompt"
    )
    if [[ -n "$depth" ]]; then
      args+=(--depth "$depth")
    fi
    for rel in "${paths[@]}"; do
      args+=(--expect "$rel")
    done
    args+=(
      --
      env "CLAUDE_CONFIG_DIR=$work/.claude-home"
      nono run --no-diagnostics -p "{{profile}}" --allow "{{cache}}" --
      claude -p
      --agent participant
      --input-format stream-json
      --output-format stream-json
      --verbose
      --permission-mode bypassPermissions
      --permission-prompts none
    )
    set +e
    "${args[@]}"
    code=$?
    set -e

    missing=0
    if [[ ${#paths[@]} -gt 0 ]]; then
    for rel in "${paths[@]}"; do
      if [[ ! -f "$work/$rel" ]]; then
        missing=1
      fi
    done
    fi
    unexpected=0
    if [[ ${#absent[@]} -gt 0 ]]; then
    for rel in "${absent[@]}"; do
      if [[ -f "$work/$rel" ]]; then
        unexpected=1
      fi
    done
    fi
    why=$(jq -Rrn '[inputs | fromjson? | select(type=="object" and .type=="result" and .subtype=="success")] | last | .result // empty' "$dest/session.jsonl" 2>/dev/null || true)
    if [[ "$code" != 0 || "$missing" != 0 || "$unexpected" != 0 ]]; then
      echo "FAIL simulate $lesson"
      if [[ ${#paths[@]} -gt 0 ]]; then
        echo "expected: ${paths[*]}"
        if [[ "$missing" != 0 ]]; then
          echo "received: missing"
        else
          echo "received: claude exited $code"
        fi
      else
        echo "expected: ${absent[*]} absent"
        echo "received: present"
      fi
      echo "why:"
      if [[ -n "$why" ]]; then
        printf '%s\n' "$why"
      else
        echo "claude exited $code and returned no reply"
      fi
      echo "log: $dest/session.jsonl"
      exit 1
    fi
    "$root/scripts/capture-result-tree" "$work" "$dest"
    echo "PASS simulate $lesson"
    if [[ ${#paths[@]} -gt 0 ]]; then
      echo "expected: ${paths[*]}"
      echo "received: present"
    else
      echo "expected: ${absent[*]} absent"
      echo "received: absent"
    fi
    echo "saved $dest"

# Judge result trees from the harness root. Does not read or write develop/.
# A lesson is workshop/results/<lesson>/: stamp directories, judgements/, JUDGE.md.
# Stamps narrow the set. With none, every stamp at or after results/<lesson>/cutoff.
# No cutoff file means every stamp. Older trees stay on disk and are not judged.
# See docs/specs/SPEC.v3-judge.md.
[positional-arguments]
judge lesson *stamps:
    #!/usr/bin/env bash
    set -euo pipefail
    lesson="${1:?usage: just judge <lesson> [stamp...]}"
    shift
    root="{{justfile_directory()}}"
    results="$root/workshop/results/$lesson"
    judge="$results/JUDGE.md"
    [[ -f "$judge" ]] || { echo "no judge prompt: $judge" >&2; exit 1; }

    stamp_re='^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$'
    min=2
    kept=()
    for token in "$@"; do
      if [[ "$token" == min=* ]]; then
        min="${token#min=}"
        [[ "$min" =~ ^[0-9]+$ && "$min" -ge 1 ]] || { echo "bad min: $min" >&2; exit 1; }
        continue
      fi
      kept+=("$token")
    done
    if [[ ${#kept[@]} -gt 0 ]]; then
      set -- "${kept[@]}"
    else
      set --
    fi
    cutoff=""
    if [[ -f "$results/cutoff" ]]; then
      cutoff=$(tr -d '[:space:]' < "$results/cutoff")
      [[ "$cutoff" =~ $stamp_re ]] || { echo "bad cutoff in $results/cutoff: $cutoff" >&2; exit 1; }
    fi
    chosen=()
    skipped=()
    if [[ $# -gt 0 ]]; then
      for stamp in "$@"; do
        [[ "$stamp" =~ $stamp_re ]] || { echo "not a stamp: $stamp" >&2; exit 1; }
        [[ -d "$results/$stamp" ]] || { echo "no result tree: $results/$stamp" >&2; exit 1; }
        if [[ -n "$cutoff" && "$stamp" < "$cutoff" ]]; then
          skipped+=("$stamp")
          continue
        fi
        chosen+=("$stamp")
      done
    else
      shopt -s nullglob
      for dir in "$results"/*/; do
        stamp=$(basename "$dir")
        [[ "$stamp" =~ $stamp_re ]] || continue
        if [[ -n "$cutoff" && "$stamp" < "$cutoff" ]]; then
          skipped+=("$stamp")
          continue
        fi
        chosen+=("$stamp")
      done
    fi
    if [[ -n "$cutoff" ]]; then
      echo "cutoff: $cutoff"
      if [[ ${#skipped[@]} -gt 0 ]]; then
        echo "skipped: ${skipped[*]}"
      fi
    fi
    if [[ ${#chosen[@]} -eq 0 ]]; then
      echo "FAIL judge $lesson"
      echo "expected: at least $min trees at or after ${cutoff:-the first run}"
      echo "received: 0"
      exit 1
    fi
    mapfile -t stamps < <(printf '%s\n' "${chosen[@]}" | sort -u)
    if [[ ${#stamps[@]} -lt "$min" ]]; then
      echo "FAIL judge $lesson"
      echo "expected: at least $min trees at or after ${cutoff:-the first run}"
      echo "received: ${#stamps[@]} (${stamps[*]})"
      exit 1
    fi

    stamp=$(date +%Y-%m-%d-%H-%M-%S)
    dest="$results/judgements/$stamp.md"
    mkdir -p "$(dirname "$dest")"
    mapfile -t given < <("$root/scripts/judge-given" "$root/workshop/material" "$lesson" --paths)
    {
      echo "# Judgement $lesson"
      echo
      echo "trees:"
      for s in "${stamps[@]}"; do
        echo "- $s"
      done
      echo
      echo "given:"
      for path in "${given[@]}"; do
        echo "- $path"
      done
      echo
      echo "## Material"
    } > "$dest"

    prompt=$(mktemp)
    log=$(mktemp)
    trap 'rm -f "$prompt" "$log"' EXIT
    {
      echo "# Material"
    } > "$prompt"

    # Expected files that are not markdown (a hook, a justfile, build.sbt, a report) are
    # copied into the stamp too; show the small ones so a claim about them is decidable.
    extra_files() {
      local tree="$1" rel size
      for rel in ${expected[@]+"${expected[@]}"}; do
        [[ "$rel" == *.md || ! -f "$tree/$rel" ]] && continue
        size=$(wc -c < "$tree/$rel" | tr -d ' ')
        echo
        echo "### $rel"
        echo
        if [[ "$size" -gt 20000 ]]; then
          echo "(file is $size bytes; not shown)"
          continue
        fi
        echo '````'
        cat "$tree/$rel"
        echo '````'
      done
    }

    for s in "${stamps[@]}"; do
      # The spec is what the lesson is expected to produce, not every markdown file
      # a full-tree stamp carries. A lesson that expects no .md falls to the final reply.
      mapfile -t expected < <("$root/scripts/lesson-forks" paths "$lesson" 2>/dev/null || true)
      specs=()
      for rel in ${expected[@]+"${expected[@]}"}; do
        if [[ "$rel" == *.md && -f "$results/$s/$rel" ]]; then
          specs+=("$results/$s/$rel")
        fi
      done
      {
        echo
        echo "## $s"
      } >> "$dest"
      {
        echo
        echo "## $s"
      } >> "$prompt"
      session="$results/$s/session.jsonl"
      if [[ -f "$session" ]]; then
        echo "measures: $($root/scripts/lesson-status measures "$session")" >> "$prompt"
      fi
      extra_files "$results/$s" | tee -a "$dest" >> "$prompt"
      if [[ ${#specs[@]} -eq 0 ]]; then
        session="$results/$s/session.jsonl"
        [[ -f "$session" ]] || { echo "no spec and no session in $s" >&2; exit 1; }
        reply=$(jq -Rrn '[inputs | fromjson? | select(type=="object" and .type=="result" and .subtype=="success")] | last | .result // empty' "$session")
        [[ -n "$reply" ]] || { echo "no reply in $s" >&2; exit 1; }
        {
          echo
          echo "spec: absent"
          echo
          echo "### final reply"
          echo
          printf '%s\n' "$reply"
        } | tee -a "$dest" >> "$prompt"
        continue
      fi
      for spec in "${specs[@]}"; do
        rel=${spec#"$results/$s/"}
        headings=$(awk '/^#{1,6} / { print }' "$spec")
        {
          echo
          echo "### $rel"
          echo
          echo '```'
          if [[ -n "$headings" ]]; then
            printf '%s\n' "$headings"
          else
            echo "(no headings)"
          fi
          echo '```'
        } >> "$dest"
        {
          echo
          echo "### $rel"
          echo
          echo "#### Headings"
          echo
          echo '```'
          if [[ -n "$headings" ]]; then
            printf '%s\n' "$headings"
          else
            echo "(no headings)"
          fi
          echo '```'
          echo
          echo "#### Spec"
          echo
          cat "$spec"
        } >> "$prompt"
      done
    done

    "$root/scripts/judge-given" "$root/workshop/material" "$lesson" >> "$prompt"

    home="$root/.claude-home"
    mkdir -p "$home"
    [[ -f "$home/.claude.json" ]] || echo '{"theme":"auto"}' > "$home/.claude.json"
    jq '.hasCompletedOnboarding = true' "$home/.claude.json" > "$home/.claude.json.tmp"
    mv "$home/.claude.json.tmp" "$home/.claude.json"

    echo "judging $lesson -> $dest"
    # cwd is workshop/; allow results stamps so the judge can Read trees (v13.M4).
    # develop/ stays outside the grant. Default tools stay enabled.
    set +e
    jq -nc --arg content "$(cat "$prompt")" '{type:"user",message:{role:"user",content:$content}}' \
      | ( cd "$root/workshop" && CLAUDE_CONFIG_DIR="$home" nono run --no-diagnostics -p "{{profile}}" --allow "$home" --allow "$results" -- \
          claude -p \
            --input-format stream-json \
            --output-format stream-json \
            --verbose \
            --permission-mode acceptEdits \
            --permission-prompts none \
            --system-prompt-file "$judge" ) \
      | tee "$log"
    ps=("${PIPESTATUS[@]}")
    code=${ps[1]}
    set -e
    if [[ "$code" != 0 ]]; then
      echo "judge failed; claude exited $code" >&2
      exit 1
    fi

    answer=$(jq -Rrn '[inputs | fromjson? | select(type=="object" and .type=="result" and .subtype=="success")] | last | .result // empty' "$log")
    if [[ -z "$answer" ]]; then
      echo "judge returned no answer" >&2
      exit 1
    fi
    {
      echo
      echo "## Answer"
      echo
      printf '%s\n' "$answer"
    } >> "$dest"

    if grep -qx 'verdict: pass' <<< "$answer"; then
      echo "PASS judge $lesson"
      echo "expected: verdict: pass"
      echo "received: verdict: pass"
      echo "report: $dest"
    elif grep -qx 'verdict: fail' <<< "$answer"; then
      echo "FAIL judge $lesson"
      echo "expected: verdict: pass"
      echo "received: verdict: fail"
      echo "why:"
      printf '%s\n' "$answer"
      echo "report: $dest"
      exit 1
    else
      echo "FAIL judge $lesson"
      echo "expected: verdict: pass"
      echo "received: no verdict line"
      echo "why:"
      printf '%s\n' "$answer"
      echo "report: $dest"
      exit 1
    fi

# One line per lesson. Stamps before results/<lesson>/cutoff stay on disk and do not count.
# The line is the verdict plus interactions and length when a session log is in range.
summary:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    "$root/scripts/lesson-status" lines "$root/workshop/results"

# Prepare, run the participant once, judge, and print one status line.
# With no lesson, do that for every lesson and print a line after each.
# A lesson that did not work does not stop the rest.
# depth=N caps each fork. forks=N runs that many forks, one after another.
[positional-arguments]
validate *lessons:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    mapfile -t order < <("$root/scripts/lesson-order" "$root/workshop/JOURNEY.md")
    runnable() {
      for id in "${order[@]}"; do
        [[ "$id" == "$1" ]] && return 0
      done
      return 1
    }
    chosen=()
    depth=""
    forks=1
    if [[ $# -eq 0 ]]; then
      chosen=("${order[@]}")
    else
      for lesson in "$@"; do
        if [[ "$lesson" == max=* ]]; then
          echo "use depth=" >&2
          exit 1
        fi
        if [[ "$lesson" == depth=* ]]; then
          depth="${lesson#depth=}"
          [[ "$depth" =~ ^[0-9]+$ && "$depth" -ge 1 ]] || { echo "bad depth: $depth" >&2; exit 1; }
          continue
        fi
        if [[ "$lesson" == forks=* ]]; then
          forks="${lesson#forks=}"
          [[ "$forks" =~ ^[0-9]+$ && "$forks" -ge 1 ]] || { echo "bad forks: $forks" >&2; exit 1; }
          continue
        fi
        known=0
        for id in "${order[@]}"; do
          [[ "$id" == "$lesson" ]] && known=1
        done
        if [[ "$known" != 1 ]]; then
          echo "unknown lesson: $lesson" >&2
          echo "lessons: ${order[*]}" >&2
          exit 1
        fi
        chosen+=("$lesson")
      done
    fi
    status=0
    for lesson in "${chosen[@]}"; do
      if runnable "$lesson"; then
        results="$root/workshop/results/$lesson"
        mkdir -p "$results"
        printf '%s\n' "$(date +%Y-%m-%d-%H-%M-%S)" > "$results/cutoff"
        just prepare "$lesson"
        set +e
        if [[ "$forks" == 1 ]]; then
          if [[ -n "$depth" ]]; then
            just simulate "$lesson" prep=no "depth=$depth"
          else
            just simulate "$lesson" prep=no
          fi
        else
          prompt=$("$root/scripts/participant-session" section "$root/workshop/JOURNEY.md" "$lesson")
          sha=$(git -C "$root/develop" rev-parse HEAD)
          "$root/scripts/participant-session" install --from "$root/.claude/agents/participant.md" --work "$root/develop"
          mapfile -t fork_paths < <("$root/scripts/lesson-forks" paths "$lesson")
          fork_args=(
            "$root/scripts/lesson-forks" run
            --work "$root/develop"
            --results "$results"
            --forks "$forks"
            --prepared "$sha"
            --message "$prompt"
          )
          if [[ -n "$depth" ]]; then
            fork_args+=(--depth "$depth")
          fi
          for rel in "${fork_paths[@]}"; do
            fork_args+=(--expect "$rel")
          done
          fork_args+=(
            --
            env "CLAUDE_CONFIG_DIR=$root/develop/.claude-home"
            nono run --no-diagnostics -p "{{profile}}" --allow "{{cache}}" --
            claude -p
            --agent participant
            --input-format stream-json
            --output-format stream-json
            --verbose
            --permission-mode bypassPermissions
            --permission-prompts none
          )
          "${fork_args[@]}"
        fi
        min=$("$root/scripts/lesson-forks" judge-min "$forks")
        just judge "$lesson" "min=$min"
        set -e
      fi
      "$root/scripts/lesson-status" lines "$root/workshop/results" "$lesson" || status=1
      "$root/scripts/lesson-status" heading "$root/workshop/JOURNEY.md" "$root/workshop/results" "$lesson"
    done
    "$root/scripts/lesson-status" yaml "$root/workshop/results" "$root/workshop/results/status.yaml"
    exit "$status"

# Similar terms across the prompts, the expected observations, and the material.
term-drift:
    python3 scripts/term-drift "{{justfile_directory()}}/workshop/JOURNEY.md" "{{justfile_directory()}}/workshop/material" "{{justfile_directory()}}/workshop/term-drift-natural.txt" "{{justfile_directory()}}/workshop/term-drift-pinned.txt"

# Named ambiguities from past runs that must not come back. See SPEC.v10 M1.
ambiguity-check:
    python3 scripts/ambiguity-check "{{justfile_directory()}}/workshop/JOURNEY.md" "{{justfile_directory()}}/workshop/material" "{{justfile_directory()}}/workshop/known-ambiguities.txt"

# Fail when a session.jsonl Bash command matches workshop/session-bash-forbids.txt (v13.M2c–M2e).
session-bash-forbid session:
    python3 scripts/session-bash-forbid "{{justfile_directory()}}/workshop/session-bash-forbids.txt" "{{session}}"

# Distances between the fenced lesson prompts. See SPEC.v7 M1.
prompt-distance lesson="":
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    args=("$root/scripts/prompt-distance" "$root/workshop/JOURNEY.md")
    lesson="{{lesson}}"
    if [[ -n "$lesson" ]]; then
      args+=(--lesson "$lesson")
    fi
    "${args[@]}"

# Overwrite the committed baseline with the current board. A deliberate step;
# nothing else writes this file. See SPEC.v10 M2.
prompt-distance-freeze:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    "$root/scripts/prompt-distance" "$root/workshop/JOURNEY.md" | grep -v '^segment ' > "$root/workshop/prompt-distance-baseline.txt"

# Fail when a lesson's prompt has drifted past the threshold from its frozen
# baseline. Skipped by the pre-commit hook when no baseline is frozen yet.
prompt-drift-check:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    "$root/scripts/prompt-distance" "$root/workshop/JOURNEY.md" --check-baseline "$root/workshop/prompt-distance-baseline.txt"

# Distances between expected-observation bullets (v13.M5). Instructor-invoked; not a pre-commit gate yet.
observation-distance lesson="":
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    args=("$root/scripts/observation-distance" "$root/workshop/JOURNEY.md")
    lesson="{{lesson}}"
    if [[ -n "$lesson" ]]; then
      args+=(--lesson "$lesson")
    fi
    "${args[@]}"

observation-distance-freeze:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    "$root/scripts/observation-distance" "$root/workshop/JOURNEY.md" > "$root/workshop/observation-distance-baseline.txt"

observation-drift-check:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    "$root/scripts/observation-distance" "$root/workshop/JOURNEY.md" --check-baseline "$root/workshop/observation-distance-baseline.txt"

# Refresh *WORKTREE* summary blocks in JOURNEY.md (outer.v16.M1). Idempotent.
journey-worktrees:
    python3 "{{justfile_directory()}}/scripts/journey-worktrees" --write

# Refresh each lesson's last: mark, show the M1 board, and report smoothness.
instruct lesson="":
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    args=("$root/scripts/instruct" "$root/workshop/JOURNEY.md" "$root/workshop/results")
    lesson="{{lesson}}"
    if [[ -n "$lesson" ]]; then
      args+=(--lesson "$lesson")
    fi
    "${args[@]}"

# ATX heading TOC / outline compare (Scala via scala-cli). Args forwarded as-is.
#   just tocmd docs/specs/SPEC.v17-presentation-and-journey-bridge.md
#   just tocmd -- --compare a.md b.md
tocmd *args:
    "{{justfile_directory()}}/scripts/tocmd" {{args}}

# Software slide deck (presentation/). Ported from agentic-engineering-workshop @ e5a0ee9.
# First time (or after lockfile change): just present-install
# Default rebuilds (bridge → build-deck) then serves .build/:
#   just present
#   just present deck=software-part2
# Skip rebuild when .build/ is already fresh:
#   just present rebuild=no
# Assemble without serving: just present-build
present-install:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}/presentation"
    npm ci

present deck="software-part1" rebuild="yes":
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    deck="{{deck}}"
    rebuild="{{rebuild}}"
    case "$rebuild" in
      yes|no) ;;
      *)
        echo "rebuild must be yes or no, got: $rebuild" >&2
        exit 1
        ;;
    esac
    cd "$root/presentation"
    if [[ ! -d node_modules ]]; then
      echo "missing presentation/node_modules; run: just present-install" >&2
      exit 1
    fi
    PRESENT_REBUILD="$rebuild" exec ./.bin/present "$deck"

present-build:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    cd "$root/presentation"
    if [[ ! -d node_modules ]]; then
      echo "missing presentation/node_modules; run: just present-install" >&2
      exit 1
    fi
    exec ./.bin/build-deck

present-stop:
    "{{justfile_directory()}}/presentation/.bin/stop"

present-check:
    #!/usr/bin/env bash
    set -euo pipefail
    root="{{justfile_directory()}}"
    cd "$root/presentation"
    if [[ ! -d node_modules ]]; then
      echo "missing presentation/node_modules; run: just present-install" >&2
      exit 1
    fi
    exec ./.bin/check

# Mechanical deck/bridge gate (v17.M3). Narrative pass: /deck-smoothness skill.
present-check-smooth:
    python3 "{{justfile_directory()}}/scripts/presentation-check"

# Drawing companions (outer.v18): sidecar .md next to each docs/drawings/*.excalidraw
#   just drawing-companions-status     # board (exit 0)
#   just drawing-companions-check      # board; exit 1 if missing/stale
#   just drawing-companions-generate   # stub companions where missing only
drawing-companions-status:
    "{{justfile_directory()}}/scripts/drawing-companions" status "{{justfile_directory()}}/docs/drawings"

drawing-companions-check:
    "{{justfile_directory()}}/scripts/drawing-companions" status --fail "{{justfile_directory()}}/docs/drawings"

drawing-companions-generate:
    "{{justfile_directory()}}/scripts/drawing-companions" generate-missing "{{justfile_directory()}}/docs/drawings"

# once per machine, for nono-strict.json
@claude-login:
    #!/usr/bin/env bash
    set -euo pipefail
    claude setup-token
    read -rsp "Paste the token printed above (sk-ant-oat01-...): " token; echo
    [[ $token == sk-ant-oat01-* ]] || { echo "not a Claude OAuth token, nothing stored" >&2; exit 1; }
    if [[ {{os()}} == macos ]]; then
      security add-generic-password -U -s nono -a claude_code_oauth_token -w "$token"
    else
      printf %s "$token" | secret-tool store --label="nono: claude_code_oauth_token" service nono username claude_code_oauth_token target default
    fi
    echo "stored in the OS keyring as nono/claude_code_oauth_token"
