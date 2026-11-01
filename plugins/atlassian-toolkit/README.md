# atlassian-toolkit

Atlassian Cloud integration for Claude Code. Installing this plugin preconfigures the official, Atlassian-hosted **Rovo MCP server** (`https://mcp.atlassian.com/v2/mcp`), so Claude can read and write Jira issues and Confluence pages. Nothing to install locally — no Node, Python or Docker — and no API tokens: authentication is OAuth, with your own Atlassian permissions.

## What's included

| Component | Purpose |
|---|---|
| `.mcp.json` | Registers the remote Atlassian MCP server (`atlassian`, HTTP). |
| `hooks/` | Auto-approves the server's **read-only** tools (get/search/list, `discover` and `executeRead`). Non-destructive writes (create, edit, transition, comment, `executeWrite`) are approved only when a subagent issues them, because the content was already approved in the main session; from the main session they ask. `executeDestructive` always asks. |
| `agents/atlassian-operator` | Isolated subagent that writes to Jira so the main session stays clean. The caller decides and shows the content; the agent validates it, creates it and returns the keys. Pass batches. It cannot delete anything. |
| `skills/jira-create-story` | Creates Stories in JTTC from a structured input, using the Story template in its `assets/`. Blocks on missing entry-level fields, leaves refinement sections as `Pending refinement`, skips duplicates. |
| `skills/jira-create-{epic,task,bug,subtask}` | Same for Epics, Tasks, Bugs and sub-tasks (five types, estimate up to 8 h, Mode AFK or HITL). |
| `skills/jira-link-issues` | Blocks / relates / remote links, with a cycle check and no duplicates. |
| `skills/jira-update-issue` | Story Points, Size, Business Value, Risk, Mode, labels, Flagged, estimate, description sections and comments. Never changes the status. |
| `skills/jira-transition-issue` | Moves issues and enforces the Definition of Ready (two gates) and Definition of Done by reading the live Confluence pages. A failed gate leaves the issue where it is. |
| `skills/confluence-create-doc` | Creates a PRD, Technical Plan, Consistency Analysis, ADR or Runbook page from the template kept in its `assets/`: finds the parent, builds and checks the title, fills the summary table and sections and creates the page in one call, with the type label. |
| `skills/confluence-update-doc` | Maintains those pages with targeted edits: summary rows, sections, status changes (the status lozenge in the summary table) and retire (`SUPERSEDED`, moves under Archive). Never deletes a page and cannot remove a label. |
| `skills/confluence-create-component` | Bootstraps the Confluence side of a new component: the component page and its five children (Overview, PRDs, Decisions, Design, Runbooks) with the Overview table filled. The Jira Component must exist first. |
| `skills/confluence-sync-templates` | Maintenance skill, run only when asked. Regenerates the read-only Confluence mirrors of the issue and document templates, the Component Template tree, the Definition of Ready and Done, the Templates index and "How this space works", each with a "generated, do not edit" notice. It always previews first, with a summary of what changes on every page, and writes only after the maintainer confirms. |
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
