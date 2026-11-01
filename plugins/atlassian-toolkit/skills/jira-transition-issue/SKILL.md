---
name: jira-transition-issue
description: Move issues of the Jira project JTTC to another status and enforce the Definition of Ready and Definition of Done at the gates - Gate 1 (In refinement to Refined), Gate 2 (Refined to Ready, or Backlog to Ready for a small Task), the Definition of Done (In Review to Done) - using the criteria kept in this skill's references. The transition is found by its target status, never by ID. A failed gate leaves the issue where it is and returns the failed criteria. Use when an issue must move through the workflow, or the user says "move to Ready", "mark as Done", "start refinement", "pasar a Refined", "transition". Setting field values belongs to jira-update-issue.
---

# jira-transition-issue

Moves issues through the JTTC workflow and applies the gates. The caller decides the target
status; this skill checks whether the issue may go there and moves it. Cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. Workflow and status names:
`jttc-workspace`, `references/jira-project.md`.

`Backlog → In refinement → Refined → Ready → In Progress → In Review → Done`. Transitions are
global, so any move is technically possible. The gates below are the rule, not Jira.

## Input

A list of moves. Each has `key` and `to` (a status name, `In refinement` with a lowercase r).
Optional:

| Input | Needed for | Notes |
|---|---|---|
| `evidence` | `Done` | PR URL, CI run, test, output. "Done" without a link is not Done |
| `closing_comment` | `Done` | Outcome and anything that deviated from the plan |
| `reason` | any move backwards | A move to an earlier status is allowed without a gate, but needs a reason, written as a comment |
| `pr_url` | `In Review` | The open pull request |

## Which gate applies

The criteria live in `references/definition-of-ready.md` and `references/definition-of-done.md`
(the Confluence pages are generated mirrors, never read here).

| Move | Gate | Section of the reference |
|---|---|---|
| `Backlog → In refinement` | Entry checklist | `definition-of-ready.md`, "Entry" |
| `In refinement → Refined` | Gate 1 | "Gate 1" (Bug: "Bug variant of Gate 1"). Task: optional, only when unclear. Epic and sub-task: not applicable |
| `Refined → Ready` | Gate 2 | "Gate 2". Task: "Task variant of Gate 2". Sub-task: "Sub-task checklist" |
| `Backlog → Ready` | Task variant of Gate 2, **Task only** | "Task variant of Gate 2". Any other type: reject |
| `Ready → In Progress` | none | |
| `In Progress → In Review` | A pull request exists | `pr_url` given and linked on the issue |
| `In Review → Done` | Definition of Done | `definition-of-done.md`: Universal, plus Story, Bug or Epic by type, plus the component type |
| Any move to an earlier status | none, needs `reason` | |

## Steps

1. **Read each issue** with `getJiraIssue` (`view: full`) and `listJiraIssueRemoteIssueLinks`
   through `executeRead`. Take its type, status, fields, description, sub-tasks and links.
2. **Pick the gate** from the table. If the move skips a status the table does not allow
   (for example `Backlog → Done`, or `Backlog → Ready` on a Story), reject it.
3. **Read the reference file** for the gate (`references/definition-of-ready.md` or
   `references/definition-of-done.md`) and evaluate only the section that applies. Do not call
   Confluence for the criteria. The only Confluence call allowed is the **PRD approval
   check**: Gate 1 requires the PRD page linked from the issue or its Epic to be `APPROVED`.
   Take the page ID from the remote link URL (`/pages/<id>/`) and read the page with
   `getConfluenceContent` and `detail: summary`: the excerpt starts with the summary table and
   its Status row reads `Status APPROVED Green` when the status lozenge is `APPROVED`. Any other
   text, or no Status row, means not approved. If the excerpt does not reach the Status row,
   read the page once with `detail: full` and `content_format: html` and look for the lozenge
   `<span data-type="status" ...>`. The state lives in that lozenge only, never in a label. With `No PRD: <reason>` the criterion is `N/A`.
   A remote link to a Confluence PRD page counts as the PRD link; it does not need to be
   repeated in the description. For `Done`, see "What the transition skill can and cannot
   check" in `definition-of-done.md`.
4. **Evaluate every criterion** of that section against the issue, as yes or no. A criterion
   that does not apply must say `N/A` and a reason **in the issue**; if it is silently
   missing, it fails. Mechanical checks use the data you read (Story Points in the Fibonacci
   set and at most 8, Size not `XXL`, Business Value, Risk, Mode, sub-task estimates at most
   8 hours, the sum of the estimates against the Story Points, *blocks* links with no cycle,
   a Component, a parent, all sub-tasks Done, `Flagged` empty and no open *is blocked by*).
   Judgement checks (acceptance criteria that are testable, every NFR category answered,
   assumptions written, paths named) are read from the description. Be strict: "send it back
   when" in the page is the standard.
5. **If any criterion fails, do not move the issue.** Return the failed criteria, each with
   what is missing. Do not write a comment and do not edit the issue.
6. **If everything passes, move it.** `executeRead` with `name: listJiraIssueTransitions`, pick
   the transition whose **target status** is `to` (never the transition name, never a guessed
   ID), then `transitionJiraIssue` with its ID. The result says the status the issue landed in.
   **Moving to `In Review`:** before the check, if `pr_url` was given and is not already among
   the issue's remote links (`listJiraIssueRemoteIssueLinks`), link it yourself with
   `executeWrite`, `name: createJiraIssueRemoteIssueLink`, `inputs: {issueIdOrKey, url: <pr_url>,
   title: "Pull request"}`. The caller does not have to link it separately. Without a `pr_url`
   and without an existing pull request link, the move is rejected.
7. **Comment** with `addOrEditJiraIssueComment`: the `closing_comment` for `Done`, the `reason`
   for a backward move. A comment inside the transition call can be dropped silently.
8. **Sub-tasks and the parent move together at Gate 2.** When the issue is a Story, Task or Bug
   going to `Ready`, the whole set of its sub-tasks is checked first: all must pass the
   sub-task checklist, otherwise nothing moves. If they pass, move the parent and then its
   sub-tasks to `Ready`.

## Output

| key | from | to | status |
|---|---|---|---|
| JTTC-9 | In refinement | Refined | `moved`, or `blocked: <failed criteria>`, or `rejected: <reason>` |

For a `blocked` row, list the failed criteria below the table, one per line, naming the page
section they come from.

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you actually did, for example `Checks: issue read with links; gate Gate 1 from definition-of-ready.md; PRD approval searched; transition found by target status; comment added`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Move an issue whose gate failed, "with a promise to fix it later".
- Accept `Done` without `evidence` and a `closing_comment`.
- Find a transition by its name or guess its ID.
- Skip a criterion silently, or accept `N/A` without a reason in the issue.
- Read the Definition of Ready or Definition of Done from Confluence: the references are the source.
- Edit fields or the description: that is `jira-update-issue`.
