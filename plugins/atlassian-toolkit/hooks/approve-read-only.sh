#!/bin/bash
# PreToolUse hook for the Atlassian MCP server: auto-approve read-only tools. The filtering
# lives entirely in the hooks.json matcher — an explicit allowlist of read tool names behind
# this plugin's own prefix — so this script only ever runs for those tools and needs no input
# parsing (no jq). New tools Atlassian adds are not in the allowlist and keep prompting.
echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "atlassian-toolkit read-only Atlassian tool"}}'
exit 0
