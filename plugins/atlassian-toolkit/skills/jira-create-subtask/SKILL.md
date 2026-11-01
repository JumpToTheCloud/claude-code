---
name: jira-create-subtask
description: Create one or more sub-tasks in the Jira project JTTC under a Story, Task or Bug, as one of five types - Development, Automation, Analysis, Architecture Design, Documentation. Each sub-task is self-contained (goal, context, exact files, steps, acceptance criteria covered, tests, estimate in hours up to 8, Mode AFK or HITL, tdd label). Validates the whole set, copies the Component from the parent, creates in Backlog and returns the keys. Use when the iteration plan breaks a refined item into technical sub-tasks, or the user says "create sub-tasks", "crear subtareas", "split JTTC-N into tasks". Dependencies between sub-tasks and the move to Ready are done by jira-link-issues and jira-transition-issue.
---

# jira-create-subtask

Creates sub-tasks in JTTC. The caller (the iteration plan) reads the codebase and writes the
content; this skill checks it, fits it into the template and writes it. Site
`jumptothecloud.atlassian.net`, cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`, project
`JTTC`. IDs and gotchas: `jttc-workspace`.

A sub-task is self-contained: a person or an agent can start by reading only it.

## Input

For each sub-task:

| Input | Required | Notes |
|---|---|---|
| `type` | yes | `Development`, `Automation`, `Analysis`, `Architecture Design` or `Documentation` |
| `summary` | yes | The work in plain words, at most 100 characters |
| `parent` | yes | Story, Task or Bug key. Never an Epic or another sub-task |
| `goal` | yes | |
| `context` | yes | Minimal context |
| `files` | yes | Exact paths and what changes in each |
| `steps` | yes | Numbered and concrete, with signatures |
| `acceptance_criteria` | yes | IDs and text taken from the parent |
| `tests` | yes | Tests to write and their level. `N/A: <reason>` allowed for `Documentation` and `Analysis` |
| `estimate_hours` | yes | Ideal hours, at most 8 |
| `mode` | yes | `AFK` or `HITL` |
| `tdd` | no | `true` adds the `tdd` label |
| `blocked_by` | no | Not applied here, see Steps |

The Component is **not** an input: it is read from the parent.

## Steps

0. **Mandatory reads. Do them first, even when the input looks complete.** Skipping one is a
   failure of the whole run, not a shortcut. Never take the Component from the input: it comes
   from the parent.
1. **Read each distinct parent** with `getJiraIssue` (`view: full`: the default view omits the issue type). Check it is a Story, Task or Bug (not an
   Epic or a sub-task) and take its Component.
2. **Validate every sub-task before creating any.** If one fails, create nothing from the batch
   and return the problems per sub-task. Never invent a missing value.
   - required inputs present and non-empty;
   - `estimate_hours` is a number and at most 8 (more means the work must be split);
   - `Architecture Design` has `mode: HITL`;
   - `tdd` is not set on `Automation`, `Architecture Design`, `Analysis` or `Documentation`,
     and an unit-test sub-task is never created apart from the `Development` one it belongs to;
   - `files` lists real file paths from the repository root, each with what changes in it. A
     directory, a module name or "the relevant files" is not a path. **Every test named in
     `tests` has its own file path in `files`** (the `Development` unit test and the
     `Automation` test included); when `tests` is `N/A: <reason>` this check does not apply.
     For `Analysis`, `Architecture Design` and `Documentation`, `files` names the path or page
     where the output is written.
3. **Check for duplicates.** `searchJiraIssuesUsingJql`:
   `project = JTTC AND parent = <parent> AND issuetype = "<type>" AND summary ~ "<key words>"`.
   On a clear match do not create; report `duplicate` with the existing key.
4. **Build the description** from the body between the `body` markers in
   `assets/subtask-template.md`. Do not copy "Guidance (not posted)".
5. **Create** with `createJiraIssue`: `cloudId`, `projectKey: JTTC`, `issueType: <type>`,
   `summary`, `description` (markdown), `parent`, `labels` (`["tdd"]` or none),
   `additional_fields: {"components": [{"name": "<parent's component>"}], "Mode": "<mode>",
   "timetracking": {"originalEstimate": "<n>h"}}`. If `Mode` is rejected, look up the option ID
   (`GET /rest/api/3/field/customfield_10231/context`, then `/option`) as `jttc-workspace`
   says and retry with the ID. On any other rejection use the `repairHint` and retry once. If
   `timetracking` is not on the screen, report `created, estimate field not set`: the estimate
   and the Mode live only in their fields, never repeated in the description.
6. **Do not transition and do not link.** Sub-tasks are born in `Backlog`: the workflow has a
   single initial status. If `blocked_by` was given, create the sub-task anyway and report
   `created, blocked_by not applied` so the caller sends it to `jira-link-issues`.

## Output

| summary | type | key | url | status |
|---|---|---|---|---|
| ... | Development | JTTC-n | https://jumptothecloud.atlassian.net/browse/JTTC-n | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: parents read (JTTC-n, Story); component copied from parent; validated; duplicates searched`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create a sub-task under an Epic, or without a parent.
- Accept more than 8 hours: it must be split.
- Create a generic `Sub-task`: JTTC has none, every sub-task has one of the five types.
- Create the same sub-task twice. If a call times out, search before retrying.
