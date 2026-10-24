# GitHub — Fetch, Enrich, Update

See `prd-to-issues/references/github.md` for the shared Project/field-resolution model
(`Resolving the shared Project`, `Resolving the Component/Phase/Status fields`, `Finding a
Project item for an existing issue`) — this file only covers what's specific to `refine-story`.

## Fetching the Feature

```bash
gh issue view <number> --json title,body,comments,id
```

Then find its Project item and current `Status` (see `prd-to-issues/references/github.md` —
"Finding a Project item for an existing issue").

## Listing Backlog Features (batch mode, `SKILL.md` Step 0)

Needs both the `Status` value and the native Issue Type on each item, which `gh project item-
list` doesn't expose together — use GraphQL instead:

```bash
gh api graphql -f query='
  query($owner: String!, $number: Int!, $endCursor: String) {
    organization(login: $owner) {
      projectV2(number: $number) {
        items(first: 100, after: $endCursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            status: fieldValueByName(name: "Status") {
              ... on ProjectV2ItemFieldSingleSelectValue { name }
            }
            content {
              ... on Issue {
                number
                title
                issueType { name }
                repository { nameWithOwner }
              }
            }
          }
        }
      }
    }
  }' -f owner="<project-owner>" -F number=<project-number> \
  --jq '.data.organization.projectV2.items.nodes[]
    | select(.status.name == "Backlog" and .content.issueType.name == "Feature")
    | {number: .content.number, title: .content.title, repo: .content.repository.nameWithOwner}'
```

Page through with `endCursor`/`pageInfo.hasNextPage` if the Project has more than 100 items.

If the Project's owner is a personal account (no Issue Types at all — `organization(login:)`
won't resolve; use `user(login:)` instead), filter on the `feature` label instead of
`issueType.name == "Feature"` — same fallback `prd-to-issues` uses everywhere else. Add
`labels(first: 10) { nodes { name } }` to the `content { ... on Issue { ... } }` selection above
and filter on `.content.labels.nodes[].name == "feature"` in the `--jq` instead.

## Setting `Status`

```bash
gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <status-field-id> --single-select-option-id <refining-or-ready-option-id>
```

`Refining` and `Ready` must already exist as `Status` options — this skill never creates Project
fields or options. If `Refining` is missing, warn and skip just that update (same best-effort
rule `analyze` uses for `Analysis`); don't block refinement over a missing tracking value. `Ready`
is a GitHub Projects default option, so it should always be present.

## Reading the parent PRD and its blockers

```bash
gh issue view <prd-number> --json title,body,comments
```

Look for the `## Success Criteria` section in the PRD body — this is what feeds Step 2.

Blocking issues, via the native connector (not the text "Blocked by" section):

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        blockedBy(first: 20) {
          nodes { number title state }
        }
      }
    }
  }' -f owner="<owner>" -f repo="<repo>" -F number=<feature-number>
```

If any blocker is still open, note it in the session comment (Step 8.2) — it doesn't block
refinement itself (refining is about understanding the work, not starting it), but it's
important context for whoever reads the issue next.

## Reading the Definition of Done (best-effort)

Check `AGENTS.md`/`CLAUDE.md` in the current repo for a `GitHub Management Repo` key (format:
`<owner>/<repo>`, same shape as any other repo reference). If present:

```bash
gh api repos/<management-repo>/contents/docs/DEFINITION_OF_DONE.md --jq '.content' | base64 -d
```

If the key is missing, the API call 404s, or the repo itself is unreachable: treat it exactly as
if the key had never been set — fall through to enriching every NFR individually. Never retry,
never warn loudly; this is a genuine nice-to-have, not a dependency.

## Ensuring the `tdd` label exists

Same low-stakes-local philosophy as `prd-to-issues`'s `afk`/`hitl` labels — this skill creates
it itself rather than only warning, but check case-insensitively first since many repos already
have a `TDD`/`tdd` label from before this pipeline existed:

```bash
gh label list --repo <repo> --json name --jq '.[].name' | grep -i '^tdd$'
```

If something case-insensitively matching `tdd` already exists, reuse it as-is (don't rename it
to force lowercase). Only create a new `tdd` label if nothing matches at all:

```bash
gh label create tdd --repo <repo> --color "C5DEF5" \
  --description "Build this via red-green-refactor (see the tdd skill)"
```

Resolve its node ID the same way `prd-to-issues` resolves `afk`/`hitl`'s.

Adding or removing it from an issue:

```bash
gh issue edit <number> --add-label tdd      # Step 5b judged it suitable
gh issue edit <number> --remove-label tdd   # Step 5b judged it no longer suitable
```

## Updating the Feature

Rewrite the body with `gh issue edit`:

```bash
gh issue edit <number> --body-file <path-to-updated-body.md>
```

Post the session comment:

```bash
gh issue comment <number> --body "$(cat <<'EOF'
<session comment content>
EOF
)"
```

Set `Size`/`Estimate`/`Priority` on the Project item (single-select for `Size`/`Priority`,
number for `Estimate`):

```bash
gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <size-field-id> --single-select-option-id <size-option-id>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <estimate-field-id> --number <estimate-value>

gh project item-edit --project-id <project-node-id> --id <item-id> \
  --field-id <priority-field-id> --single-select-option-id <priority-option-id>
```

Skip the `Priority` call entirely (don't error) if the field has zero options configured — see
`SKILL.md` Step 5.
