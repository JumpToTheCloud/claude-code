---
name: complete-feature
description: Move a GitHub Feature (or Bug) to Status Done once its PR (feature/<n>-* or bugfix/<n>-*, opened by /execute-feature) has been merged into the base branch (next) — resolves the Feature from the PR or the PR from the Feature, gates on Issue Type, Phase Execution and Status In review (the only Status it moves from), sets Status Done and posts a completion comment. Never closes the issue (it stays open until the Feature is Released), never touches Phase or the PR, and is idempotent. Use whenever the user says a Feature's PR was merged, wants to mark a Feature done, or wants the board updated after a merge into next. Also runs unattended inside a GitHub Actions job on the "PR merged" event — trigger on "/complete-feature", "complete feature #N", "mark #N done", "PR #N merged", "feature #N merged", or any variation of closing out the development of a merged Feature.
allowed-tools: Bash(gh *), Bash(jq *), Bash(echo *), Read, AskUserQuestion
---

# /complete-feature — Mark a Merged Feature Done

`/execute-feature` leaves a Feature at `Status: In review` with a PR against the base branch
(`next`). A human merges that PR — and `Closes #n` doesn't fire, because `next` isn't the repo's
default branch. This skill closes that gap: given the merged PR (or the Feature), it moves the
Feature to `Status: Done`.

**`Done` is not `Released`.** `Done` means development is finished and merged into the base
branch: dependents are unblocked (`/execute-feature` already counts a `Done` blocker as
resolved). `Released` means it shipped and was validated. Between the two, a release candidate
is deployed and tested; if it reveals a bug, a `Bug` issue is created and set as a blocker of
the Feature that caused it — the dependents stay unblocked, but the Feature can't become
`Released` while that Bug is open. That's why this skill **never closes the issue**: it stays
open until it is `Released`. Creating RC bugs and moving to `Released` are not this skill's job.

**This also runs unattended.** A GitHub Actions job runs it headless on the **PR merged** event,
passing the PR number. Detect it exactly as `refine-story/SKILL.md` ("Detecting headless
execution") describes and hold the answer for the whole run. Headless: never call
`AskUserQuestion` and require an explicit argument. **Never write headless detection, tool
availability or session mechanics into any comment** — write what was done, never how the run
behaved.

Read `references/github.md` for every GitHub command.

---

## Step 1 — Resolve the PR and the Feature

The argument is a PR or an issue: a PR URL, `--pr <n>`, an issue URL, or a bare `#<n>`/`<n>`.
A bare number can be either — check it (`references/github.md` — "PR or issue?"). No argument:
interactive → ask for it; headless → fail visibly.

Resolve the **base branch** first: a `Base branch` key in `AGENTS.md`/`CLAUDE.md` if declared,
else `next` — same rule as `execute-feature/SKILL.md` Step 5.

- **Given a PR**: fetch it (`references/github.md` — "Fetching the PR"). It must be `MERGED` and
  its base must be the base branch — otherwise hard stop, no writes (an open PR: "not merged
  yet"; a PR into another branch: "not merged into `<base>`"). The Feature number comes from the
  head branch, `^(feature|bugfix)/(\d+)-`; fallback, the first `Closes|Fixes|Resolves #<n>` in
  the body. Neither → hard stop: "can't tell which Feature this PR implements".
- **Given an issue**: find its merged PR from `feature/<n>-*` or `bugfix/<n>-*` into the base
  branch (`references/github.md` — "Finding the merged PR of a Feature"). None → hard stop: "no
  PR for #<n> merged into `<base>` yet". More than one → take the most recently merged.

---

## Step 2 — Resolve the Project and fetch the Feature

1. Resolve the Project, its node ID and its `Status`/`Phase` fields exactly as
   `prd-to-issues/references/github.md` describes ("Resolving the shared Project", "Resolving the
   `Component`, `Phase`, and `Status` fields"). `Status` option this skill needs: `Done` —
   matched case-insensitively.
2. Fetch the Feature with the same query as `execute-feature/references/github.md` ("Fetching
   the Feature"), and its sub-issues' state (`references/github.md` — "Open sub-issues").

---

## Step 3 — Gate

Hard stops, never a question, no writes:

- Issue Type `Feature` or `Bug` (the `feature`/`bug` label on a personal-account Project). Any
  other → "not a Feature or Bug".
- `Phase: Execution`. Any other → "#<n> hasn't been through `/iteration-plan`".
- `Status`:
  - `In review` → proceed. This is the **only** `Status` a Feature moves to `Done` from — states
    are never skipped.
  - `Done` or `Released` → **no-op**: report "already `<Status>`" and exit successfully. The job
    can fire more than once for the same merge.
  - Anything else — `In progress` included, even with the PR already merged → hard stop, no
    writes: "#<n> is at `<Status>` — only `In review` can move to `Done`". A PR merged before
    `/execute-feature` finished (HITL or blocked sub-tasks left) needs a human to sort the
    Feature out; this skill never jumps over `In review`.
- The `Done` option missing on the board → hard stop: it's the only thing this skill writes.
  Tell the user to add it.

Open sub-issues don't stop the run — list them in the comment and the report.

---

## Step 4 — Set Done and comment

1. Set the Feature's `Status` to `Done` (`execute-feature/references/github.md` — "Setting
   `Status`").
2. Post the completion comment from `assets/comment-done.md`, unless one is already there
   (`references/github.md` — "Comment"): the merged PR, merge commit, base branch, open
   sub-issues if any, and that the Feature is pending release.

Never close the issue, never touch `Phase`, never touch the PR or any sub-task.

---

## Step 5 — Report

Feature (number, title, URL), PR (number, URL, merge commit), base branch, `Status` before →
after (or "already `<Status>`, nothing to do"), and any warning (open sub-issues, no
`Base branch` declared so `next` was assumed).

---

## Rules

- Only `Status` changes, only `In review` → `Done`. Never skip a state. Never close or reopen the Feature, never set
  `Released`, never touch `Phase`, the PR, or any sub-task.
- Idempotent: a Feature already `Done` or `Released` is a successful no-op; the comment is posted
  at most once.
- Every precondition failure is a hard stop with no writes — headless, it fails visibly (non-zero
  exit, clear message) so the job shows red.
- Comments describe the merge, never the session or tooling. **No AI attribution** — no
  "Generated with Claude Code" line or similar in any comment.
