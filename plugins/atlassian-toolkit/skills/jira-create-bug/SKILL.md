---
name: jira-create-bug
description: Create one or more Bugs in the Jira project JTTC from a structured input (summary, environment, affects version, steps to reproduce, expected vs actual, impact and severity, component). Fills the Bug template, blocks creation when reproduction or impact is missing, leaves root cause and acceptance criteria as `Pending refinement`, links the origin when known, skips duplicates and returns the new keys. Use when a defect must be filed in JTTC, or the user says "report a bug", "file a bug", "crear un bug", "this is a bug in JTTC-N". Bugs go through In refinement first to find the cause.
---

# jira-create-bug

Creates Bugs in JTTC. The caller supplies the content; this skill checks it, fits it into the
template and writes it. Site `jumptothecloud.atlassian.net`, cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. IDs and gotchas: `jttc-workspace`.

## Input

For each Bug:

| Input | Required | Notes |
|---|---|---|
| `summary` | yes | What fails, in plain words, at most 100 characters, no `Bug:` prefix |
| `component` | yes | Exactly one Jira Component name |
| `environment` | yes | Where it was observed (version, OS, environment, branch) |
| `affects_version` | yes | Version where it was observed |
| `steps_to_reproduce` | yes | Numbered, exact |
| `expected` and `actual` | yes | Both |
| `impact` and `severity` | yes | Who is affected and how badly |
| `priority` | no | Defaults to what the severity implies |
| `parent` | no | Epic key |
| `origin_issue` or `origin_url` | no | Jira key, or the URL of the PR or GitHub issue that introduced it |
| `labels` | no | |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   **Component:** call `executeRead` with `name: listJiraProjectComponents`, `inputs: {projectIdOrKey: "JTTC"}` once per batch and keep the names. A `component` that is not in the list is a validation error. Do not assume it exists because a create call accepted it.
   **Parent:** when `parent` is given, call `getJiraIssue` (`view: full`: the default view omits the issue type); it must exist and be an Epic.
   **Affects version:** there is no read to do. The create call in step 4 reports a version that
   does not exist, and step 4 says what to do then.


1. **Validate every Bug before creating any.** If one fails, create nothing from the batch and
   return the problems per Bug. Never invent a missing value, least of all a reproduction step.
   - required inputs present and non-empty;
   - `summary` is 100 characters or fewer, states what fails, no `Bug:` prefix;
   - `steps_to_reproduce` is a numbered list with at least two steps;
   - `component` exists; `parent`, when given, exists and is an Epic.
2. **Check for duplicates.** `searchJiraIssuesUsingJql`:
   `project = JTTC AND issuetype = Bug AND status != Done AND summary ~ "<key words>"`.
   On a clear match do not create; report `duplicate` with the existing key.
3. **Build the description** from the body between the `body` markers in
   `assets/bug-template.md`. Leave `Root cause` and `Acceptance criteria` as
   `Pending refinement`. Do not copy "Guidance (not posted)".
4. **Create** with `createJiraIssue`: `cloudId`, `projectKey: JTTC`, `issueType: Bug`,
   `summary`, `description` (markdown), `priority`, `parent`, `labels`,
   `additional_fields: {"components": [{"name": "<component>"}], "versions": [{"name":
   "<affects_version>"}]}`. If the version does not exist in the project, retry once without
   `versions`, keep the value in the Environment section as `Affects version: <value>` and report
   `created, affects version not set`. When no `affects_version` was given and the project has
   no versions, write `Affects version: none yet` in the Environment section. On any other rejection use the `repairHint` and retry once.
5. **Link the origin**, when given. For `origin_issue`, `executeWrite` with
   `name: createJiraIssueLink`, `inputs: {linkType: "Relates", inwardIssue: <bug key>,
   outwardIssue: <origin_issue>}`. For `origin_url`, `name: createJiraIssueRemoteIssueLink`,
   `inputs: {issueIdOrKey: <bug key>, url: <origin_url>, title: "Origin"}`. `cloudId` at top
   level. The origin is traceability only: never create a *blocks* link from here. If a link
   fails, keep the Bug and report `created, link failed`.
6. **Do not transition.** A Bug stays in `Backlog` and goes through `In refinement` first.

## Output

| summary | key | url | status |
|---|---|---|---|
| ... | JTTC-n | https://jumptothecloud.atlassian.net/browse/JTTC-n | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: components listed; parent read or none; duplicates searched; origin link created or none`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create a Bug without reproduction steps, expected vs actual, or impact.
- Guess a root cause or write acceptance criteria: both belong to refinement.
- Close or transition a Bug.
- Create the same Bug twice. If a call times out, search before retrying.
