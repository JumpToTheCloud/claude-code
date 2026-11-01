---
name: jira-create-epic
description: Create one or more Epics in the Jira project JTTC from a structured input (summary, expected outcome, out of scope, success criteria, component, PRD link). Fills the Epic template, blocks creation when a required field is missing, links the PRD and related ADRs as remote links, skips duplicates and returns the new keys. Use whenever an Epic must be created in JTTC - usually one per PRD - or when the user says "create an epic", "crear una epic", "epic for this PRD". An Epic has no refinement gate: it is complete at creation.
---

# jira-create-epic

Creates Epics in JTTC. The caller supplies the content; this skill checks it, fits it into the
template and writes it. Site `jumptothecloud.atlassian.net`, cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. IDs and gotchas: `jttc-workspace`.

## Input

For each Epic:

| Input | Required | Notes |
|---|---|---|
| `summary` | yes | The outcome it delivers, at most 100 characters |
| `component` | yes | Exactly one Jira Component name |
| `outcome` | yes | Expected outcome, in plain words |
| `out_of_scope` | yes | At least one bullet |
| `success_criteria` | yes | At least one, keeping the PRD's `SC-n` numbering, each measurable |
| `prd_url` or `no_prd_reason` | yes, exactly one | The PRD's Confluence page URL, or the reason there is none |
| `adr_urls` | no | Confluence URLs of related ADRs |
| `scope` | no | Bullets |
| `labels`, `priority` | no | |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   **Component:** call `executeRead` with `name: listJiraProjectComponents`, `inputs: {projectIdOrKey: "JTTC"}` once per batch and keep the names. A `component` that is not in the list is a validation error. Do not assume it exists because a create call accepted it.

1. **Validate every Epic before creating any.** If one fails, create nothing from the batch and
   return the problems per Epic. Never invent a missing value.
   - required inputs present and non-empty, exactly one of `prd_url` and `no_prd_reason`;
   - `summary` states an outcome and is 100 characters or fewer;
   - `component` exists in the project;
   - every success criterion is measurable (no "fast", "robust", "better").
2. **Check for duplicates.** `searchJiraIssuesUsingJql`:
   `project = JTTC AND issuetype = Epic AND component = "<component>" AND summary ~ "<key words>"`.
   On a clear match do not create; report `duplicate` with the existing key.
3. **Build the description** from the body between the `body` markers in
   `assets/epic-template.md`. Write the `Source` section only when `no_prd_reason` was given;
   otherwise omit it. Do not copy "Guidance (not posted)".
4. **Create** with `createJiraIssue`: `cloudId`, `projectKey: JTTC`, `issueType: Epic`,
   `summary`, `description` (markdown), `labels`, `priority`,
   `additional_fields: {"components": [{"name": "<component>"}]}`. On rejection use the
   `repairHint` and retry once.
5. **Link the sources.** For `prd_url` and each of `adr_urls`, `executeWrite` with
   `name: createJiraIssueRemoteIssueLink`, `inputs: {issueIdOrKey, url, title}` (`PRD`, or the
   ADR page title), `cloudId` at top level. If a link fails, keep the Epic and report
   `created, link failed: <which>`.
6. Do not transition. The Epic stays in `Backlog`.

## Output

| summary | key | url | status |
|---|---|---|---|
| ... | JTTC-n | https://jumptothecloud.atlassian.net/browse/JTTC-n | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: components listed; duplicates searched; PRD and ADR links created`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create an Epic without a Component, an outcome, an out of scope or success criteria.
- Put the PRD or ADR links in the body; they are Jira links.
- Create the same Epic twice. If a call times out, search before retrying.
