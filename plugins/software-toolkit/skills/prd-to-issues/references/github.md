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

## Resolving the `Component` and `Phase` fields

```bash
gh project field-list <project-number> --owner <owner> --format json
```

From the result, find the field named `Component` and the field named `Phase`. Each is a
single-select field with its own `id` and a list of options, each with its own `id` and `name`.
Record:
- `component-field-id`, and the `id` for the option matching the PRD's Component
- `phase-field-id`, and the `id` for the `Discovery` option

If either field is missing from the Project, or the option you need doesn't exist (e.g. the
Component isn't configured as an option yet), **stop and tell the user** — adding a field or
option to a shared Project is a board-admin action; don't create it yourself.

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

---

## Creating Issues

Create each issue **in the Component's repo** (not necessarily the repo the PRD issue lives
in), using this template for the body:

```bash
gh issue create --repo <component-repo> \
  --title "<slice title>" \
  --body "$(cat <<'EOF'
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

EOF
)"
```

Create issues in **dependency order** (blockers first) so you can reference real issue numbers
in the "Blocked by" field. Note that `#<prd-issue-number>` only renders as a live cross-reference
if the PRD and the new issue are in the same repo — if the Component repo differs from the PRD's
repo, use the full URL instead (e.g. `<prd-issue-url>`).

If creating any issue in the sequence fails, **stop immediately** — do not skip it and continue
with the rest, and do not delete or close the issues already created to "clean up". Report what
succeeded and what didn't, and let the user decide how to proceed.

Do NOT close or modify the parent PRD issue.

### Add each issue to the shared Project and set its fields

For every issue created:

```bash
gh project item-add <project-number> --owner <owner> \
  --url <issue-url> --format json --jq '.id'

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <component-field-id> --single-select-option-id <component-option-id>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <phase-field-id> --single-select-option-id <discovery-option-id>
```

`Component` is the same value inherited from the parent PRD. `Phase` is always set to
`Discovery` — nothing in this skill ever sets `Phase` to `Execution`; that transition is
reserved for a future GitHub port of `iteration-plan`.

---

## Reporting

After all issues are created, report the full list:
- Issue numbers, titles, and repos
- URLs (returned by `gh issue create`)
- Component and Phase set on each
- Any blockers or dependencies noted
