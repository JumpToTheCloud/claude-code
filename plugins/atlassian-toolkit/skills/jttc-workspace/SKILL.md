---
name: jttc-workspace
description: Reference map of the Jump to the Cloud (JTTC) workspace in Atlassian - the Jira project JTTC (workflow, statuses, issue types, custom fields, boards, components) and the Confluence space JTTC (page tree, templates, Definition of Ready, Definition of Done, naming, labels), with the IDs needed to read and write them. Use whenever the user mentions the JTTC project or space, the Definition of Ready or Definition of Done, a PRD / Technical Plan / Consistency Analysis / ADR / Runbook / Component template, where a document should live, how to name or label a page, the workflow statuses (Backlog, In refinement, Refined, Ready, In Progress, In Review, Done), sub-task types, the Mode / Size / Risk / Business Value fields, or when creating or transitioning Jira issues and Confluence pages in this workspace. Read it before any Jira or Confluence write that touches JTTC.
---

# JTTC workspace

Where everything lives in the Jump to the Cloud Atlassian workspace, and the rules that
apply to it. This skill is a **map**, not the source of truth: the Definition of Ready, the
Definition of Done and the templates live in Confluence and are edited there.

**Rule 1 — know which copy is the source.** The Definition of Ready, the Definition of Done and
the issue-body templates are kept **in the plugin** (`jira-transition-issue/references/` and the
`assets/` of each `jira-create-*` skill). The Confluence pages for them are generated mirrors for
people to read: never edit them by hand and do not read them to apply a gate. The PRD,
Technical Plan, Consistency Analysis, ADR and Runbook templates are in
`confluence-create-doc/assets/`; only the Component Template tree still lives in Confluence and
is copied by ID.

**Rule 2 — IDs here are stable, but verify when something fails.** A 404 or "not found"
means an ID changed: look it up again, do not guess.

Site: `jumptothecloud.atlassian.net`
Cloud ID: `41be3e35-e509-4a4c-93e1-5460248e11ab`

## Which reference to read

| The task involves… | Read |
|---|---|
| Creating, editing, searching or transitioning Jira issues in JTTC; statuses, issue types, custom fields, boards, components | `references/jira-project.md` |
| Creating or finding a Confluence page: PRD, plan, analysis, ADR, runbook, component page; naming; labels; templates | `references/confluence-space.md` |
| Whether an item is ready to start or done: the two gates, per-type shortcuts, Done checklists | `references/quality-gates.md`, which points to the criteria kept in `jira-transition-issue` |

Most tasks need two of them. Creating a PRD, for example, needs `confluence-space.md` for the
template and the naming, and `jira-project.md` if Epics or Stories are created from it.

## The model in one screen

- **One Jira project (`JTTC`) for the whole platform.** One **Component per repository**.
  Component is **required** when creating an issue.
- **One workflow for every issue type:**
  `Backlog → In refinement → Refined → Ready → In Progress → In Review → Done`.
  Any status can move to any other, so shortcuts are allowed (a small Task goes
  `Backlog → Ready`). The gates in `quality-gates.md` still apply.
- **Done = merged into `main`**, feature flag off if needed. Releases live in GitHub, not Jira.
- **Sub-tasks have five types**, matching what `iteration-plan` produces: Development,
  Automation, Analysis (spike), Architecture Design, Documentation. AFK/HITL is the **Mode**
  field, not a label. `tdd` is a label.
- **One Confluence space (`JTTC`).** The type of document decides where it lives, the
  component is its branch of the tree, and the status is a label. Nothing is stored twice.
- **A PRD usually leads to one Epic**, linked both ways. This is a default, not a rule.

## Gotchas that have already cost time

1. **Sub-tasks are created in `Backlog`.** The workflow has a single initial status. The
   iteration plan must move them to `Ready` afterwards. Never assume they start in `Ready`.
2. **Confluence titles are unique across the whole space.** Component pages are therefore
   prefixed with the component name (`<component> — Decisions`).
3. **`In refinement` has a lowercase "r".** It reuses a pre-existing global status. Match it
   exactly in JQL and transitions.
4. **Do not delete the `JTTC: …` schemes** (workflow scheme 10007, issue type scheme 10147,
   issue type screen scheme 10004 and their screens). They look like leftovers but CDKX,
   ORKAI, DH, ALZCL, IOTF and others still use them. Only the schemes named
   `JTTC Unified …` and `JTTC …` (no colon) belong to this project.
5. **The Default Field Configuration is shared by every project.** Never mark a field required
   there. JTTC has its own `JTTC Field Configuration`, managed only from the Jira UI (the REST
   API cannot create or edit it).
6. **Do not run `acli jira board delete`.** It waits for an interactive confirmation and hangs.
   Use the REST agile API instead.
7. **The Development board is Scrum.** Without a sprint, `Ready` items show in its Backlog
   tab, not in the columns.
8. **The legacy skills (`refine-story`, `iteration-plan`, `user-story` for Jira) still assume
   the old CDKX workflow** (`To Do`, `Ready for Implementation`, `Análisis`). Do not apply
   their hardcoded status names to JTTC; use the statuses in `jira-project.md`.

9. **Nothing in the plugin can delete a Jira issue.** The MCP has no delete operation and the
   `atlassian-operator` agent has no destructive tools. Remove test data with
   `acli jira workitem delete --key JTTC-n --yes` (explicit keys only, never a JQL), after the
   user says so.

10. **The MCP does not return `timetracking`.** `getJiraIssue` omits the estimate even when it is
    stored. To verify it use the REST API (`GET /rest/api/3/issue/<key>?fields=timetracking`)
    or the Jira UI. A create call that accepts `timetracking` without an error means it was
    saved, provided `timetracking` is on `JTTC Default Screen` (`jira_template.py apply` adds
    it).
11. **Remote links are not in `getJiraIssue` either.** List them with `executeRead` and the
    operation `listJiraIssueRemoteIssueLinks`.

12. **`editJiraIssue` has no `description` argument.** Pass the description inside
    `fields: {"description": ...}`. A top-level `description` is dropped silently and the call
    still reports success, so always read the issue back.
13. **`getConfluenceContent` does not return labels.** To check a label use `searchConfluence`
    with `cql: id = <pageId> AND label = "<label>"`.

14. **Story Points live on Story, Task and Bug only** (fixed 2026-11-01 in the Jira UI; before
    that only Story had it). They are deliberately not on the sub-tasks (estimated in hours with
    `timetracking`) nor on the Epic (its size is the sum of its children). Verify with
    `GET /rest/api/3/issue/createmeta/JTTC/issuetypes/<typeId>` and look for `customfield_10041`.

## Creating things — quick recipes

**A Jira issue.** Required at creation: project, issue type, summary, **components**; a
sub-task also needs `parent`. Set Story Points, Size, Business Value, Risk during refinement,
and Mode on sub-tasks. Field IDs and allowed values are in `jira-project.md`. Look the option
IDs up at runtime; do not hardcode them.

**A Confluence page.** Copy the matching template under the right parent, rename it with the
title pattern, add the type label (the state is a status lozenge in its summary table, not a label). Details in `confluence-space.md`.

**A component.** Create the Jira Component first, then copy the `Component Template` tree
under `Components`, replacing `Component Template` with the component name in the titles.
After the copy, list the descendants and confirm all five children came with it: copying the
children was not verified.

## Maintaining this skill

The IDs and the model in these files describe the workspace as set up on 2026-10-31. When the
workspace changes (new status, new field, moved page), update the reference in the same piece
of work. The script that builds and syncs the Jira side ships with this skill:
`scripts/jira_template.py` (relative to this skill's directory). It is described in
`references/jira-project.md`.
