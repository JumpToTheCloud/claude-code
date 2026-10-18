#!/bin/bash
# PreToolUse hook for the Skill tool: auto-approve invoking any skill that belongs to this
# plugin (software-toolkit), since each of those skills already scopes its own tool access
# via allowed-tools/permissionMode in its own SKILL.md — asking permission a second time just
# to invoke the skill is redundant friction. Skills from other plugins are left untouched
# (exit 0, no output) so the normal permission flow decides.
set -euo pipefail

input=$(cat)
skill=$(echo "$input" | jq -r '.tool_input.skill // ""')

if [[ "$skill" == software-toolkit:* ]]; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "software-toolkit skill, self-scoped via its own allowed-tools"}}'
fi

exit 0
