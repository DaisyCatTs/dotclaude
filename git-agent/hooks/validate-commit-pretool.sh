#!/usr/bin/env bash
#
# PreToolUse hook — redirect bare `git commit` / `git add` to git-agent.
#
# Background: Agent built-in commit flow (status -> diff -> add -> commit) takes
# priority over prompt instructions. Without this hook the agent runs the
# built-in flow instead of git-agent. This hook intercepts the Bash call and
# denies it with a message pointing at git-agent.
#
# Allowed exceptions:
#   `git add <path> && git-agent commit ...` chained in one command — scoped staging
#   for `git-agent commit --no-stage`.

set -uo pipefail

input=$(</dev/stdin)

# Fast path: zero forks for non-git commands
case "$input" in
  *git*) ;;
  *) exit 0 ;;
esac

# Extract the command via jq or grep fallback
if command -v jq >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || true)
else
  cmd=$(printf '%s' "$input" | grep -oE '"command"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"' | head -1 \
    | sed -E 's/.*"command"[[:space:]]*:[[:space:]]*"(.*)"/\1/' || true)
fi

[ -z "$cmd" ] && exit 0

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

# Command position anchor
POS=$'(^|[;&|\n])[[:space:]]*([A-Za-z_][A-Za-z_0-9]*=[^[:space:]]*[[:space:]]+)*'
END='([;&|[:space:]]|$)'

# Raw `git commit` check
RE_COMMIT="${POS}git[[:space:]]+commit${END}"
if [[ $cmd =~ $RE_COMMIT ]]; then
  deny "Use /git-agent:commit or /git-agent:commit-and-push instead of raw git commit. git-agent creates atomic AI commits with conventional messages."
fi

# `git add` without chained `git-agent commit`
RE_ADD="${POS}git[[:space:]]+add${END}"
RE_AGENT="${POS}git-agent[[:space:]]+commit${END}"
if [[ $cmd =~ $RE_ADD ]] && ! [[ $cmd =~ $RE_AGENT ]]; then
  deny "Use /git-agent:commit instead of raw git add. For folder-scoped staging, chain it with git-agent: git add <path> && git-agent commit --no-stage ..."
fi

exit 0
