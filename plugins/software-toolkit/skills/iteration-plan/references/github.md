# GitHub — Fetch, Analyze, Create Sub-tasks

See `prd-to-issues/references/github.md` for the shared Project/field-resolution model and
`refine-story/references/github.md` for the Feature/PRD/blocker-fetching pattern — this file
only covers what's specific to `iteration-plan`.

## Fetching the Feature

```bash
gh issue view <number> --json title,body,comments,id,repository
```

Then its Project item and `Status` (see `prd-to-issues/references/github.md` — "Finding a
Project item for an existing issue"), and its `Size`/`Estimate`/`Milestone` values — needed for
Step 9's threshold check and for assigning sub-tasks to the same Milestone.

## Searching for Ready, Discovery-phase Features (no issue number given)

Filter on both `Status` and `Phase` — a Feature already broken down sits at `Status: Ready`
too, just with `Phase: Execution`, and that one is not a match here:

```bash
gh project item-list <project-number> --owner <owner> --format json \
  --jq '.items[] | select(.status == "Ready" and .phase == "Discovery")'
```

Present the matches and ask the user which one — this path only applies with a human present
(see `SKILL.md` Step 1 for the headless requirement of an explicit issue number).

## Resolving the "Task" Issue Type

Same mechanism as `prd-to-issues` resolving `Feature` (see its `references/github.md` —
"Resolving the 'Feature' Issue Type") — organization-level, query `organization(login:
$owner).issueTypes`, find the node named `"Task"`. If the org has no Issue Types at all, fall
back to a `task` label instead, same fallback philosophy as the rest of the pipeline.

## Ensuring the category labels exist

Same low-stakes-local philosophy as the `afk`/`hitl` labels in `prd-to-issues` — this skill
creates whichever of these is missing in the Feature's repo, rather than only warning:

```bash
gh label list --repo <repo> --json name --jq '.[].name'
```

For whichever of `development`, `automation`, `spike`, `architecture-design`, `documentation` is
missing:

```bash
gh label create development --repo <repo> --color "0E8A16" --description "Functional implementation"
gh label create automation --repo <repo> --color "5319E7" --description "Integration tests"
gh label create spike --repo <repo> --color "FBCA04" --description "Technical investigation"
gh label create architecture-design --repo <repo> --color "B60205" --description "Interface or architecture decision (always HITL)"
gh label create documentation --repo <repo> --color "0075CA" --description "Documentation"
```

Then resolve their node IDs the same way `prd-to-issues` resolves `afk`/`hitl`'s.

## Ensuring the `tdd` label exists

See `refine-story/references/github.md` ("Ensuring the `tdd` label exists") for the exact
commands — same label, same repo-local low-stakes philosophy, same case-insensitive reuse rule.
Resolve its node ID once per repo, same as the category labels above.

## Creating sub-tasks

Resolve the Feature's repo node ID once, reuse for every sub-task:

```bash
gh repo view <repo> --json id --jq '.id'
```

Write the body from `assets/task-template.md`, then create the issue — one combined mutation,
same pattern as `prd-to-issues`:

```bash
gh api graphql -f query='
  mutation($repositoryId: ID!, $title: String!, $body: String!, $issueTypeId: ID!, $projectId: ID!, $categoryLabelId: ID!, $afkHitlLabelId: ID!, $milestoneId: ID!) {
    createIssue(input: {
      repositoryId: $repositoryId,
      title: $title,
      body: $body,
      issueTypeId: $issueTypeId,
      projectV2Ids: [$projectId],
      labelIds: [$categoryLabelId, $afkHitlLabelId],
      milestoneId: $milestoneId
    }) {
      issue {
        id
        number
        url
        projectItems(first: 5) { nodes { id } }
      }
    }
  }' \
  -f repositoryId="<repo-node-id>" \
  -F title=@<path-to-title.txt> \
  -F body=@<path-to-body.md> \
  -f issueTypeId="<task-issue-type-id>" \
  -f projectId="<project-node-id>" \
  -f categoryLabelId="<category-label-node-id>" \
  -f afkHitlLabelId="<afk-or-hitl-label-node-id>" \
  -f milestoneId="<parent-feature-milestone-node-id>"
```

For a `development` sub-task Step 5 marked for the `tdd` label, add a fourth label variable and
list element the same way (`$tddLabelId: ID!` / `labelIds: [$categoryLabelId, $afkHitlLabelId,
$tddLabelId]` / `-f tddLabelId="<tdd-label-node-id>"`) — never add it for any other category.

`milestoneId` is the **same Milestone the parent Feature already belongs to** — fetch it from
the Feature's own issue data (`gh issue view <feature-number> --json milestone`) rather than
re-resolving or creating a new one.

Then set `Component`/`Phase`/`Status` on the Project item the same `gh project item-edit`
pattern `prd-to-issues` uses for its implementation issues — but with different values here:
`Phase = Execution` (not `Discovery` — a sub-task is itself an execution-phase unit of work from
the moment it exists) and `Status = Ready` (not `Backlog` — see `SKILL.md` Step 7 for why).

## Setting `Status` on the Feature itself (Step 1 and Step 7b)

At the start (Step 1, gate passed): set the parent Feature's own `Status` to `Planning`:

```bash
gh project item-edit --project-id <project-node-id> --id <feature-item-id> \
  --field-id <status-field-id> --single-select-option-id <planning-option-id>
```

At the end (Step 7b, only after every sub-task succeeded): set the Feature's `Status` to `Ready`
**and** `Phase` to `Execution`:

```bash
gh project item-edit --project-id <project-node-id> --id <feature-item-id> \
  --field-id <status-field-id> --single-select-option-id <ready-option-id>

gh project item-edit --project-id <project-node-id> --id <feature-item-id> \
  --field-id <phase-field-id> --single-select-option-id <execution-option-id>
```

Both of these are best-effort, same as every other `Status`/`Phase` write in this pipeline — a
missing option is a warning, never a reason to block.

## Setting native sub-issue hierarchy and dependencies

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $subIssueId: ID!) {
    addSubIssue(input: { issueId: $issueId, subIssueId: $subIssueId }) {
      issue { number }
      subIssue { number }
    }
  }' \
  -f issueId="<parent-feature-node-id>" \
  -f subIssueId="<this-sub-task-node-id>"
```

Then, for each dependency on an already-created sibling sub-task, the same `addBlockedBy`
mutation `prd-to-issues` uses (see its `references/github.md` — "Setting native Blocked-by
relationships"), with both node IDs being sub-task issues this time instead of Features.

If either call fails, treat it exactly like a failed issue creation: stop immediately and report
which sub-tasks and links succeeded and which didn't.

## Correcting `Size` against the real split (Step 8b)

The `Size` field's options and their IDs were already resolved earlier (same `gh project
field-list` lookup `prd-to-issues`/`refine-story` use — see `prd-to-issues/references/github.md`
"Resolving the `Component`, `Phase`, and `Status` fields" for the pattern; `Size` works
identically). Only write it if the smallest option covering the real total is larger than the
Feature's current `Size`:

```bash
gh project item-edit --project-id <project-node-id> --id <feature-item-id> \
  --field-id <size-field-id> --single-select-option-id <corrected-size-option-id>
```

If the total exceeds even `XL`'s range, don't write anything here — there's no larger option —
just note it for Step 9's report.

## Reporting

After all sub-tasks are created, report:
- Sub-task numbers, titles, URLs, category + afk/hitl labels, and which got the `tdd` label
- Native sub-issue links established (and any that failed)
- Native dependency links established (and any that failed)
- The branch name, total estimated hours vs. the Feature's `Size` threshold, and whether `Size`
  was corrected (from what, to what)
- AC coverage check result
- The Feature's final `Status: Ready` + `Phase: Execution` (Step 7b)
