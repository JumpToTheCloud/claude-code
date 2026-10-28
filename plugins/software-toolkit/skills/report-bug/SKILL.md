---
name: report-bug
description: File a bug found during review, while executing a Feature, or in a release candidate as a GitHub issue with the native "Bug" Issue Type — reproduction steps, expected vs actual behavior, affected files, Given/When/Then acceptance criteria including a regression test, an afk/hitl label, added to the shared Project with Component, Phase Discovery and Status Backlog so it enters the usual refine-story → iteration-plan → execute-feature → complete-feature flow. Optionally links its origin (the issue or PR that introduced it — traceability only, never a blocker, except for release-candidate bugs, which block their Done origin from reaching Released) and marks the issues it blocks with native dependencies (addBlockedBy). Use whenever the user found a bug, wants to report, file or open a bug, or turn a review finding into an issue. Also runs unattended inside a GitHub Actions job or from /execute-feature's final review — trigger on "/report-bug", "report a bug", "file a bug", "open a bug for this", "crear un bug", "this is a bug in #N", or any variation of recording a defect.
allowed-tools: Bash(gh *), Bash(git *), Bash(jq *), Bash(echo *), Read, Grep, Glob, AskUserQuestion
---

# /report-bug — File a Bug into the Pipeline

Turn a fault description into a `Bug` issue that the rest of the pipeline can pick up exactly
like a Feature: `/refine-story` refines it, `/iteration-plan` breaks it down, `/execute-feature`
fixes it on a `bugfix/<n>-<slug>` branch, `/complete-feature` marks it `Done` once merged.

Unlike most of this pipeline, **this skill runs in the main session, not a forked agent** — the
fault is usually described in the conversation (a review finding, a failing deploy), and that
context is the best source for the issue body.

**This also runs unattended** — from a GitHub Actions job, or from `/execute-feature` when its
final review finds a fault outside the Feature's diff. Detect it exactly as
`refine-story/SKILL.md` ("Detecting headless execution") describes and hold the answer for the
whole run. Headless: never call `AskUserQuestion`, never wait for confirmation, gaps become
named assumptions, and every input comes as an argument. **Never write headless detection, tool
availability or session mechanics into the issue or any comment** — write what was found, never
how the run behaved.

Read `references/github.md` for every GitHub command.

---

## Origin: traceability, not a blocker — hard rule

A Bug can name its **origin**: the issue (Feature or Bug) or the PR that introduced it.

- **Found in review or during execution** (the normal case): the origin's own work is finished —
  it keeps moving `In review` → `Done` as usual. The Bug records the origin in `## Origin` and
  comments on it. **The origin is never blocked.**
- **Found in a release candidate** (`--found-in <rc>`): the origin is `Done` but must not be
  `Released` while the fault is open — so the Bug **also blocks the origin** (`addBlockedBy`).
  Its dependents stay unblocked: `Done` still counts as a resolved blocker for them.

Whatever the case, the origin's `Status` and open/closed state are never touched — never
reopened, never moved back.

---

## Inputs

| Input | Meaning |
|---|---|
| description (required) | What fails — free text, or taken from the conversation |
| `--origin #n` | The issue (Feature/Bug) that introduced it |
| `--pr #n` | The PR that introduced it (or where review found it) |
| `--blocks #a,#b` | Issues that can't proceed until this is fixed — always linked |
| `--found-in <rc>` | Found in this release candidate (e.g. `v1.4.0-rc.1`) |

Interactive, any of these can come from the conversation ("the bug we just saw in #26 breaks
#6"). Headless, only what's passed — a missing description fails visibly.

---

## Step 1 — Resolve the origin

- `--pr`: fetch it and resolve its Feature/Bug from the head branch (`feature|bugfix/<n>-*`) or
  the first `Closes #n` in the body (`complete-feature/references/github.md` — "Fetching the
  PR"). The PR may be open or merged. If `--origin` is also given and differs, keep `--origin`
  and warn.
- `--origin`: fetch it with the query in `execute-feature/references/github.md` ("Fetching the
  Feature"). Keep its repo, Issue Type, `Status`, Component and Milestone (`gh issue view <n>
  --json milestone`).
- Neither: no origin — `## Origin` says "None".

`--found-in` with an origin that isn't `Done` (or `Released`) → warn: the origin is only
blocked when it's `Done` (Step 7).

---

## Step 2 — Resolve repo, Component and Project

- Repo and Component: the origin's. No origin → the current checkout's repo and its
  `GitHub Component: <name>` line in `AGENTS.md`/`CLAUDE.md` (written by `/init-repo`).
- Project, its node ID and `Component`/`Phase`/`Status` fields exactly as
  `prd-to-issues/references/github.md` describes ("Resolving the shared Project", "Resolving the
  `Component`, `Phase`, and `Status` fields").
- The `Bug` Issue Type (`references/github.md` — "Bug Issue Type") and the `afk`/`hitl` labels
  (`prd-to-issues/references/github.md` — "Ensuring the `afk`/`hitl` labels exist").

No Component resolvable, or no `Discovery`/`Backlog` option → hard stop: the Bug couldn't enter
the flow.

---

## Step 3 — Investigate

Fill what a developer needs to reproduce and fix it without asking:

- The PR diff if there's one (`gh pr diff`), and the origin's body (what it was meant to do).
- The code, when the current checkout is the Bug's repo: Grep/Read the paths involved to name
  the affected files and, where clear, the function and line.
- Reproduction steps as concrete as the evidence allows (inputs, command, request, state).

Real gaps (expected behavior unclear, can't tell how to trigger it): interactive → one round of
at most 5 questions (`AskUserQuestion`); headless → named assumptions written into the body.
Never invent a reproduction you can't support — say what's known and mark the rest as an
assumption.

---

## Step 4 — Draft

Title: what fails, in plain words, ≤ 70 characters, no `Bug:` prefix (the Issue Type says it).
Body from `assets/bug-body.md`:

- `## Origin`, `## Summary`, `## Steps to reproduce`, `## Expected behavior`,
  `## Actual behavior`, `## Affected files`.
- `## Acceptance criteria` in Given/When/Then — the fixed behavior, and **always** a regression
  test: _"Given the conditions in Steps to reproduce, when the regression test runs, then it
  fails before the fix and passes after it."_
- `## Blocks` — the `--blocks` issues (and the origin, in the RC case), or "None".
- `## Mode: AFK` or `## Mode: HITL` with a one-line reason. **AFK** when the fix is clear and
  local; **HITL** when it needs a human decision (an Interface Contract change, a design or
  product call, data migration or repair, infrastructure or credentials). Headless: decide and
  state the reason as a plain decision.
- The hidden marker `<!-- report-bug:origin=<n|none> -->` as the body's first line.

---

## Step 5 — Duplicate check

Look for an open Bug in the repo with the same origin marker and a near-identical title
(`references/github.md` — "Duplicate check"). Found: interactive → show it and ask whether to
create anyway; headless → don't create, report the existing one (a re-run must never file the
same Bug twice) and still apply Steps 7–8 to it for any link or comment missing.

---

## Step 6 — Confirm (interactive only)

Show title, body, afk/hitl with its reason, Milestone, what it will block (and that the origin is
**not** blocked, unless RC), and where it will comment. Ask for **one** confirmation; apply the
edits asked for. Headless: skip to Step 7.

---

## Step 7 — Create and link

1. Create it in the Bug's repo with Issue Type `Bug`, directly in the Project, with the afk/hitl
   label and the origin's Milestone if it has one (`references/github.md` — "Creating the Bug").
2. Set `Component`, `Phase = Discovery`, `Status = Backlog` on its Project item — it enters the
   pipeline like any Feature, ready for `/refine-story`.
3. `addBlockedBy` for each `--blocks` issue (the Bug blocks it) — and the origin too, **only**
   with `--found-in` and the origin at `Done`. A blocked issue that is closed → skip it with a
   warning; one already `In progress`/`In review` → link anyway and warn (it's executing without
   the fix).

Any failure → stop immediately and report exactly what was created and linked. Never delete or
close what was already created.

---

## Step 8 — Comment on the origin

Post `assets/comment-origin.md` on the origin issue and on the PR if one was given — whatever
their state, closed included. Link the Bug, one-line summary, what it blocks; in the RC case, say
it now blocks `Released`. Skip a target that already has this Bug's comment (marker in
`references/github.md` — "Comments"). Never reopen anything, never change a `Status`.

---

## Step 9 — Report

Bug number, URL, title, afk/hitl, Milestone, issues it blocks, whether the origin was blocked
(and why or why not), comments posted, named assumptions, warnings. Called from
`/execute-feature`, the number and URL are what it needs back.

---

## Rules

- Origin = traceability. It's blocked only for a release-candidate bug with the origin `Done`.
  Its `Status` and state are never touched.
- Every Bug enters at `Phase: Discovery` + `Status: Backlog`, Issue Type `Bug`, exactly one of
  `afk`/`hitl`. Never create sub-issues — that's `/iteration-plan`'s job.
- Every Bug carries a regression-test acceptance criterion.
- Never file the same Bug twice: duplicate check before every creation.
- Issue bodies and comments describe the fault, never the session or tooling. **No AI
  attribution** — no "Generated with Claude Code" line or similar anywhere.
