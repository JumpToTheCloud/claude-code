# GitHub — PR, Feature, Comment

Shared queries live elsewhere — this file only covers what's specific to `complete-feature`:

- Project and field resolution: `prd-to-issues/references/github.md` ("Resolving the shared
  Project", "Resolving the `Component`, `Phase`, and `Status` fields").
- Fetching the Feature (Issue Type, state, `Status`/`Phase`, item ID):
  `execute-feature/references/github.md` ("Fetching the Feature").
- Setting `Status`: `execute-feature/references/github.md` ("Setting `Status`").

`<owner>`/`<repo>` are the Feature's repo — the current checkout's unless a URL says otherwise
(`gh repo view --json nameWithOwner --jq .nameWithOwner`). Comment bodies are written to a temp
file first and passed with `--body-file`, never inline.

## PR or issue?

A bare number is either; the issues endpoint answers for both and only PRs carry `pull_request`:

```bash
gh api repos/<owner>/<repo>/issues/<n> --jq 'has("pull_request")'
```

## Fetching the PR

```bash
gh pr view <pr> --repo <owner>/<repo> \
  --json number,url,state,baseRefName,headRefName,body,mergeCommit,mergedAt
```

Requires `state == "MERGED"` and `baseRefName == <base>`. Feature number from the head branch:

```bash
... --jq '.headRefName | capture("^(feature|bugfix)/(?<n>[0-9]+)-").n'
```

Fallback, from the body (case-insensitive): `(?i)\b(close[sd]?|fix(e[sd])?|resolve[sd]?) #([0-9]+)`
— the first match.

## Finding the merged PR of a Feature

```bash
gh pr list --repo <owner>/<repo> --state merged --base <base> --limit 200 \
  --json number,url,headRefName,mergeCommit,mergedAt \
  --jq '[.[] | select(.headRefName | test("^(feature|bugfix)/<n>-"))] | sort_by(.mergedAt) | last'
```

`null` → no merged PR yet.

## Open sub-issues

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        subIssues(first: 50) { nodes { number title state } }
      }
    }
  }' -f owner=<owner> -f repo=<repo> -F number=<n> \
  --jq '[.data.repository.issue.subIssues.nodes[] | select(.state == "OPEN")]'
```

## Comment

The posted body is everything below the `---` line of `assets/comment-done.md`. It starts with
the hidden marker `<!-- complete-feature:done -->`; skip posting if it's already there:

```bash
gh issue view <n> --repo <owner>/<repo> --json comments \
  --jq '[.comments[].body | select(startswith("<!-- complete-feature:done -->"))] | length'

gh issue comment <n> --repo <owner>/<repo> --body-file <tmp>/comment-<n>-done.md
```

Never `gh issue close`, `gh pr merge`, `gh pr close` or `gh pr edit` — this skill only moves
`Status` and comments.
