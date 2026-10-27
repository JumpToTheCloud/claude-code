# GitHub — Gate, Blockers, Sub-issues, Comments, PR

See `prd-to-issues/references/github.md` for the shared Project/field-resolution model
("Resolving the shared Project", "Resolving the `Component`, `Phase`, and `Status` fields",
"Finding a Project item for an existing issue") — this file only covers what's specific to
`execute-feature`.

`<owner>`/`<repo>` below are the Feature's own repo (`JumpToTheCloud/factory-dispacher`, say);
`<project-owner>`/`<project-number>` the shared Project. Every body (comment, PR) is written to a
file in the run directory first (`references/scheduling.md` — "Worktree layout") and passed with
`--body-file`, never inline.

## Fetching the Feature

One GraphQL call gives the gate everything — Issue Type, state, Project `Status`/`Phase`, item ID
and native blockers:

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        id number title state url
        issueType { name }
        blockedBy(first: 50) { nodes { number state repository { nameWithOwner } } }
        projectItems(first: 10) {
          nodes {
            id
            project { number }
            status: fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
            phase: fieldValueByName(name: "Phase") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
          }
        }
      }
    }
  }' -f owner=<owner> -f repo=<repo> -F number=<n>
```

Pick the `projectItems` node whose `project.number` is the shared Project's. If the Project owner
is a personal account (no Issue Types), fall back to the `feature`/`bug` label, same as the rest
of the pipeline.

## Listing executable Features (batch mode, `SKILL.md` Step 0)

Same query as `refine-story/references/github.md` ("Listing Backlog Features"), adding
`phase: fieldValueByName(name: "Phase")` to the item selection and filtering instead on:

```
select(.status.name == "Ready" and .phase.name == "Execution"
       and (.content.issueType.name == "Feature" or .content.issueType.name == "Bug"))
```

Then run the Step 2 blocker check on each and keep only the resolved ones.

## Checking Feature-level blockers (`SKILL.md` Step 2)

For each node in `blockedBy`:

1. `state == "CLOSED"` → resolved.
2. Otherwise read its Project `Status` (same `projectItems` selection as above on that issue) —
   `Done` (case-insensitive) → resolved.
3. Otherwise look for a merged PR from its branch into the base branch:
   ```bash
   gh pr list --repo <blocker-repo> --state merged --base <base-branch> --limit 200 \
     --json number,headRefName,mergedAt \
     --jq '.[] | select(.headRefName | test("^(feature|bugfix)/<blocker-number>-"))'
   ```
   Any match → resolved.

Otherwise unresolved — record its state, `Status`, and open PR if any (same command with
`--state open`) for the stop report.

## Loading sub-issues (`SKILL.md` Step 3)

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        subIssues(first: 50) {
          nodes {
            id number title state body
            labels(first: 20) { nodes { name } }
            blockedBy(first: 50) { nodes { number state } }
            projectItems(first: 10) { nodes { id project { number } } }
          }
        }
      }
    }
  }' -f owner=<owner> -f repo=<repo> -F number=<n>
```

Lowercase every label name before classifying. A `blockedBy` node that is **not** a sibling
sub-issue (cross-Feature dependency) counts as done only when `state == "CLOSED"`.

## Setting `Status`

```bash
gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <status-field-id> --single-select-option-id <option-id>
```

Options used: `In progress` (Feature on claim; sub-task on start), `Done` (sub-task on
integration), `Ready` (blocked sub-task, reset), `In review` (Feature at the end). Best-effort,
same as the rest of the pipeline: a missing option is a warning in the report, never a blocker.
Never touch `Phase` — everything here already is `Execution`.

## Comments and closing

```bash
gh issue comment <n> --repo <owner>/<repo> --body-file <run-dir>/comment-<n>-<kind>.md
gh issue close <n> --repo <owner>/<repo> --reason completed
```

Close only sub-tasks, only after their integration was pushed. Never close the Feature.

The posted body is everything below the `---` line of the matching `assets/comment-*.md`
template (the part above it is guidance for you, never posted). It starts with a hidden marker
`<!-- execute-feature:<kind> -->` (`start`, `done`, `blocked`, `hitl`) so a later run can tell
whether a `hitl` comment is already there:

```bash
gh issue view <n> --repo <owner>/<repo> --json comments \
  --jq '[.comments[].body | select(startswith("<!-- execute-feature:hitl -->"))] | length'
```

## Base branch

```bash
git ls-remote --exit-code --heads origin <base>          # exists?
git push origin origin/<default-branch>:refs/heads/<base>  # create it from main, only if missing
```

`<default-branch>` from `gh repo view <owner>/<repo> --json defaultBranchRef --jq .defaultBranchRef.name`.
If the push is rejected (rulesets forbid creating it), stop and tell the user to create the base
branch — don't fall back to targeting `main`.

## Pull request (`SKILL.md` Step 9)

Find an existing one first (resume):

```bash
gh pr list --repo <owner>/<repo> --head <feature-branch> --state open --json number,url,isDraft
```

Create (after the first integration only):

```bash
gh pr create --repo <owner>/<repo> --draft --base <base> --head <feature-branch> \
  --title "<feat|fix>: <Feature title> (#<n>)" --body-file <run-dir>/pr-body.md
```

`feat` for Issue Type `Feature`, `fix` for `Bug`. Refresh and finish:

```bash
gh pr edit <pr> --repo <owner>/<repo> --body-file <run-dir>/pr-body.md
gh pr ready <pr> --repo <owner>/<repo>
```

Never `gh pr merge`, `gh pr review --approve` or `gh pr close` — merging is a human's call.
