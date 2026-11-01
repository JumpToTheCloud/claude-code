#!/bin/bash
# PreToolUse hook for the Atlassian MCP server: auto-approve non-destructive WRITES, but only
# when the call comes from a subagent (the atlassian-operator agent). The user approves the
# content in the main session before delegating, so the agent must not prompt again. Calls from
# the main session produce no output here and keep the normal permission prompt.
#
# The matcher in hooks.json lists the write tools; executeDestructive is deliberately absent.
# A subagent call carries "agent_id" in the hook input. If a Claude Code version names it
# differently the writes simply keep prompting (safe failure), they are never approved by mistake.
input=$(cat)
if printf '%s' "$input" | grep -q '"agent_id"'; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "atlassian-toolkit write issued by the atlassian-operator subagent after the user approved the content"}}'
fi
exit 0
