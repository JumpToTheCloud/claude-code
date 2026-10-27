---
name: iteration-plan
description: Break a refined GitHub Feature (Status Ready + Phase Discovery, already processed by /refine-story) into technical sub-tasks — codebase analysis, TDD/branching decisions, native sub-issue hierarchy (addSubIssue) and dependencies (addBlockedBy), category and afk/hitl labels — then moves the Feature itself to Status Ready + Phase Execution, the signal a separate execution orchestrator picks up to run the whole Feature. Use whenever the user wants to plan an iteration, split a Feature into tasks, or break down ready work for implementation. Also runs unattended inside a GitHub Actions job (no human present) when a Feature reaches that Status+Phase combination — trigger on "/iteration-plan", "iteration plan issue #N", "split this feature into tasks", "break down this feature", or any variation of turning a ready Feature into implementation sub-tasks.
context: fork
agent: iteration-plan
background: false
allowed-tools: Bash(gh issue *), Bash(gh api *), Bash(gh project *), Bash(gh repo *), Read, Grep, Glob, AskUserQuestion
---

# /iteration-plan — Split a Feature into Sub-tasks

Take a refined GitHub Feature (`Status: Ready` **and** `Phase: Discovery` — already processed
by `/refine-story`) and break it into 4–8-hour technical sub-tasks, created as native sub-issues
of the Feature with native dependencies between them. Once every sub-task exists, this skill
moves the Feature itself to `Status: Ready` + `Phase: Execution` — the same `Status` value as
before, but a different `Phase` entirely changes what it means: the execution orchestrator,
`/execute-feature`, treats *that* specific combination (`Ready` + `Execution` + Issue Type
`Feature`) as "pick up this whole Feature and execute it" — it reads the Feature's sub-issues
and works through them in dependency order, rather than anything in this skill dispatching
per-sub-task work itself.

This skill runs in an isolated `iteration-plan` subagent with no visibility into the
conversation that triggered it — the Feature issue number (or none, to search for Ready
Discovery-phase Features) arrives as the input and everything else is re-derived from GitHub and
the local codebase.

**This also runs unattended.** A Feature reaching `Status: Ready` + `Phase: Discovery` is meant
to trigger this skill headless inside a GitHub Actions job, same as `/refine-story` reaching
`Refining`. Read
`refine-story/SKILL.md`'s "Detecting headless execution" section — the same mechanism
(`GITHUB_ACTIONS`/`CI` env var, held for the whole run), the same two behavior changes apply
here (no `AskUserQuestion`, and no waiting for approval before creating sub-tasks — Step 7
becomes "publish directly" instead of "show and iterate"), **and the same rule that none of
this — headless detection, tool availability, session mechanics — ever gets written into a
sub-task body or comment.** Named assumptions are published as plain decisions about the work,
never as narration about how the run that produced them behaved.

---

## Step 1 — Resolve the Feature and gate

By issue number if given; otherwise search for Features with `Status: Ready` **and** `Phase:
Discovery` in the Project and ask the user which one (headless: this skill should always be
invoked with an explicit issue number in that case — if it isn't, fail visibly rather than
guessing which Feature to plan).

This skill only ever runs on that exact combination — `Status: Ready` **and** `Phase:
Discovery`. Checking `Status` alone isn't enough: once a Feature has already been through this
skill, it sits at `Status: Ready` again but with `Phase: Execution` (Step 7b) — same `Status`
value, different meaning entirely, reserved for the execution orchestrator, not this skill. Any
combination other than `Ready`+`Discovery` is a hard stop, human or headless, no "proceed
anyway?" question: report "cannot plan — not `Ready`/`Discovery`" and stop — this Feature either
hasn't finished `/refine-story` yet, or has already been broken down.

Set `Status = Planning` immediately once the gate passes (best-effort — missing option = warn
and skip, never block) — same pattern `/refine-story` uses for `Refining`, so the board shows
something is actively working on this Feature's breakdown.

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
   same Milestone as the parent Feature, `Status = Ready`, `Phase = Execution` — one combined
   `createIssue` mutation, same pattern `prd-to-issues` uses. Sub-tasks are born `Ready`, not
   `Backlog`: the task template already makes each one fully self-contained (interface
   contracts, phases, pattern to follow, ACs covered), so there's no separate "refine a
   sub-task" step for anything to wait on. `Phase = Execution` from the moment of creation, not
   inherited `Discovery` from the parent — a sub-task is itself an execution-phase unit of work,
   even while its parent Feature is still at `Phase: Discovery` until Step 7b below.
3. `addSubIssue` — link it as a native sub-issue of the parent Feature.
4. `addBlockedBy` for each dependency on an already-created sibling sub-task.

Hour estimates go in the sub-task body text only (the template's `Estimate: Xh` section) — never
in the Project's `Estimate` field, which `/refine-story` already uses for the parent Feature's
Story Points. Mixing the two units there would make the field meaningless.

**On any failure**: stop immediately, same rule as `prd-to-issues` — report exactly which
sub-tasks were created/linked and which weren't, never roll back silently.

---

## Step 7b — Move the Feature to Execution

Only once every sub-task above was created and linked successfully (never on a partial
failure — see above): move the parent Feature itself to `Status = Ready` + `Phase = Execution`.

This is the one signal this skill hands off to whatever picks up next — `/execute-feature`
watches for Issue Type `Feature` + `Phase: Execution` + `Status: Ready` and treats it as "this
Feature is fully broken down, go execute it end to end" (reading its sub-issues and working
through them in dependency order). Setting that orchestrator's own "I've claimed this" lock
(flipping `Status` to `In progress` once it starts) is entirely `/execute-feature`'s
responsibility, not this one's — this skill's job ends at handing off a clean, complete signal,
not at managing what happens after.

---

## Step 8 — Verify AC coverage

Cross-check that every AC on the parent Feature is covered by at least one sub-task (from the
FR → AC → module map built in Step 3). Note any gap in the final report — don't silently drop
an uncovered AC.

---

## Step 8b — Reconcile `Size` against the real split

Sum every sub-task's `Estimate: Xh` (the body text one, never the Project field). Compare that
total against these thresholds: **XS ≤ 4h, S ≤ 8h, M ≤ 16h, L ≤ 32h**.

Find the smallest option that actually covers the total. If that's **larger** than the
Feature's current `Size` (or `Size` was never set), update the Project's `Size` field to it —
the split just produced better information than whatever `Size` was set from before actually
seeing the breakdown, so let it correct the record rather than silently diverging from it. Never
shrink `Size` down, even if the total comes out smaller than expected — a lower total isn't a
correctness problem the same way a higher one is, and `/refine-story`'s own judgment on the
smaller side isn't this skill's to second-guess.

If the total still exceeds even `XL`'s range (> 32h), there's no larger option to move to —
leave `Size` at `XL` and instead flag in the report (Step 9) that the Feature itself is
probably too big and should be reconsidered for splitting, same spirit as the old threshold
check this step replaces.

Best-effort like every other field write in this pipeline: if `Size` has no options or can't be
resolved, warn and skip — never block the rest of the report over it.

---

## Step 9 — Report

Tell the user (or, headless, make sure it's all in the session comment / sub-task bodies
themselves): the branch name, total estimated hours vs. the parent Feature's `Estimate` (Story
Points), the count by category and by AFK/HITL, which sub-tasks got the `tdd` label, the
dependency graph, AC coverage, the Feature's final `Status: Ready` + `Phase: Execution` (Step
7b), and whether `Size` was corrected in Step 8b (from what, to what, and why). If any AC
genuinely needs e2e coverage (crosses a deployed-service or UI boundary that integration tests
alone can't reach), flag it explicitly as an out-of-scope gap — e2e sub-task creation isn't
something this skill does yet.

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
- Every sub-task is created at `Status: Ready` + `Phase: Execution` directly — never `Backlog`,
  never inherited `Discovery`. The parent Feature only reaches `Phase: Execution` itself once
  every sub-task exists (Step 7b) — don't flip the Feature's `Phase` early, and don't leave
  sub-tasks behind at `Discovery` once it does.
- This skill only ever runs on `Status: Ready` + `Phase: Discovery` together — checking `Status`
  alone is not enough, since the same `Status: Ready` value means something entirely different
  once `Phase` is `Execution` (reserved for the execution orchestrator, not this skill).
- Hour estimates live only in the sub-task body text — never in the Project's `Estimate` field.
- `Size` gets corrected **upward only** once the real split is known (Step 8b) — to the
  smallest option that covers the actual total hours, never shrunk back down, and never past
  `XL` (which has no larger option to move to; flag the Feature as probably needing a split
  instead).
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
