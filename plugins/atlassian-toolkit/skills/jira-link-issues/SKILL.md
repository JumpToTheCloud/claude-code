---
name: jira-link-issues
description: Create links on Jira issues in the JTTC project - blocks / is blocked by between issues (with a cycle check), relates, and remote links to Confluence pages or URLs (a PRD or ADR on an Epic, a pull request on a Story). Skips links that already exist, rejects a batch that would create a dependency cycle and returns what was linked. Use whenever the iteration plan models the order of sub-tasks, a bug must point to its origin, a PRD page must be linked to an Epic, or the user says "link these issues", "X blocks Y", "enlazar", "add a dependency". Hierarchy (parent, Epic) is not a link and is not handled here.
---

# jira-link-issues

Creates links between Jira issues, and from issues to pages and URLs. The caller decides what
to link; this skill checks it, skips what already exists and writes the rest. Cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. Gotchas: `jttc-workspace`.

## Input

A list of links. Each is one of:

| Kind | Fields | Meaning |
|---|---|---|
| `blocks` | `blocker`, `blocked` (issue keys) | `blocker` must finish before `blocked` can start |
| `relates` | `a`, `b` (issue keys) | Traceability only, never a dependency |
| `remote` | `issue`, `url`, `title` | A Confluence page or any URL shown in the issue's Web links |

Parent and Epic are the `parent` field, set at creation. They are not links.

## Steps

0. **Mandatory reads. Do them first, even when the batch looks trivial.** For every issue in a
   `blocks` link call `getJiraIssue` with `view: evidence` to read its existing links. The
   cycle check is meaningless without them: "the issues are new" is not a reason to skip it.
1. **Validate every link before creating any.** If one fails, create nothing from the batch and
   return the problems per link.
   - both issues exist (`getJiraIssue`); no link from an issue to itself;
   - `url` is absolute `http` or `https`;
   - **No cycle.** For `blocks`, build the graph from the batch plus the existing *Blocks*
     links of every issue involved (`getJiraIssue` with `view: evidence`, `fields.issuelinks`)
     and reject the batch if adding the edges creates a cycle, naming the cycle.
2. **Skip what already exists.** An issue link between the same pair with the same type is
   `exists`. For `remote`, call `executeRead` with `name: listJiraIssueRemoteIssueLinks` first:
   the same URL added twice becomes two links and nothing can remove one.
3. **Create**, with `executeWrite` and `cloudId` at top level:
   - `blocks` and `relates`: `name: createJiraIssueLink`, `inputs: {linkType, inwardIssue,
     outwardIssue}`. For `Blocks`, `inwardIssue` is the blocker and `outwardIssue` is the
     blocked issue. For `Relates`, order does not matter. Confirm the type names with
     `listJiraIssueLinkTypes` if a call is rejected.
   - `remote`: `name: createJiraIssueRemoteIssueLink`, `inputs: {issueIdOrKey, url, title}`.
4. **Return** one row per link. Do not delete or edit existing links: nothing here can, and a
   wrong link is reported to the caller to fix by hand.

## Output

| kind | from | to | status |
|---|---|---|---|
| blocks | JTTC-11 | JTTC-12 | `created`, `exists` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: issues read with their links (JTTC-n, JTTC-m); cycle check: none; existing remote links listed`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Create a *blocks* link that closes a cycle.
- Use a link to express a parent or Epic.
- Add a remote link without checking the existing ones first.
