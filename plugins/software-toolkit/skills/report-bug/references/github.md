# GitHub — Bug Type, Creation, Duplicates, Comments

Shared queries live elsewhere — this file only covers what's specific to `report-bug`:

- Project and field resolution, Project item lookup, `afk`/`hitl` labels, `createIssue` and
  `addBlockedBy`: `prd-to-issues/references/github.md` ("Resolving the shared Project",
  "Resolving the `Component`, `Phase`, and `Status` fields", "Ensuring the `afk`/`hitl` labels
  exist", "Creating Issues", "Setting native Blocked-by relationships").
- Fetching an origin issue: `execute-feature/references/github.md` ("Fetching the Feature").
- Resolving a PR to its Feature: `complete-feature/references/github.md` ("PR or issue?",
  "Fetching the PR").

Every title, body and comment is written to a temp file first and passed with `-F …=@<file>` or
`--body-file`, never inline.

## Bug Issue Type

Same lookup as `prd-to-issues` uses for `Feature` ("Resolving the 'Feature' Issue Type"), picking
the node named `"Bug"`. No Issue Types in the org (personal account) → fall back to a `bug` label,
creating it if missing:

```bash
gh label create bug --repo <owner>/<repo> --color "D73A4A" --description "Something isn't working"
```

Never create the Issue Type itself.

## Creating the Bug

The `createIssue` mutation from `prd-to-issues/references/github.md` ("Creating Issues"), with
`issueTypeId` = the Bug type, `labelIds: [<afk-or-hitl-label-id>]`, and `milestoneId` only when
the origin has a Milestone — drop the variable and the field from the mutation otherwise. Record
the issue's node `id`, `number`, `url` and its Project item `id`.

Then, on that item, `gh project item-edit` three times: `Component` (the origin's, or the
current repo's declared one), `Phase = Discovery`, `Status = Backlog` — same calls as
"Set `Component`, `Phase`, and `Status` on each issue's Project item" there.

## Linking blocked issues

For each issue the Bug blocks (`issueId` = the blocked issue, `blockingIssueId` = the Bug — both
node IDs, from `gh issue view <n> --repo <owner>/<repo> --json id,state`):

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $blockingIssueId: ID!) {
    addBlockedBy(input: { issueId: $issueId, blockingIssueId: $blockingIssueId }) {
      issue { number }
      blockingIssue { number }
    }
  }' -f issueId="<blocked-issue-node-id>" -f blockingIssueId="<bug-node-id>"
```

The blocked issue's current `Status` (for the `In progress`/`In review` warning) comes from its
Project item — same `projectItems` selection as "Fetching the Feature".

## Duplicate check

```bash
gh issue list --repo <owner>/<repo> --state open \
  --search 'in:body "report-bug:origin=<n|none>"' \
  --json number,title,url,issueType
```

Keep only results of Issue Type `Bug` (or label `bug`) and compare titles: same fault described
the same way → duplicate. When unsure, interactive asks; headless treats it as a new Bug only if
the affected files differ too.

## PR diff

```bash
gh pr diff <pr> --repo <owner>/<repo> --name-only   # files first
gh pr diff <pr> --repo <owner>/<repo>               # then the hunks you need
```

## Comments

The posted body is everything below the `---` line of `assets/comment-origin.md`. It starts with
`<!-- report-bug:<bug-number> -->`; skip a target that already has it:

```bash
gh issue view <n> --repo <owner>/<repo> --json comments \
  --jq '[.comments[].body | select(startswith("<!-- report-bug:<bug-number> -->"))] | length'

gh issue comment <n> --repo <owner>/<repo> --body-file <tmp>/comment-<n>-bug.md
gh pr comment <pr> --repo <owner>/<repo> --body-file <tmp>/comment-pr-<pr>-bug.md
```

(`gh pr view <pr> --json comments` for the PR's marker check.) Never `gh issue reopen`, never
`gh issue edit --state`, never `gh project item-edit` on the origin.
