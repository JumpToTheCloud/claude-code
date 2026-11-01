---
name: jira-create-story
description: Create one or more Stories in the Jira project JTTC from a structured input (summary, user story, source, out of scope, initial acceptance criteria, component, parent Epic). Fills the Story template, blocks creation when an entry-level field is missing, leaves the refinement sections marked `Pending refinement`, skips duplicates and returns the new keys. Use whenever a Story must be created in JTTC - from a PRD, from prd-to-issues, or when the user says "create a story", "crear una historia", "add a user story to epic JTTC-N". Does not set Story Points, Size, Business Value or Risk (that is refinement) and does not move the issue out of Backlog.
---

# jira-create-story

Creates Stories in JTTC. It does the plumbing, not the thinking: the caller supplies the
content, this skill checks it, fits it into the template and writes it.

Read `jttc-workspace` (`references/jira-project.md`) for IDs when something fails. Site:
`jumptothecloud.atlassian.net`, cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`.

## Input

A list of one or more stories. For each:

| Input | Required | Notes |
|---|---|---|
| `summary` | yes | Outcome in plain words, at most 100 characters, no `Story:` prefix |
| `component` | yes | Exactly one Jira Component name |
| `parent` | yes | Epic key. A Story always belongs to an Epic |
| `user_story` | yes | `as_a`, `i_want`, `so_that` |
| `prd_url` or `no_prd_reason` | yes, exactly one | The PRD's Confluence page URL, or the reason there is no PRD |
| `requirements` | no | Requirement IDs the Story covers (`REQ-n`) |
| `out_of_scope` | yes | At least one bullet |
| `acceptance_criteria` | yes | At least one, each Given / When / Then |
| `labels` | no | |
| `priority` | no | |
| `extras` | no | Size, Story Points, Risk, Business Value. Ignored here: those are set at refinement |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   **Component:** call `executeRead` with `name: listJiraProjectComponents`, `inputs: {projectIdOrKey: "JTTC"}` once per batch and keep the names. A `component` that is not in the list is a validation error. Do not assume it exists because a create call accepted it.
   **Parent:** call `getJiraIssue` (`view: full`: the default view omits the issue type) for every distinct `parent` key. It must exist and be an Epic; do not trust the key as given.

1. **Validate every story before creating any.** If one fails a rule, create nothing from the
   batch and return the list of problems per story. Never invent a missing value.
   - all required inputs present and non-empty, with exactly one of `prd_url` and
     `no_prd_reason`;
   - `summary` states an outcome and is 100 characters or fewer;
   - `parent` exists and is an Epic; `component` exists in the project;
   - each acceptance criterion contains Given, When and Then.
2. **Check for duplicates.** `searchJiraIssuesUsingJql`:
   `project = JTTC AND issuetype = Story AND parent = <parent> AND summary ~ "<key words>"`.
   If a clear match exists, do not create; report it as `duplicate` with the existing key.
3. **Build the description** from the body between the `body` markers in
   `assets/story-template.md`. Fill the placeholders from the input. Leave every
   `Pending refinement` section exactly as the template has it. In "Context and source" write
   `No PRD` only when `no_prd_reason` was given and `Requirements covered` only when
   `requirements` was given; if neither applies, omit the whole section. Never write `N/A` or
   a guess. Do not repeat the PRD or the Epic in the body. Do not copy the template's
   "Guidance (not posted)" section.
4. **Create** with `createJiraIssue`: `cloudId`, `projectKey: JTTC`, `issueType: Story`,
   `summary`, `description` (markdown), `parent`, `labels`, `priority`, and
   `additional_fields: {"components": [{"name": "<component>"}]}`. If the call is rejected, use
   the `repairHint` and retry once.
   If `prd_url` was given, link it right after creating: `executeWrite` with
   `name: createJiraIssueRemoteIssueLink`, `inputs: {issueIdOrKey: <new key>, url: <prd_url>,
   title: "PRD"}`, `cloudId` at top level. The link is a new issue, so there is nothing to
   deduplicate. If the link fails, keep the Story and report `created, PRD link failed`.
5. **Do not set** Story Points, Size, Business Value or Risk, and do not transition. The Story
   stays in `Backlog`.
6. **Return** one row per story.

## Output

| summary | key | url | status |
|---|---|---|---|
| ... | JTTC-n | https://jumptothecloud.atlassian.net/browse/JTTC-n | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: components listed; parents read (JTTC-n, Epic); duplicates searched; PRD links created`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create a Story without a parent Epic or a Component.
- Fill a refinement section with a guess.
- Put Story Points, Size, Business Value or Risk on a new Story.
- Create the same Story twice. If a call times out, search before retrying.
