#!/usr/bin/env bash
# UserPromptSubmit hook: append every prompt to docs/PROMPTS.md.
# Reads the hook's JSON on stdin; needs jq.
set -euo pipefail

LOG_FILE="$CLAUDE_PROJECT_DIR/docs/PROMPTS.md"

input=$(cat)
prompt=$(jq -r '.prompt' <<<"$input")
session=$(jq -r '.session_id' <<<"$input" | cut -c1-8)
stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

[[ -f "$LOG_FILE" ]] || printf '# Prompts\n\nAppend-only, written by `.claude/hooks/log-prompt.sh`. Do not edit past entries.\n' > "$LOG_FILE"

{
  printf '\n## %s · %s\n\n' "$stamp" "$session"
  printf '```text\n%s\n```\n' "$prompt"
} >> "$LOG_FILE"
