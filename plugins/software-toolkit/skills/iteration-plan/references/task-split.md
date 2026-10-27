# Task Split — Iteration Plan

Rules and guidelines for splitting a Feature into sub-tasks.

---

## Sub-task categories

Every sub-task is created as Issue Type `Task` (generic, same type for all of them — see
`references/github.md`), with exactly one of these category labels:

| Category label | Mode |
|---------------|------|
| `development` — functional implementation | AFK (usually) |
| `development` or `automation` — unit tests (non-TDD only) | AFK |
| `automation` — integration tests | AFK |
| `spike` — technical investigation | HITL |
| `architecture-design` — interface / architecture decision | HITL (always) |
| `documentation` | AFK or HITL |

Plus exactly one of the existing `afk`/`hitl` labels (same label pair `prd-to-issues` already
uses) — the category label says *what kind* of work it is, the `afk`/`hitl` label says whether
it needs a human. `development` sub-tasks additionally get the `tdd` label when judged suitable
(see "TDD vs. non-TDD" below) — it says *how* to build it, orthogonal to the other two.

---

## TDD vs. non-TDD

This is a **per-sub-task** judgment made in `SKILL.md` Step 5 — not a single yes/no asked once
for the whole Feature. For every `development` sub-task, decide whether it has a clear, testable
public interface (same criterion the `tdd` skill itself applies — see its `deep-modules.md`/
`interface-design.md`). If yes, mark it with the `tdd` label and put it in TDD mode below; if
not (it's too exploratory, or the interface isn't settled yet — which usually means it should
have been a `spike` or `architecture-design` sub-task instead), leave it in non-TDD mode.

With a human present, this can be confirmed via `AskUserQuestion` alongside the rest of the
proposal in `SKILL.md` Step 6. Headless, it's decided unilaterally here and recorded as a named
assumption in the sub-task body (same mechanism as everywhere else in this pipeline) rather than
asked.

### TDD mode (sub-task carries the `tdd` label)
- Unit tests are written **before** the implementation, in the **same sub-task** — the assignee
  picks up the `tdd` skill when they start it
- Sub-task title: `Implement <feature> (TDD)` — tests implicit
- Category label: `development`
- **Do NOT** create a separate unit-test sub-task

### Non-TDD mode (sub-task does not carry the `tdd` label)
- Implementation and unit tests can be separate sub-tasks
- Implementation sub-task: category `development`, AFK
- Unit test sub-task: category `development` or `automation`, AFK
- The test sub-task must reference the implementation sub-task it covers

### Integration tests — always separate

Regardless of TDD:
- Integration tests cross component or layer boundaries
- Always a dedicated sub-task, category `automation`
- Depends on all relevant functional sub-tasks being complete
- These are written **after** the functional implementation exists

**E2E testing is out of scope for now** — this pipeline doesn't create e2e sub-tasks. Don't
treat `automation` as covering e2e; if a Feature genuinely needs e2e coverage, that's a gap to
note in the report (`SKILL.md` Step 9), not something to fold into an integration sub-task.

---

## Task sizing

Target: **4–8 ideal hours per sub-task** (~1 task per developer per day).

| Size | Hours | Guidance |
|------|-------|----------|
| Too small | < 2h | Merge with a related sub-task |
| Right | 2–8h | Proceed |
| Too large | > 8h | Split further |

A task is too large if it touches more than 3–4 files or covers more than 3 distinct ACs.
When in doubt, split — smaller tasks flow better through the iteration.

---

## AFK vs. HITL classification

**AFK (Away From Keyboard)** — an agent or developer can execute this sub-task to completion
without human input, given only the sub-task description:
- Implementation of a well-specified function or module
- Writing unit or integration tests for a concrete AC
- Wiring a CLI command to existing logic
- Documentation of a finished feature

**HITL (Human In The Loop)** — a human must review, decide, or sign off at some point:
- Defining a public interface or API contract (impacts other code or consumers)
- Architecture decisions with multiple valid approaches
- Spikes where the result requires team discussion before proceeding
- Any sub-task that could break external consumers

When a sub-task is HITL, note the reason in the description so the assignee knows
what decision is expected of them.

---

## Dependency rules

Dependencies between sub-tasks follow natural implementation order:

- **Functional → Wiring**: the feature must exist before it can be wired into the CLI
- **Functional → Unit tests** (non-TDD): implementation before test sub-task
- **All Functional → Integration tests**: all components must exist before cross-component tests
- **Spike → Placeholder**: resolve the spike before estimating the implementation

Represent dependencies as native GitHub issue dependencies (`addBlockedBy`, created in Step 8 of
`SKILL.md`, same mechanism `prd-to-issues` already uses):
- Sub-task A blocking sub-task B means B cannot start until A is done

Do not add dependencies that are not real blockers — unnecessary ordering slows the iteration.

---

## Branching convention

One branch per Feature, not per sub-task:

```
feature/<issue-number>-<kebab-short-title>
# e.g. feature/42-plan-command-entry-point
```

All sub-tasks are implemented and committed on this branch, which `/execute-feature` creates
from the base branch (`next` — the integration branch; `main` only ever receives `next`). The PR
is opened against that base branch and is always merged by a human. A `Bug` uses
`bugfix/<issue-number>-<kebab-short-title>` instead.

Sub-tasks track progress within the branch — they are not separate deployment units.

---

## Spike sub-tasks

Use a spike when a FR or AC has no clear implementation path after codebase exploration:

1. Create a **spike sub-task** (category `spike`, HITL):
   - Title: `Spike: investigate <unknown>`
   - Timebox: 2–4 hours
   - Goal: answer a specific question (stated in the description)
   - Output: a concrete recommendation, not just findings

2. Create a **placeholder sub-task** (category `development`):
   - Title: `[Pending spike] Implement <feature>`
   - Mark it blocked by the spike (`addBlockedBy`)
   - Include a rough hour estimate with `(TBD after spike)` note

After the spike, update the placeholder's description and estimate before implementation starts.

---

## Principles

- Sub-tasks are not allocated during iteration planning — devs self-assign when the iteration
  starts
- Estimations are in ideal hours, not story points (story points are what `refine-story` sets on
  the parent Feature's `Estimate` field — don't mix the two units)
- Task estimating is a team endeavor — avoid individual estimates during planning, with a human
  present
- Include only work that adds direct value: implementation, tests, design, relevant project
  decisions
- Do not include admin tasks (email, unrelated meetings, general overhead)
- The right size is ~1 task per developer per day; larger tasks create bottlenecks
- Some design discussion during iteration planning is appropriate — deep architectural analysis
  is not (that's what the `architecture-design` category/HITL is for)
