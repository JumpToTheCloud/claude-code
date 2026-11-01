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
| `evidence` | `Done` | The fixed contract of `how-gates-are-applied.md`: `pr_url`, `merged`, `ci`, `reviewer`, plus what that type adds. "Done" without a link is not Done |
| `closing_comment` | `Done` | Outcome and anything that deviated from the plan |
| `reason` | any move backwards | A move to an earlier status is allowed without a gate, but needs a reason, written as a comment |
| `pr_url` | `In Review` | The open pull request. Not used for an Epic, which has no `In Review` |

## Which gate applies

Three files in `references/`, each with its own job:

| File | What it holds |
|---|---|
| `definition-of-ready.md` | **What must be true** for Entry, Gate 1, Gate 2 and the variants. The team's agreement, mirrored to Confluence |
| `definition-of-done.md` | **What must be true** for Done. The team's agreement, mirrored to Confluence |
| `how-gates-are-applied.md` | **How this skill applies them**: which move runs which gate, how each criterion is checked in Jira, and how the Definition of Done is evidenced. Read it first |

The Confluence pages for the two definitions are generated mirrors and are never read here.

## Steps

1. **Read each issue** with `getJiraIssue` (`view: full`) and `listJiraIssueRemoteIssueLinks`
   through `executeRead`. Take its type, status, fields, description, sub-tasks and links.
2. **Pick the gate** from the table "Which move runs which gate" of
   `references/how-gates-are-applied.md`. If the move skips a status that table does not allow
   (for example `Backlog → Done`, or `Backlog → Ready` on a Story), reject it.
3. **Read the references.** Start with `references/how-gates-are-applied.md` to know which gate the
   move runs and how each criterion is checked in Jira, then read the section of
   `references/definition-of-ready.md` or `references/definition-of-done.md` that applies. Do
   not call Confluence for the criteria. The only Confluence call allowed is the **PRD approval
   check** described in `how-gates-are-applied.md`: take the page ID from the remote link URL
   (`/pages/<id>/`) and read the page with `getConfluenceContent` and `detail: summary`; its
   excerpt starts with the summary table, and the Status row reads `Status APPROVED Green` when
   the status lozenge is `APPROVED`. Any other text, or no Status row, means not approved. If the
   excerpt does not reach the Status row, read the page once with `detail: full` and
   `content_format: html` and look for the lozenge `<span data-type="status" ...>`. With
   `No PRD: <reason>` the criterion is `N/A`. For `Done`, see "The Definition of Done: what can be
   checked and how" in `how-gates-are-applied.md`.
4. **Evaluate every criterion** of that section against the issue, as yes or no. A criterion
   that does not apply must say `N/A` and a reason **in the issue**; if it is silently
   missing, it fails. Mechanical checks use the data you read (Story Points in the Fibonacci
   set and at most 8, Size not `XXL`, Business Value, Risk, Mode, sub-task estimates at most
   8 hours, the sum of the estimates against the Story Points, *blocks* links with no cycle,
   a Component, a parent, all sub-tasks Done, `Flagged` empty and no open *is blocked by*).
   Judgement checks (acceptance criteria that are testable, every NFR category answered,
   assumptions written, paths named) are read from the description. Be strict: "send it back
   when" in the page is the standard. **You may never decide on your own that a criterion does
   not apply.** `N/A` counts only when it is already written in the issue with its reason: a
   criterion that is not addressed fails, even when the scope seems to make it irrelevant (for
   example acceptance criteria with no edge or error case, and no `N/A` saying why).
5. **If any criterion fails, do not move the issue.** Return the failed criteria, each with
   what is missing. Do not write a comment and do not edit the issue.
6. **If everything passes, move it.** `executeRead` with `name: listJiraIssueTransitions`, pick
   the transition whose **target status** is `to` (never the transition name, never a guessed
   ID), then `transitionJiraIssue` with its ID. The result says the status the issue landed in.
   **Moving to `In Review` (never an Epic):** before the check, if `pr_url` was given and is not already among
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
