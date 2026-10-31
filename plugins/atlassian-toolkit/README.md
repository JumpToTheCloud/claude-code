# atlassian-toolkit

Atlassian Cloud integration for Claude Code. Installing this plugin preconfigures the official, Atlassian-hosted **Rovo MCP server** (`https://mcp.atlassian.com/v2/mcp`), so Claude can read and write Jira issues and Confluence pages. Nothing to install locally — no Node, Python or Docker — and no API tokens: authentication is OAuth, with your own Atlassian permissions.

## What's included

| Component | Purpose |
|---|---|
| `.mcp.json` | Registers the remote Atlassian MCP server (`atlassian`, HTTP). |
| `hooks/` | Auto-approves the server's **read-only** tools (get/search/list, `discover` and `executeRead`). Tools that create, edit, transition or comment, plus `executeWrite` and `executeDestructive`, always ask for confirmation. |
| `skills/jttc-workspace` | Reference map of the Jump to the Cloud workspace: the Jira project `JTTC` (workflow, issue types, custom fields, boards, components) and the Confluence space `JTTC` (page tree, templates, naming, labels), plus the Definition of Ready and Definition of Done. Activates on its own when you work with them; the IDs it carries are specific to the `jumptothecloud.atlassian.net` site. |

### The `jttc-workspace` skill

It is a map, not the source of truth. The Definition of Ready, the Definition of Done and the templates live in Confluence and are edited there; the skill holds where they are, the model behind them and the gotchas, and tells Claude to read the live page before applying any of it.

| File | Contents |
|---|---|
| `SKILL.md` | Index, the model in one screen, known gotchas, quick recipes |
| `references/jira-project.md` | Workflow and status IDs, issue types, custom fields and allowed values, boards, filters, components |
| `references/confluence-space.md` | Page tree with IDs, where each document goes, naming, labels, summary tables, recipes |
| `references/quality-gates.md` | Summary of the two Definition of Ready gates and of the Definition of Done |

When the workspace changes (a new status, a moved page), update the matching reference in the same piece of work.

## First use

1. Install the plugin:

   ```shell
   /plugin install atlassian-toolkit@jumptothecloud-code-marketplace
   ```

2. Authenticate once: run `/mcp`, select `plugin:atlassian-toolkit:atlassian` and complete the OAuth login in the browser.
3. Check it works, e.g. ask Claude: *"list my Jira projects"*.

If the login fails, the Atlassian Rovo MCP server may be disabled or restricted for your organization — ask an Atlassian org admin to check it in admin.atlassian.com.

> If you previously added the Atlassian MCP server yourself (`claude mcp add … atlassian`), remove it (`claude mcp remove atlassian`) to avoid duplicated tools.

## Requirements

- An Atlassian **Cloud** site (Jira and/or Confluence). Server/Data Center is not supported by the remote MCP server.
