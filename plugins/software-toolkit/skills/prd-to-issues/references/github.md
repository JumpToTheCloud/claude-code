# GitHub — Fetch PRD, Resolve Component, Create Issues

This is the full reference for the Project/Component/Phase model. `prd/references/github.md`
points back here for the shared parts instead of repeating them. See `configuration.md` for the
one-time setup checklist (Issue Type, Project fields, config keys) a team needs before either
skill works.

## Fetching the PRD

```bash
gh issue view <number> --json title,body,labels,comments
```

The issue body is the PRD. Read it carefully — it contains user stories, functional requirements, and constraints. Comments may contain prior discussion or clarifications that affect scope.

---

## Resolving the shared Project

1. Check `AGENTS.md` and `CLAUDE.md` for:
   - `GitHub Project` — the Project's number or title
   - `GitHub Project Owner` — the Project's owner login (user or org)
2. If either is missing, call `gh project list --owner <owner>` (try the repo's owner first) and
   ask the user which Project to use. Record both — reuse for the rest of the session.
3. Check the token has the `project` scope: `gh auth status`. If it doesn't, stop and tell the
   user to run `gh auth refresh -s project` themselves (this is an interactive auth flow — don't
   run it on their behalf).
4. Get the Project's node ID (needed for `item-edit`):
   ```bash
   gh project view <project-number> --owner <owner> --format json --jq '.id'
   ```

## Resolving the `Component`, `Phase`, and `Status` fields

```bash
gh project field-list <project-number> --owner <owner> --format json
```

From the result, find the fields named `Component`, `Phase`, and `Status`. Each is a
single-select field with its own `id` and a list of options, each with its own `id` and `name`.
Record:
- `component-field-id`, and the `id` for the option matching the PRD's Component
- `phase-field-id`, and the `id` for the `Discovery` option
- `status-field-id`, and the `id`s for whichever `Status` options this skill needs
  (`Backlog`, `Ready for Breakdown`, `Broken Down` — see each skill's own `SKILL.md` for which
  it sets and when)

If a field is missing from the Project, or an option you need doesn't exist (e.g. the Component
isn't configured as an option yet, or the Discovery-specific Status values haven't been added),
**stop and tell the user** — adding a field or option to a shared Project is a board-admin
action; don't create it yourself. `prd`/`plan`/`analyze` treat a missing `Status` option as
best-effort (warn and continue) rather than a hard stop, since it's a tracking nicety, not a
requirement for producing a PRD/plan/analysis — see their own `SKILL.md`. `prd-to-issues`
still stops hard on a missing `Component`/`Phase` option, same as before.

## Finding a Project item for an existing issue

Needed whenever a skill updates `Status` on an issue that already has a Project item (the PRD,
when `plan`/`analyze` touch it) rather than one it just created itself:

```bash
gh project item-list <project-number> --owner <owner> --format json \
  --jq '.items[] | select(.content.number == <issue-number>)'
```

The result includes the item's `id` (needed for `item-edit`) directly, along with `status`,
`component`, and `phase` as plain fields — no need to dig into a nested fields array.

## Resolving the "Feature" Issue Type

Every implementation issue this skill creates gets the native GitHub Issue Type `Feature` (not
a label) — same mechanism `prd` uses for the `PRD` type, see `prd/references/github.md` ("Step
1 — Resolve the 'PRD' Issue Type") for the full reasoning. Issue Types are organization-level:

```bash
gh api graphql -f query='
  query($owner: String!) {
    organization(login: $owner) {
      issueTypes(first: 50) {
        nodes { id name isEnabled }
      }
    }
  }' -f owner="<org>" --jq '.data.organization.issueTypes.nodes'
```

Find the node whose `name` is `"Feature"` and keep its `id`. If the org has no Issue Types at
all (e.g. the Component's repo belongs to a personal account), fall back to a `feature` label
instead — create it first if missing (`gh label create feature --repo <component-repo> ...`).
Do not attempt to create the Issue Type itself.

## Ensuring the `afk`/`hitl` labels exist

Unlike Issue Types and Project fields/options, these are ordinary repo labels — low-stakes and
local, so this skill creates them itself rather than only warning:

```bash
gh label list --repo <component-repo> --json name --jq '.[].name'
```

For whichever of `afk`/`hitl` is missing from that list:

```bash
gh label create afk --repo <component-repo> --color "1D76DB" \
  --description "Can be implemented and merged without human interaction"
gh label create hitl --repo <component-repo> --color "D93F0B" \
  --description "Requires human interaction (architectural decision, design review, external approval)"
```

Then resolve their node IDs (needed for `labelIds` below):

```bash
gh label list --repo <component-repo> --json id,name --jq '.[] | select(.name == "afk" or .name == "hitl")'
```

## Resolving the Component → repo mapping

There is no central table to maintain — each repo self-declares its Component in its own
`AGENTS.md`/`CLAUDE.md` (written by the `init-repo` skill), as the exact line
`GitHub Component: <name>`. Discover the repo by searching for that declaration across the org:

First, find the PRD's Component by locating its item in the Project:

```bash
gh project item-list <project-number> --owner <owner> --format json \
  --jq '.items[] | select(.content.number == <prd-issue-number>)'
```

Then search the org for the repo that self-declares it (two calls — `gh search code` doesn't
accept more than one `--filename` per call, so check both candidate filenames and merge):

```bash
gh search code "GitHub Component: <component>" --owner <org> --filename AGENTS.md \
  --json path,repository
gh search code "GitHub Component: <component>" --owner <org> --filename CLAUDE.md \
  --json path,repository
```

`<org>` is the same owner already resolved for the Project (`GitHub Project Owner`) — no extra
config key needed.

- **Exactly one match** (across both calls) → that `repository.nameWithOwner` is the target
  repo. Verify it's actually reachable before doing anything else with it:
  ```bash
  gh repo view <component-repo>
  ```
  If this fails (deleted, renamed since the search index last updated, no access), stop and ask
  — don't discover it mid-way through creating issues.
- **Zero matches** → stop and tell the user: *"No repo in `<org>` self-declares Component
  `<component>`. Run `/init-repo` on the intended repo, or check its `AGENTS.md` for a typo."*
- **More than one match** → stop and tell the user which repos conflict: *"Both `<repo1>` and
  `<repo2>` self-declare Component `<component>` — fix the duplicate declaration before
  continuing."* Never pick one arbitrarily.

## Resolving the PRD's Milestone

Milestones are repo-local (unlike the Project), so this is the earliest point the target repo
is known. Same low-stakes philosophy as the `afk`/`hitl` labels — this skill creates it itself
rather than only warning; it's an ordinary repo entity, not board/org-admin infrastructure.

Name: `PRD #<prd-issue-number>: <prd-title>` — unique, traceable to the source PRD at a glance.

Check whether it already exists first (so re-running this skill on the same PRD, e.g. after
adding more slices, reuses it instead of duplicating):

```bash
gh api repos/<component-repo>/milestones --paginate --jq \
  '.[] | select(.title == "PRD #<prd-issue-number>: <prd-title>")'
```

If found, record its `node_id`. If not, create it:

```bash
gh api --method POST repos/<component-repo>/milestones \
  -f title="PRD #<prd-issue-number>: <prd-title>" \
  -f due_on="<ISO-8601-datetime>" \
  --jq '.node_id'
```

Only pass `-f due_on=...` when the PRD's `**Deadline**` field is set to something other than
"None" — omit the flag entirely otherwise, rather than guessing a date.

Record the returned `node_id` — that's the `milestoneId` used in every `createIssue` mutation
below.

---

## Creating Issues

Create each issue **in the Component's repo** (not necessarily the repo the PRD issue lives
in), with Issue Type `Feature`, directly inside the shared Project — one `createIssue` GraphQL
mutation does all three (same combined pattern `prd` uses for the PRD issue; see
`prd/references/github.md` — "Step 2 — Create the issue with that Issue Type, directly in the
Project" for why body/title go through temp files rather than inline shell interpolation).

First, resolve the Component repo's node ID (once, reuse for every issue):

```bash
gh repo view <component-repo> --json id --jq '.id'
```

Write the body to a temp file using this template, then create the issue:

```markdown
## Parent PRD

#<prd-issue-number>

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation. Reference specific sections of the parent PRD rather than duplicating content.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- Blocked by #<issue-number>

Or "None — can start immediately" if no blockers.

## User stories addressed

Reference by number from the parent PRD:
- User story 1
- User story 3
```

```bash
gh api graphql -f query='
  mutation($repositoryId: ID!, $title: String!, $body: String!, $issueTypeId: ID!, $projectId: ID!, $labelId: ID!, $milestoneId: ID!) {
    createIssue(input: {
      repositoryId: $repositoryId,
      title: $title,
      body: $body,
      issueTypeId: $issueTypeId,
      projectV2Ids: [$projectId],
      labelIds: [$labelId],
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
  -f repositoryId="<component-repo-node-id>" \
  -F title=@<path-to-title.txt> \
  -F body=@<path-to-body.md> \
  -f issueTypeId="<feature-issue-type-id>" \
  -f projectId="<project-node-id>" \
  -f labelId="<afk-or-hitl-label-node-id>" \
  -f milestoneId="<milestone-node-id-from-above>"
```

`$labelId` is **either** the `afk` or the `hitl` label's node ID — whichever Step 2 classified
this slice as, never both (don't pass a two-element array here).

If falling back to the `feature` label (no Issue Types in this org), use
`gh issue create --repo <component-repo> --title ... --body-file <path> --label feature --label
afk-or-hitl --milestone "<milestone-title>"` instead — that path doesn't set a Project
membership or Issue Type, so still follow up with `gh project item-add` (see
`prd/references/github.md` for that call shape) to add it to the Project, and fetch the issue's
node `id` separately (`gh issue view <number> --json id`) for the dependency-linking step below.

Record the issue `id` (its node ID — needed for `addBlockedBy` below), `number`, `url`, and the
single `id` under `issue.projectItems.nodes` (the Project item ID, used in the next section — no
separate `gh project item-add` call needed when the GraphQL path was used).

Create issues in **dependency order** (blockers first) so you can reference real issue numbers
in the "Blocked by" field. Note that `#<prd-issue-number>` only renders as a live cross-reference
if the PRD and the new issue are in the same repo — if the Component repo differs from the PRD's
repo, use the full URL instead (e.g. `<prd-issue-url>`).

If creating any issue in the sequence fails, **stop immediately** — do not skip it and continue
with the rest, and do not delete or close the issues already created to "clean up". Report what
succeeded and what didn't, and let the user decide how to proceed.

Do NOT close or modify the parent PRD issue.

### Set `Component`, `Phase`, and `Status` on each issue's Project item

```bash
gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <component-field-id> --single-select-option-id <component-option-id>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <phase-field-id> --single-select-option-id <discovery-option-id>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <status-field-id> --single-select-option-id <backlog-option-id>
```

`Component` is the same value inherited from the parent PRD. `Phase` is always set to
`Discovery` — nothing in this skill ever sets `Phase` to `Execution`; `/iteration-plan` is what
moves a Feature (and its sub-tasks) into `Execution`, once the Feature is fully broken down.
`Status` is always set to `Backlog` on a freshly created implementation issue, regardless of
`Phase`.

### Setting native Blocked-by relationships

For every "Blocked by" relationship a slice has (the blocking issue must already exist — this
is why creation order matters), link them natively in addition to the text reference already in
the body:

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $blockingIssueId: ID!) {
    addBlockedBy(input: { issueId: $issueId, blockingIssueId: $blockingIssueId }) {
      issue { number }
      blockingIssue { number }
    }
  }' \
  -f issueId="<this-issue-node-id>" \
  -f blockingIssueId="<blocking-issue-node-id>"
```

Both IDs are issue **node** IDs (the `id` field from `createIssue`'s response, or from
`gh issue view <number> --json id` for issues created via the label-fallback path) — not issue
numbers. If this call fails, treat it the same as a failed issue creation: stop immediately and
report exactly which dependency links succeeded and which didn't, alongside which issues were
created — don't let a missing native link pass silently, since the whole point is for tooling
to be able to trust it later.

### Mark the PRD as `Broken Down`

Once every issue above has been created successfully (and only then — see the partial-failure
rule above), find the PRD's own Project item (using "Finding a Project item for an existing
issue" above, with the PRD's issue number) and set its `Status` to `Broken Down`:

```bash
gh project item-edit --project-id <project-node-id> --id <prd-item-id> \
  --field-id <status-field-id> --single-select-option-id <broken-down-option-id>
```

---

## Reporting

After all issues are created, report the full list:
- Issue numbers, titles, and repos
- URLs (returned by `createIssue`)
- Component, Phase, and Status set on each, and the PRD's own `Status: Broken Down`
- Which of `afk`/`hitl` each issue got
- Native dependency links established (and any that failed)
- The milestone title and URL every issue was assigned to
