#!/usr/bin/env bash
# nono session_hooks.before: create Claude paths so Landlock/Seatbelt grants attach.
# Host privileges, before the sandbox boundary goes up.
set -euo pipefail

mkdir -p \
  "$HOME/.claude" \
  "$HOME/.cache/claude" \
  "$HOME/.local/state/claude/locks"

if [ -n "${XDG_RUNTIME_DIR:-}" ]; then
  mkdir -m 700 -p "$XDG_RUNTIME_DIR/cc-socks"
fi
