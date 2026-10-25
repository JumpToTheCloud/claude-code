---
name: prd-to-issues
description: Break a PRD (a GitHub issue written by /prd) into independently-grabbable issues using tracer-bullet vertical slices, created with the native "Feature" Issue Type, an afk/hitl label, a per-PRD Milestone, and native GitHub issue dependencies, in the repo its Component maps to, added to the team's shared GitHub Project with Component and Phase fields set. Use whenever the user wants to convert a PRD to issues, create implementation tickets, break down a spec into work items, or create GitHub issues from a PRD. Trigger on "prd-to-issues", "break PRD into issues", "create issues from PRD", "create GitHub issues from PRD", "create tasks from spec", or any variation of converting a product spec into implementation tasks.
context: fork
agent: prd-to-issues
background: false
allowed-tools: Bash(gh issue *), Bash(gh api *), Bash(gh project *), Bash(gh repo *), Read, Grep, Glob, AskUserQuestion
---

# PRD to Issues

Break a PRD into independently-grabbable GitHub issues using vertical slices (tracer bullets).
Issues are created with the native `Feature` Issue Type, exactly one of the `afk`/`hitl`
labels, and this PRD's Milestone, in the repo the PRD's Component maps to, added to the shared
GitHub Project, and linked back to the source PRD and to each other via both a text reference
and a native GitHub dependency link.

This skill runs in an isolated `prd-to-issues` subagent with no visibility into the conversation
that triggered it — the PRD issue number arrives as the input and everything else (Component,
target repo, Project fields) is re-derived from GitHub and `AGENTS.md`/`CLAUDE.md`. This also
means issue creation (which can mean many sequential `gh` calls for a large breakdown) doesn't
block or clutter the main session.

## Step 0 — Fetch the PRD

The PRD is always a GitHub issue. Read `references/github.md` ("Fetching the PRD") and fetch it.
If it is empty or has no actionable content, tell the user and stop.

Extract from the PRD:
- **User stories** — numbered list of user-facing outcomes ("As a X, I want Y so that Z")
- **Functional requirements** — constraints and rules the implementation must satisfy
- **Non-functional requirements** — performance, security, scalability constraints

**Quality gate check**: look through the issue's comments for an `/analyze` report (header
`## 🔍 Consistency Analysis`) and its verdict. If there is none, or the latest verdict was "❌
Not ready", tell the user explicitly and ask whether to proceed anyway:

> _"No passing `/analyze` report found on this PRD (or the last one wasn't ready). `/analyze`
> is meant to run before breaking a PRD into issues. Proceed anyway, or run `/analyze` first?"_

This is a warning, not a hard block — respect the user's choice either way.

---

## Step 0b — Resolve the Component, its target repo, and the "Feature" Issue Type

Read `references/github.md` ("Resolving the shared Project", "Resolving the Component → repo
mapping", "Resolving the 'Feature' Issue Type") and follow it:
1. Resolve the shared GitHub Project (config, token scope, node ID).
2. Resolve the `Component`, `Phase`, and `Status` field/option IDs on that Project.
3. Find the PRD's Project item and read its `Component` value.
4. Discover which repo self-declares that Component (`gh search code` across the org — there is
   no central table; see `references/github.md` for the exact queries and how to handle zero or
   multiple matches).
5. Verify the discovered repo actually exists and is reachable: `gh repo view <component-repo>`.
6. Resolve the organization's "Feature" Issue Type (every implementation issue this skill
   creates gets that type). If the org has no Issue Types at all (e.g. the repo's owner is a
   personal account), fall back to a `feature` label instead — same fallback `prd` uses for the
   "PRD" type.
7. Ensure the `afk` and `hitl` labels exist in the Component's repo — create them if missing
   (see `references/github.md` — "Ensuring the afk/hitl labels exist"). Unlike Issue Types and
   Project fields, repo labels are low-stakes and local, so this skill creates them itself
   rather than only warning.
8. Resolve or create this PRD's Milestone in the Component's repo (see `references/github.md`
   — "Resolving the PRD's Milestone"): named `PRD #<prd-issue-number>: <prd-title>`, reused if
   it already exists (e.g. a prior run on the same PRD), created otherwise. Same low-stakes
   philosophy as the labels — this skill creates it itself.

If any of these is missing or unresolvable (Project, field, option, no repo declares the
Component, more than one repo declares it, the repo itself is unreachable, or no "Feature"
Issue Type and no way to fall back), stop and ask the user rather than guessing. Checking the
repo exists *here* — before exploring code or drafting slices — avoids discovering a typo'd or
undeclared Component only after several issues have already been created against it.

---

## Step 1 — Explore the codebase (optional)

Exploring code means reading local files — it only works if the current working directory is a
checkout of the Component's repo (resolved in Step 0b). Compare it against the current repo
(`gh repo view --json nameWithOwner`); if they don't match, tell the user and let them choose:

> _"This PRD's Component resolves to `<component-repo>`, but you're currently in `<current-
> repo>`. Switch to a checkout of `<component-repo>` for accurate exploration, or continue
> without exploring code (slices drafted from the PRD content alone)?"_

If they match (or the user chooses to continue without exploring), look for existing patterns to
follow and avoid reimplementing what's already there.

---

## Step 2 — Draft vertical slices

Break the PRD into **tracer bullet** slices. Each slice is a thin vertical cut through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Every slice is **exactly one** of 'HITL' or 'AFK' — never both, never neither. This becomes a
label (`hitl` or `afk`) on the created issue, so the classification has to be a clean binary
choice, not a spectrum:
- **HITL**: requires human interaction (architectural decision, design review, external approval)
- **AFK**: can be implemented and merged without human interaction

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
- A slice that is only "set up scaffolding" or "create the database schema" is NOT a tracer bullet — push it to include a real user-facing interaction
</vertical-slice-rules>

Map each slice to the PRD user stories it addresses — this makes coverage traceable even
without a parent Epic.

**Before presenting the breakdown**: check the "Blocked by" relationships you just assigned for
cycles (slice A blocked by B, B blocked by A, directly or transitively). If one exists, resolve
it yourself (usually by merging the cyclic slices or re-ordering the dependency) before showing
anything to the user — never present a breakdown whose dependency order is impossible to create.

## Step 3 — Quiz the user

Present the proposed breakdown as a flat numbered list:

```
Target: <component-repo> (Component: <name>)

Implementation Slices:
  1. <Slice title> [AFK]
     Covers: US-1, US-2
     Blocked by: Slice 2
  2. <Slice title> [HITL]
     Covers: US-3
     Blocked by: none
```

Ask the user:
- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL / AFK?

Iterate until the user approves the breakdown.

## Step 4 — Create the issues

Read `references/github.md` ("Creating Issues", "Setting native Blocked-by relationships") for
the exact commands.

**Order matters**: always create blockers before blocked issues — this is required (not just
convenient) now, since the native dependency link in step 5 below needs the blocking issue's
real node ID to already exist, and it also lets you reference real issue numbers in the
"Blocked by" text section.

1. Create each issue in the Component's repo, with Issue Type `Feature` (or the `feature` label
   fallback) **and** the `afk` or `hitl` label (exactly one, from Step 2's classification),
   directly inside the shared Project, **and** assigned to this PRD's Milestone (resolved in
   Step 0b) — one `createIssue` GraphQL mutation does all of this, same pattern `prd` uses for
   the PRD issue itself. In dependency order.
2. Reference real issue numbers (or the full URL, if the PRD lives in a different repo) in the
   "Blocked by" text section — keep this even though step 5 also sets a native relationship;
   it's the quick-glance version for someone reading the issue body.
3. Link back to the parent PRD issue.
4. Set `Component` (inherited from the PRD), `Phase = Discovery`, and `Status = Backlog` on the
   Project item returned by that same mutation.
5. For each "Blocked by" relationship this slice has, call `addBlockedBy` (GraphQL) with this
   issue's node ID and the blocking issue's node ID — a **native** GitHub dependency, not just
   the text reference. This is what lets tooling later query "what's unblocked right now"
   instead of parsing issue bodies, which matters once work is parallelized across people/agents.

**If any step fails partway through** (network error, permission error, a `gh` call rejected,
a dependency link rejected, etc.): stop immediately. Do not continue to the next slice and do
not attempt to delete or revert the issues already created — report exactly which issues were
created (numbers, URLs, Component/Phase/Status/label set, which dependency links succeeded) and
which were not, and ask the user how they want to proceed. A shared Project and repo are not
yours to silently roll back.

Once every issue has been created successfully, mark the PRD itself as done with Discovery:
find its Project item and set its `Status` to `Broken Down` (see `references/github.md` —
"Mark the PRD as Broken Down"). If the Status field is missing the `Broken Down` option, warn
and skip this one step — don't let a missing tracking option undo work that already
succeeded.

Do NOT close or modify the parent PRD issue.

## Step 5 — Report

Tell the user what was created: issue numbers, titles, repo, URLs, the Component/Phase/Status
set on each, which of `afk`/`hitl` each got, the native dependency links established, the
Milestone every issue was assigned to, and the PRD's own `Status: Broken Down`.

If the user has not yet run `/analyze` on the spec, suggest it as a quality gate before
implementation begins.

---

## Rules

- Issues always go in the repo the PRD's Component maps to — never in the PRD's own repo unless
  they happen to be the same.
- Every issue this skill creates gets Issue Type `Feature` (or the `feature` label fallback) —
  never left untyped, and never any other Issue Type.
- Every issue gets exactly one of the `afk`/`hitl` labels — never both, never neither.
- Every "Blocked by" relationship gets both the text reference in the body **and** a native
  `addBlockedBy` link — the text is for humans skimming the issue, the native link is for
  tooling/automation that needs to query dependency state, so neither replaces the other.
- Every issue this skill creates belongs to this PRD's Milestone (`PRD #<number>: <title>`) —
  reuse an existing one with that exact title instead of creating a duplicate.
- `Phase` is always set to `Discovery` on every issue this skill creates. Nothing in this skill
  ever sets `Phase` to `Execution` — that happens later, on the Feature itself, once
  `/iteration-plan` finishes breaking it down (and directly, at creation time, on each of its
  sub-tasks) — out of scope here.
- If the Component → repo mapping, the Project, or its fields can't be resolved, stop and ask —
  never guess a repo or skip setting a field silently.
- Never present a breakdown with a dependency cycle — detect and resolve it before Step 3.
- On partial failure during creation, stop and report — never silently continue past a failed
  issue, and never auto-delete or roll back issues already created.
