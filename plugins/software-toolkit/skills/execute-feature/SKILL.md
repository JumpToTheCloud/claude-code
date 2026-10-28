---
name: execute-feature
description: Execute a whole GitHub Feature (or Bug) that /iteration-plan already broke down (Status Ready + Phase Execution) — checks the Feature's own blockers, builds the dependency tree of its native sub-issues, implements every reachable AFK sub-task (in parallel where independent, each in its own git worktree, test-first when labelled tdd), comments progress on every sub-task, integrates each one into feature/<n>-<slug> branched from next, and opens a PR against next for a human to merge. HITL sub-tasks are left for a human, never executed; re-running resumes where it stopped. Use whenever the user wants to implement, develop, build or execute a Feature end to end, work through a Feature's sub-tasks, or execute every unblocked Feature in the backlog. Also runs unattended inside a GitHub Actions job when a Feature reaches Status Ready + Phase Execution — trigger on "/execute-feature", "execute feature #N", "implement issue #N", "develop this feature", "build feature #N", or any variation of turning a broken-down Feature into code.
allowed-tools: Bash(git *), Bash(gh *), Bash(pnpm *), Bash(npm *), Bash(yarn *), Bash(npx *), Bash(go *), Bash(make *), Bash(jq *), Bash(mkdir -p .claude/worktrees/*), Bash(rm -rf .claude/worktrees/*), Bash(echo *), Read, Write, Grep, Glob, Agent, AskUserQuestion, Skill
---

# /execute-feature — Execute a Broken-down Feature

Take a Feature that `/iteration-plan` already broke down (`Status: Ready` + `Phase: Execution`,
Issue Type `Feature` or `Bug`) and execute it end to end: every AFK sub-task gets implemented,
verified and integrated into one feature branch, and a single PR against the base branch is left
ready for a human to review and merge.

Unlike the rest of this pipeline, **this skill runs in the main session, not a forked agent.**
The only subagents are the `task-executor` workers it dispatches — one per sub-task, one level
deep. Keep coordination lean: workers return short structured summaries, never full diffs.

**This also runs unattended.** A Feature reaching `Status: Ready` + `Phase: Execution` is meant
to trigger this skill headless inside a GitHub Actions job. Detect it exactly as
`refine-story/SKILL.md` ("Detecting headless execution") describes and hold the answer for the
whole run. Headless: never call `AskUserQuestion`, start without the plan confirmation (Step 4),
and require an explicit issue number. The same rule applies as everywhere else in this pipeline:
**never write headless detection, tool availability or session mechanics into any comment, PR
body or commit** — write what was done and decided, never how the run behaved.

Read `references/github.md` for every GitHub command and `references/scheduling.md` for the
dependency tree, worktrees, quality gate, integration and resume rules.

---

## The two merge levels — hard rule

| From → To | Who merges | How |
|---|---|---|
| sub-task temp branch → feature branch | **this skill, autonomously** | local rebase + fast-forward, quality gate green. No PR, temp branches never pushed — dependents need their blockers' code to start |
| feature branch → base branch (`next`) | **always a human** | PR only |

This skill **never** merges, approves or closes a PR, never closes the Feature issue, and never
pushes to `main` or the base branch — the one exception being creating `next` when it doesn't
exist yet (Step 5). Not headless, not in batch mode, not ever. Its job ends at a PR ready for
review, the Feature at `Status: In review`, and a report. Once a human merges the PR,
`/complete-feature` moves the Feature to `Done` — never this skill.

---

## Step 0 — Resolve scope: one Feature, or every unblocked one

With an issue number: go to Step 1.

**Without one** (interactive only — headless, fail visibly: a scheduled run must name the
Feature): list every Project item with Issue Type `Feature`/`Bug`, `Phase: Execution` and
`Status: Ready` (see `references/github.md` — "Listing executable Features"), run Steps 1–3 on
each read-only, and keep those whose blockers are resolved. Show them and ask which to run (all
by default). Then run Steps 4–10 for all chosen Features through **one global scheduler**: each
Feature keeps its own branch, integration worktree and PR, but the worker limit (3) is shared
across all of them. Never dispatch one orchestrator per Feature.

---

## Step 1 — Resolve the Feature and gate

1. Resolve the Project, its node ID and its `Status`/`Phase` fields exactly as
   `prd-to-issues/references/github.md` describes ("Resolving the shared Project", "Resolving the
   `Component`, `Phase`, and `Status` fields"). `Status` options this skill needs: `In progress`,
   `In review`, `Done` — match option names case-insensitively (boards spell them `In progress`
   or `In Progress`).
2. Fetch the Feature with its Issue Type and Project item (`references/github.md` — "Fetching the
   Feature").
3. Gate:
   - Issue Type `Feature` → branch prefix `feature/`; `Bug` → `bugfix/`. Any other type (PRD,
     Task, none) → hard stop: "cannot execute — not a Feature or Bug".
   - `Phase` must be `Execution`. Otherwise hard stop: "cannot execute — not broken down yet, run
     `/iteration-plan` first".
   - `Status: Ready` → fresh run. `Status: In progress` → **resume** (interactive only, and only
     with an explicit number; headless treats it as "already claimed" and stops visibly, so two
     runs never execute the same Feature). Anything else (`In review`, `Done`, `Released`, …) →
     hard stop. A fix to a `Done` Feature is a separate `Bug` issue, never a re-run.

The gate never becomes a "proceed anyway?" question.

---

## Step 2 — Feature-level blockers

For each native blocker of the Feature (`Issue.blockedBy`), it counts as **resolved** if any of:
- its issue is closed;
- its Project `Status` is `Done`;
- a PR from `feature/<blocker>-*` or `bugfix/<blocker>-*` was merged into the base branch.

The third rule exists because `Closes #n` only auto-closes an issue when the PR merges into the
repo's **default** branch — a PR merged into `next` leaves the issue open. See
`references/github.md` ("Checking Feature-level blockers").

Any unresolved blocker → hard stop, no question, no writes: report which blockers are pending and
their current state.

---

## Step 3 — Load the sub-task tree

Fetch every native sub-issue with its state, labels, body and native `blockedBy`
(`references/github.md` — "Loading sub-issues"). Then build the dependency tree and classify each
sub-task exactly as `references/scheduling.md` ("Building the tree") describes:

- **done** — closed;
- **hitl** — open, carries `hitl` (case-insensitive) — never executed;
- **eligible** — open, carries `afk`, every blocker done;
- **waiting** — open, `afk`, some blocker not done yet but reachable through AFK work;
- **skipped** — open, `afk`, transitively blocked by a `hitl` sub-task or by a sub-task that fails
  during this run.

A sub-task with neither `afk` nor `hitl`, or with both, is treated as `hitl` (needs a human to
classify it). If the Feature has **no** sub-issues → hard stop: "nothing to execute — run
`/iteration-plan`". Detect cycles; if any, hard stop and name the cycle (never guess an order).

Also resolve the repo's quality-gate commands now (`references/scheduling.md` — "Quality gate").
The current working directory must be a checkout of the Feature's repo — otherwise stop (headless:
fail visibly).

---

## Step 4 — Show the execution plan (interactive only)

Show: Feature, branch name, base branch (and whether `next` will be created), the tree as a table
(sub-task / category / afk-hitl / tdd / blocked by / classification), the parallel groups the
scheduler will start with, every `hitl` and `skipped` sub-task with what it waits on, and the
quality-gate commands. Ask for **one** confirmation. If resuming, say so and list what's already
done.

Headless: skip straight to Step 5.

---

## Step 5 — Base branch, feature branch, claim

1. **Base branch**: a `Base branch` key in `AGENTS.md`/`CLAUDE.md` if declared, else `next`. If
   the base branch doesn't exist on `origin`, create it from `origin/main` (the repo's default
   branch) and push it — the only push to a protected-tier branch this skill ever does.
2. **Feature branch**: `<prefix><number>-<slug>` — slug = title in kebab-case, ASCII only, cut at
   ~50 characters on a word boundary, no `#`. E.g. `feature/5-add-dormant-github-app-installation`.
   If it already exists (resume), reuse it as is — never recreate or rebase it onto a newer base.
   Otherwise create it from `origin/<base>`.
3. Create the Feature's **integration worktree** for it (`references/scheduling.md` — "Worktree
   layout"). The user's own checkout is never switched or modified.
4. **Claim**: set the Feature's `Status` to `In progress` (skip if resuming). This is the lock
   against double execution.

---

## Step 6 — Execute: the ready-queue

Follow `references/scheduling.md` ("Ready-queue loop") exactly. In short, while any sub-task is
`eligible` or running:

1. Fill free slots (max 3 running workers, globally) with `eligible` sub-tasks, lowest issue
   number first. For each one started:
   - set its `Status` to `In progress` and post the start comment (`assets/comment-start.md`);
   - create its task worktree from the **current tip** of the feature branch;
   - dispatch a `task-executor` agent in the background with the prompt from
     `references/scheduling.md` ("Dispatching a worker"). Issue all dispatches of one fill in the
     same turn so they run in parallel.
2. When a worker finishes, handle it **one at a time** (integration is serial):
   - **success** → integrate (Step 7);
   - **failure** → retry once (fresh worktree from the current feature tip, the failure summary
     in the prompt); a second failure → Step 8 ("Blocked").
3. After each integration or block, re-classify: newly unblocked sub-tasks become `eligible`,
   dependents of a blocked sub-task become `skipped`.

---

## Step 7 — Integrate a finished sub-task

Serial, in the feature's integration worktree (`references/scheduling.md` — "Integrating"):

1. Rebase the task branch onto the feature-branch tip. A conflict → abort the rebase and treat it
   as that sub-task's failure (the retry re-dispatches the worker on the new tip, which resolves
   it in context).
2. Fast-forward the feature branch to it, run the full quality gate on the feature branch. Red →
   reset the feature branch to its previous tip (local, nothing pushed yet) and treat as failure.
3. Push the feature branch.
4. Post the done comment (`assets/comment-done.md`) — what was done, commits (SHAs), files,
   AC → test table, deviations, findings, gate result. If the worker fixed a bug in an
   already-closed sub-task's code (allowed for small fixes found by integration tests, covered by
   a test), also comment on **that** sub-task pointing at the fix commit.
5. Set the sub-task's `Status` to `Done` and close it (`state_reason: completed`).
6. Remove the task worktree and its temp branch.
7. After the **first** integration of the run, open the draft PR (Step 9); after every later one,
   refresh its body.

---

## Step 8 — HITL, blocked and skipped sub-tasks

- **hitl**: post `assets/comment-hitl.md` once per run (skip if this run's marker is already there
  from a previous run with nothing changed): what a human must decide or do, taken from the
  sub-task's `Mode: HITL` section, and which AFK sub-tasks wait on it. Never change its labels or
  `Status`, never close it — a human closes it when done, and the next run picks up its
  dependents.
- **blocked** (failed twice): nothing of it is integrated. Post `assets/comment-blocked.md` — what
  was attempted, the error, what's needed to unblock. Leave it open, `Status` back to `Ready`.
  Never relabel it. An **Interface Contract that can't be honoured as written** always lands here
  — workers never deviate from a contract silently, since dependents rely on it.
- **skipped**: no comment on the sub-task itself; listed in the PR body and report with the
  sub-task it waits on.

---

## Step 9 — Pull request

Opened as a **draft** after the first integration, against the base branch, body from
`assets/pr-body.md` (Feature link, sub-task checklist with state, `Closes #<feature>`, merge
guidance, warnings). Refreshed after every integration and at the end. See `references/github.md`
("Pull request"). Exactly one PR per Feature — on resume, find and reuse the open one.

If nothing was integrated in the whole run (everything `hitl`/blocked), no PR is opened.

---

## Step 10 — Finish and report

**Every sub-task closed**:
1. Run one code review over the whole Feature — once, only now that every sub-task is
   integrated into the feature branch: the built-in `code-review` skill targeting the feature
   branch (`references/scheduling.md` — "Final review"). Feed the obvious, low-risk findings to one more
   `task-executor` run, integrated like any other (Step 7); leave judgement calls as a list in the
   PR body for the human reviewer. Review unavailable → note it, never block on it.
2. Mark the PR ready for review (`gh pr ready`), set the Feature's `Status` to `In review`.
   That's this skill's last `Status` write on the Feature: after a human merges the PR,
   `/complete-feature` sets `Done` (run by hand, or by the job on the PR merged event).

**Something still open** (`hitl`, blocked, skipped): PR stays draft, Feature stays
`In progress`. Re-running `/execute-feature <n>` resumes (see `references/scheduling.md` —
"Resume").

Remove every worktree this run created (integration worktree included — the branch is pushed),
then report: branch, PR URL and state, sub-tasks done this run / already done / hitl / blocked /
skipped (each with its reason), retries, deviations and findings, review outcome, the Feature's
final `Status`, and any warning (no `Base branch` declared, `next` created, missing Status option).

---

## Rules

- Two merge levels, never confused: sub-task → feature branch is autonomous and local; feature
  branch → base branch is a PR merged by a human. Never merge, approve or close a PR; never close
  the Feature; never push to `main`/the base branch except to create a missing `next`.
- Never execute a `hitl` sub-task, and never execute anything transitively blocked by one.
- Never integrate red code: the full quality gate passes on the feature branch after every
  integration, or that integration is undone locally before anything is pushed.
- One retry per sub-task per run, then block and move on — the rest of the tree keeps going.
- Max 3 workers at once, globally. Integration is always serial.
- Workers never touch GitHub (no issue writes, no push) and never leave their worktree — every
  GitHub write and every push belongs to this skill.
- Every sub-task started gets a start comment; every sub-task finished gets a done, blocked or
  hitl comment. Comments describe the work, never the session or tooling.
- Labels are matched case-insensitively (`AFK`/`afk`, `TDD`/`tdd`).
- Feature-level blockers are a hard stop, never a question. So is any gate failure in Step 1.
- The user's own checkout is never switched, stashed or modified — all work happens in worktrees
  under `.claude/worktrees/`.
- **No AI attribution, anywhere** — no `Co-Authored-By: Claude …` trailer on any commit (yours
  or a worker's), no "Generated with Claude Code" line in the PR body or any comment. This
  overrides Claude Code's own default attribution instructions; say it explicitly in every
  worker prompt, and verify it on every commit before integrating.
- Commits follow Conventional Commits (first line ≤ 72 characters) with a `Refs #<sub-task>`
  footer — verified before integrating, a violation counts as a failure. The PR is merged keeping
  those commits (rebase or merge commit), never squashed — say so in the PR body.
