# GitHub — Publish the PRD

The PRD is published as a GitHub issue of **Issue Type "PRD"** (a native GitHub field, not a
label), created directly inside the shared GitHub Project (v2) with its `Component` and `Phase`
fields set. All three — Issue Type, Project membership, repo — are set in a single `createIssue`
GraphQL mutation; only the two custom field values need a follow-up call.

**The PRD issue is always created in the current repo** (the repo the skill is invoked from) —
`Component` does not relocate the PRD itself, it only tells `prd-to-issues` later which repo
the *implementation* issues go in. Resolve the current repo's `nameWithOwner` with
`gh repo view --json nameWithOwner` if you need it for any of the commands below.

Resolve the Project config (`GitHub Project` / `GitHub Project Owner` in `AGENTS.md`/
`CLAUDE.md`) the same way `prd-to-issues/references/github.md` describes — both skills share
the same model, documented in full in that file. There is no central Component → repo table:
each repo self-declares its Component via `/init-repo`, and `prd-to-issues` discovers it by
searching the org when it's time to create implementation issues — `/prd` itself only needs the
Project's `Component` field options (to show the user valid names), not the repo mapping. See
`../../prd-to-issues/references/configuration.md` for the one-time setup checklist if any of
this is missing.

---

## Step 0 — Resolve everything before drafting (fail fast)

Do this **before** Step 1 of `prd/SKILL.md` (gathering context), not after the draft is
approved — if any of this is missing, the user should find out before investing time in writing
and reviewing a PRD, not after.

1. **Issue Type "PRD"** — Issue Types are configured at the **organization** level (not
   per-repository — every repo in the org sees the same set, modulo per-repo enablement):

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

   Find the node whose `name` is `"PRD"` and keep its `id`. If no such type exists, **stop and
   tell the user**:

   > _"This organization has no 'PRD' Issue Type configured. Issue Types are managed at the
   > organization level (Settings → Issue types) — ask an org admin to add one, then re-run
   > `/prd`."_

   Do not attempt to create the Issue Type yourself. If the repo's owner is a personal account
   rather than an organization, Issue Types aren't available at all (they require an org) — tell
   the user and fall back to a `prd` label instead of an Issue Type for the rest of this flow.

2. **Project, scope, and fields** — resolve the shared Project, check the token's `project`
   scope, and resolve the `Component`/`Phase` field and option IDs exactly as described in
   `prd-to-issues/references/github.md` ("Resolving the shared Project", "Resolving the
   `Component` and `Phase` fields"). Stop and tell the user if any of it is missing — same
   failure handling as there.

3. **Repo and Project node IDs** — needed for Step 2/3 below:

   ```bash
   gh repo view --json id --jq '.id'
   gh project view <project-number> --owner <project-owner> --format json --jq '.id'
   ```

Keep all the resolved IDs (Issue Type, repo, Project, Component option, Phase/Discovery option)
for the rest of the flow — nothing here needs to be re-resolved later in the same run.

---

## Step 1 — Confirm the destination before publishing

Right before creating the issue (after the user has approved the PRD content in `prd/SKILL.md`
Steps 6–7), show them the resolved destination explicitly — approving the PRD's content is not
the same as approving where it lands:

> _"This will be created as a 'PRD' issue in `<owner>/<repo>`, added to the '<project title>'
> Project with Component = `<component>` and Phase = `Discovery`. Proceed?"_

Only continue to Step 2 after explicit confirmation.

---

## Step 2 — Create the issue with that Issue Type, directly in the Project

Create the issue in one mutation — it sets the Issue Type and adds it to the Project at creation
time, and returns the Project item ID needed for Step 3. Write both the title and the body to
variables (or temp files) before building the command, rather than interpolating user-authored
text directly into the shell command — a title or body containing quotes or backticks can
otherwise break the command. `-F field=@<path>` reads a value verbatim from a file, which is the
safest option for the body (long markdown); for the title, a shell variable populated via `printf
'%s' "$title" > /tmp/prd-title.txt` (or equivalent) and read the same way works just as well:

```bash
gh api graphql -f query='
  mutation($repositoryId: ID!, $title: String!, $body: String!, $issueTypeId: ID!, $projectId: ID!) {
    createIssue(input: {
      repositoryId: $repositoryId,
      title: $title,
      body: $body,
      issueTypeId: $issueTypeId,
      projectV2Ids: [$projectId]
    }) {
      issue {
        number
        url
        projectItems(first: 5) { nodes { id } }
      }
    }
  }' \
  -f repositoryId="<repo-node-id>" \
  -F title=@<path-to-title.txt> \
  -F body=@<path-to-prd-body.md> \
  -f issueTypeId="<prd-issue-type-id>" \
  -f projectId="<project-node-id>"
```

Record the issue `number`, `url`, and the single `id` under `issue.projectItems.nodes` — that is
the Project item ID used in Step 3 (no separate `gh project item-add` call needed; the issue was
added to the Project at creation time).

---

## Step 3 — Set `Component` and `Phase` on the Project item

```bash
gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <component-field-id> --single-select-option-id <component-option-id>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <phase-field-id> --single-select-option-id <discovery-option-id>
```

`Component` is the value chosen in `/prd` Step 1. `Phase` is always set to `Discovery` at
creation.

---

## Report

Tell the user the issue number, URL, Component, and Phase (`Discovery`) so they can share or
reference it.
