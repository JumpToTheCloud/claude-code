---
name: jira-create-task
description: Create one or more Tasks in the Jira project JTTC - technical work with no user story - from a structured input (summary, outcome, done-when, component, parent Epic, source). Fills the Task template, blocks creation when an entry-level field is missing, leaves refinement sections marked `Pending refinement`, links the source as a remote link, skips duplicates and returns the new keys. Use when a technical task must be created in JTTC, or the user says "create a task", "crear una tarea", "add a technical task to epic JTTC-N". Not for user-visible value (that is a Story) and not for work inside a Story (that is a sub-task).
---

# jira-create-task

Creates Tasks in JTTC. The caller supplies the content; this skill checks it, fits it into the
template and writes it. Site `jumptothecloud.atlassian.net`, cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. IDs and gotchas: `jttc-workspace`.

A Task is technical work that has no user story. If it delivers user-visible value it is a
Story; if it is a step inside a Story or Bug it is a sub-task. A Task is at most 3 Story Points;
bigger work is a Story.

## Input

For each Task:

| Input | Required | Notes |
|---|---|---|
| `summary` | yes | Outcome in plain words, at most 100 characters |
| `component` | yes | Exactly one Jira Component name |
| `parent` | yes | Epic key |
| `outcome` | yes | What exists or works afterwards |
| `done_when` | yes | Two to five verifiable lines |
| `source_url` or `no_source_reason` | yes, exactly one | Confluence page that justifies it (PRD, ADR), or the reason there is none |
| `labels` | no | |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   **Component:** call `executeRead` with `name: listJiraProjectComponents`, `inputs: {projectIdOrKey: "JTTC"}` once per batch and keep the names. A `component` that is not in the list is a validation error. Do not assume it exists because a create call accepted it.
   **Parent:** call `getJiraIssue` (`view: full`: the default view omits the issue type) for every distinct `parent` key. It must exist and be an Epic.

1. **Validate every Task before creating any.** If one fails, create nothing from the batch and
   return the problems per Task. Never invent a missing value.
   - required inputs present, exactly one of `source_url` and `no_source_reason`;
   - `summary` is 100 characters or fewer; `parent` exists and is an Epic; `component` exists;
   - `done_when` has two to five lines and each one can be checked (no "works", "robust").
2. **Check for duplicates.** `searchJiraIssuesUsingJql`:
   `project = JTTC AND issuetype = Task AND parent = <parent> AND summary ~ "<key words>"`.
   On a clear match do not create; report `duplicate` with the existing key.
3. **Build the description** from the body between the `body` markers in
   `assets/task-template.md`. Write the `Source` section only when `no_source_reason` was
   given; otherwise omit it. Leave `Files to touch` as `Pending refinement`. Do not copy
   "Guidance (not posted)".
4. **Create** with `createJiraIssue`: `cloudId`, `projectKey: JTTC`, `issueType: Task`,
   `summary`, `description` (markdown), `parent`, `labels`,
   `additional_fields: {"components": [{"name": "<component>"}]}`. On rejection use the
   `repairHint` and retry once.
5. **Link the source.** If `source_url` was given, `executeWrite` with
   `name: createJiraIssueRemoteIssueLink`, `inputs: {issueIdOrKey: <key>, url, title: "Source"}`,
   `cloudId` at top level. If it fails, keep the Task and report `created, link failed`.
6. **Do not set** Mode, Story Points or any estimate, and do not transition. The Task stays in
   `Backlog` (a small, obvious Task can go straight to `Ready` later, through
   `jira-transition-issue`).

## Output

| summary | key | url | status |
|---|---|---|---|
| ... | JTTC-n | https://jumptothecloud.atlassian.net/browse/JTTC-n | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: components listed; parents read (JTTC-n, Epic); duplicates searched; source links created`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create a Task without a parent Epic or a Component.
- Fill a refinement section with a guess.
- Create the same Task twice. If a call times out, search before retrying.
