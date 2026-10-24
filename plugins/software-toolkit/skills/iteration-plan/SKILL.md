---
name: iteration-plan
description: Break a refined GitHub Feature (Status Ready, already processed by /refine-story) into technical sub-tasks — codebase analysis, TDD/branching decisions, native sub-issue hierarchy (addSubIssue) and dependencies (addBlockedBy), category and afk/hitl labels. Use whenever the user wants to plan an iteration, split a Feature into tasks, or break down ready work for implementation. Also runs unattended inside a GitHub Actions job (no human present) when a Feature's Status reaches Ready — trigger on "/iteration-plan", "iteration plan issue #N", "split this feature into tasks", "break down this feature", or any variation of turning a ready Feature into implementation sub-tasks.
context: fork
agent: iteration-plan
background: false
allowed-tools: Bash(gh issue *), Bash(gh api *), Bash(gh project *), Bash(gh repo *), Read, Grep, Glob, AskUserQuestion
---

# /iteration-plan — Split a Feature into Sub-tasks

Take a refined GitHub Feature (`Status: Ready`, already processed by `/refine-story`) and break
it into 4–8-hour technical sub-tasks, created as native sub-issues of the Feature with native
dependencies between them.

This skill runs in an isolated `iteration-plan` subagent with no visibility into the
conversation that triggered it — the Feature issue number (or none, to search for Ready
Features) arrives as the input and everything else is re-derived from GitHub and the local
codebase.

**This also runs unattended.** A Feature reaching `Status: Ready` is meant to trigger this skill
headless inside a GitHub Actions job, same as `/refine-story` reaching `Refining`. Read
`refine-story/SKILL.md`'s "Detecting headless execution" section — the same mechanism
(`GITHUB_ACTIONS`/`CI` env var, held for the whole run), the same two behavior changes apply
here (no `AskUserQuestion`, and no waiting for approval before creating sub-tasks — Step 7
becomes "publish directly" instead of "show and iterate"), **and the same rule that none of
this — headless detection, tool availability, session mechanics — ever gets written into a
sub-task body or comment.** Named assumptions are published as plain decisions about the work,
never as narration about how the run that produced them behaved.

---

## Step 1 — Resolve the Feature and gate

By issue number if given; otherwise search `Status: Ready` Features in the Project and ask the
user which one (headless: this skill should always be invoked with an explicit issue number in
that case — if it isn't, fail visibly rather than guessing which Feature to plan).

If `Status` is not `Ready`, same hard-stop handling as `refine-story` Step 1: report "cannot
plan — not `Ready`" and stop, human or headless, never a "proceed anyway?" question — this
Feature likely hasn't finished `/refine-story` yet, and this skill isn't the place to negotiate
that.

If the Project has an `Iteration` field, and this Feature isn't assigned to one that hasn't
started yet, warn — don't block.

---

## Step 2 — Gather context

Same pattern as `refine-story` Step 2: the Feature's own (already-refined) body, the parent
PRD's Success Criteria, and this issue's native blockers via `Issue.blockedBy` (see
`references/github.md`).

---

## Step 3 — Technical codebase analysis

Read `references/codebase-analysis-typescript.md` or `references/codebase-analysis-go.md`
(pick based on what's in the current repo — `package.json`/`tsconfig.json` vs. `go.mod`; ask
only if genuinely ambiguous and a human is present, otherwise pick by majority file extension)
and follow its two sub-processes: Technical Exploration, then Coverage and Gap Analysis. The
output feeds directly into sub-task descriptions in Step 6 — there's no separate design
document.

If the current working directory isn't a checkout of the Feature's repo, tell the user (or,
headless, fail visibly — codebase analysis can't proceed without the actual code).

---

## Step 4 — Test strategy and branching

Read `references/task-split.md` for the full rules. Two things to settle before splitting (TDD
is judged separately, per sub-task, in Step 5 — not here):

- **Integration tests needed?** With a human present, ask. Headless: assume yes by default
  (safer to over-cover than under-cover) unless the Feature's ACs are clearly pure-unit-scope,
  and record it as a named assumption. E2E testing is out of scope for this skill for now — don't
  ask about it, and don't fold it into this question; if a Feature clearly needs e2e coverage,
  note the gap in Step 9's report instead.
- **Branch name**: always `feature/<issue-number>-<kebab-title>` — this never depends on
  anything ambiguous, so never ask, human or headless.

---

## Step 5 — Draft the sub-task split

Using `references/task-split.md`'s sizing (4–8 ideal hours) and category rules, draft the list
of sub-tasks. Every sub-task gets:
- Exactly one category label: `development`, `automation`, `spike`, `architecture-design`, or
  `documentation`.
- Exactly one of `afk`/`hitl` — `architecture-design` is always `hitl`, no exceptions.
- A dependency list (which other draft sub-tasks block it) — check for cycles before presenting,
  same rule `prd-to-issues` follows; resolve any cycle yourself before Step 6.

For every `development` sub-task (never `automation`/`spike`/`architecture-design`/
`documentation` — see `references/task-split.md`), judge individually whether it's suited to
test-first development: does it have a clear, testable public interface, same criterion the
`tdd` skill itself uses (`deep-modules.md`/`interface-design.md`)? If yes, mark it for the `tdd`
label — this also decides, per `references/task-split.md`'s TDD-mode rule, whether a separate
unit-test sub-task is needed for it (TDD-marked sub-tasks write their own tests inline, so don't
draft a separate unit-test sub-task for one; non-TDD-marked ones may still need a sibling unit-
test sub-task). This replaces asking the user a single "TDD for the whole Feature?" question —
it's a per-sub-task call, not a Feature-wide mode.

---

## Step 6 — Show the proposal (or publish directly if headless)

**With a human present**: show the draft as a table (title / category / afk-hitl / hours /
depends-on) and the AC coverage check, iterate until approved — same loop as
`prd-to-issues` Step 3.

**Headless**: skip straight to Step 7 — publish directly, with every assumption from Step 4
visible in the final report (Step 9) for post-hoc review.

---

## Step 7 — Create the sub-tasks

Read `references/github.md` ("Creating sub-tasks", "Setting native sub-issue hierarchy and
dependencies") for the exact commands. For each sub-task, in dependency order (blockers first,
same requirement `prd-to-issues` has):

1. Write the body using `assets/task-template.md`, filling in the codebase-analysis findings
   from Step 3.
2. Create the issue in the Feature's own repo, Issue Type `Task`, with the category label, the
   `afk`/`hitl` label, and the `tdd` label if Step 5 marked it, added to the same Project and the
   same Milestone as the parent Feature, `Status = Backlog` — one combined `createIssue`
   mutation, same pattern `prd-to-issues` uses.
3. `addSubIssue` — link it as a native sub-issue of the parent Feature.
4. `addBlockedBy` for each dependency on an already-created sibling sub-task.

Hour estimates go in the sub-task body text only (the template's `Estimate: Xh` section) — never
in the Project's `Estimate` field, which `/refine-story` already uses for the parent Feature's
Story Points. Mixing the two units there would make the field meaningless.

**On any failure**: stop immediately, same rule as `prd-to-issues` — report exactly which
sub-tasks were created/linked and which weren't, never roll back silently.

---

## Step 8 — Verify AC coverage

Cross-check that every AC on the parent Feature is covered by at least one sub-task (from the
FR → AC → module map built in Step 3). Note any gap in the final report — don't silently drop
an uncovered AC.

---

## Step 9 — Report

Tell the user (or, headless, make sure it's all in the session comment / sub-task bodies
themselves): the branch name, total estimated hours vs. the parent Feature's `Estimate` (Story
Points), the count by category and by AFK/HITL, which sub-tasks got the `tdd` label, the
dependency graph, and AC coverage. If any AC genuinely needs e2e coverage (crosses a deployed-
service or UI boundary that integration tests alone can't reach), flag it explicitly as an
out-of-scope gap — e2e sub-task creation isn't something this skill does yet.

Warn if total hours exceed the threshold for the Feature's `Size`: **XS ≤ 4h, S ≤ 8h, M ≤ 16h,
L ≤ 32h, XL → always suggest considering splitting the Feature itself** rather than just its
sub-tasks.

---

## Rules

- Never create a sub-task without exactly one category label and exactly one of `afk`/`hitl`.
- `architecture-design` sub-tasks are always `hitl` — no exceptions.
- Only `development` sub-tasks are ever eligible for the `tdd` label — judged per sub-task on
  whether it has a clear testable public interface, never asked as one Feature-wide question.
  A sub-task carrying `tdd` means whoever implements it is expected to pick up the `tdd` skill
  at that point — don't mark one `tdd` without that genuinely being true.
- Sub-tasks are always native GitHub sub-issues (`addSubIssue`) of the parent Feature — never
  just text-referenced.
- Hour estimates live only in the sub-task body text — never in the Project's `Estimate` field.
- Headless execution is a first-class path through every step, same as `refine-story` — design
  and run against it, don't treat it as an edge case.
- Detect and resolve dependency cycles before presenting or creating anything.
- On partial failure during creation, stop and report — never silently continue and never
  auto-roll-back.
- Never drop an AC that ends up with no covering sub-task — surface it in the report instead.
- Never publish anything about `AskUserQuestion`, headless detection, or session/tooling
  mechanics into a sub-task body or comment — write assumptions as plain decisions about the
  work, never as narration about how or why the run produced them. Holds regardless of who or
  what executed the skill.
