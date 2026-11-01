# Definition of Ready

Source of truth for the gates `jira-transition-issue` applies on the way to `Refined` and
`Ready`. The Confluence page `Definition of Ready` (223281170) is a mirror for people to read:
it is generated from this file, never edited by hand.

**Ready means anyone can start without asking a question.** A person or an AI agent can take a
`Ready` item, read only the item and its sub-tasks, and begin implementing.

## How to apply

- Every criterion is a yes/no check. If it does not apply, the issue says `N/A` and a one-line
  reason. A criterion that is silently missing **fails**.
- Two gates. **Gate 1** is passed when leaving `In refinement` (the item becomes `Refined`).
  **Gate 2** is passed when leaving `Refined` (the item becomes `Ready`).
- The gates apply to the parent item (Story, Bug, Task). Sub-tasks are produced by Gate 2 and
  have their own checklist.
- If a gate fails the item stays where it is. It never moves forward with a promise to fix it
  later.

## Which gates apply to which type

| Type | Entry (Backlog) | Gate 1: Refined | Gate 2: Ready |
|---|---|---|---|
| Story | required | full | full |
| Bug | required, plus reproduction | bug variant | full |
| Task | required | optional, only if something is unclear | task variant (lighter) |
| Sub-task (5 types) | created by Gate 2 | not applicable | sub-task checklist |
| Epic | required | not applicable | not applicable |

## Entry: creating an item in Backlog

- **Summary** is a clear outcome in the imperative or as a user goal, not a vague area.
- **Issue type** is correct: Story for user-visible value, Task for technical work with no
  story, Bug for a defect in existing behaviour.
- **Component** is exactly one. If it spans several, split it per component.
- **Parent** is set: Stories and Tasks belong to an Epic.
- **Source** is linked: a Jira remote link to the PRD, ADR or page that originated it, or a
  `No PRD: <reason>` line in the description.
- **No duplicate**: a search by summary keywords found nothing equivalent.

## Gate 1: Refined (leaving `In refinement`)

Question answered: *what exactly are we building, and how do we know it is right?*

### 1. Traceability
- Traces back to an **approved** PRD: the PRD is a Jira remote link on the issue (or on its
  Epic) and the Status row of its Confluence page reads `APPROVED`. With `No PRD: <reason>` this is
  `N/A` and the reason must be in the issue.
- Each requirement cites the PRD requirement it comes from (`Requirements covered`).
- Linked to its Epic (the `parent` field).
- Component is set and still correct after analysis.

### 2. Value and scope
- The Story states who benefits and why: *As a / I want / so that*. Tasks state the outcome.
- An explicit **Out of scope** list exists.
- **Small**: mergeable in five working days. More than 8 Story Points, or Size
  `XXL (EPIC - TOO BIG)`, means it must be split.
- **Independent**: it delivers value without waiting for an unfinished sibling, or the
  dependency is declared (section 6).

### 3. Functional requirements
- Every functional requirement is extracted, numbered (`FR-1`, `FR-2`…) and written as an
  observable behaviour ("The system shall…").
- Each is atomic: one behaviour per line, no "and/or".
- Inputs, outputs, error behaviour and defaults are stated where they matter.

### 4. Non-functional requirements
Every category is either specified with a measurable target or marked `N/A` with a reason:
performance, reliability, security, compatibility, observability, operability, cost,
maintainability.

### 5. Acceptance criteria
- Given / When / Then.
- Each is testable: no "fast", "user-friendly", "robust", "properly".
- Covers the happy path, the edge cases (empty, maximum, duplicates) and the error cases.
- Every functional requirement is covered by at least one criterion and every criterion maps
  back to a requirement.

### 6. Dependencies and unknowns
- Blockers are linked with *is blocked by*, including external ones.
- **No unresolved technical unknown.** If something was unknown, a spike was done and its
  outcome is in the item.
- Every assumption is written as `Assumption: …`. No open questions remain.
- Any architectural decision this needs has an ADR, at least `PROPOSED` (its Status row exists).

### 7. Estimation and priority
- **Story Points** set, Fibonacci (1, 2, 3, 5, 8).
- **Size** set, from `XXS (0,25D)` to `XL (4D)`. `XXL` is never acceptable here.
- **Business Value** set as a number.
- **Risk** set to 1, 5 or 10. A Risk of 10 records what could go wrong and the mitigation.
- **Priority** set, with a one-line reason if High or Highest.

### 8. Change safety
- Feature flag decided: yes or no, its name, and that its default is off.
- Data, schema or state migrations identified, with their reversibility.
- Breaking changes declared up front, with their migration path.

### Bug variant of Gate 1

A Bug is a defect in existing behaviour, not new scope, so the variant is lighter. It
**replaces sections 1, 2, 3 and 4** with the analysis below and keeps sections 5 to 8.

**Replaces section 1, Traceability.** A PRD and an Epic are not required.
- **Component** is set and still correct after analysis.
- The **origin** is linked when known (the issue or PR that introduced it). When it is unknown,
  nothing is needed: no link and no line saying so.

**Replaces sections 2 and 3, scope and requirements.** A Bug is refined when:
- **Reproduction steps** are exact and a second person could follow them; environment and
  versions are stated.
- **Expected** and **actual** behaviour are both written down.
- **Impact** and severity are assessed: who, how often, any workaround.
- A **root cause** is identified, or a time-boxed investigation sub-task exists. A fix is never
  attempted before the cause is understood.
- **Affects version** is set. While the project has no versions yet, `Affects version: none
  yet` in the Environment section satisfies this, and so does a version written in the
  Environment text when the version does not exist in the project.

**Replaces section 4, Non-functional requirements.** One line is enough, for example `N/A for
every category: defect fix, no new requirements`. If the fix has a real non-functional effect
(performance, compatibility, security), name the category and the target.

**Kept from the full Gate 1:**
- Section 5, **Acceptance criteria**, with one criterion that is the **regression test**: it
  fails today and must pass after the fix.
- Section 6, **Dependencies and unknowns**: blockers, no unresolved unknown, `Assumption:` lines.
- Section 7, **Estimation and priority**: Story Points, Size, Business Value, Risk, Priority.
- Section 8, **Change safety**: a fix can still break compatibility or need a migration.

## Gate 2: Ready (leaving `Refined`)

Question answered: *how exactly do we build it in this codebase?* It is the output of the
iteration plan and needs the real repository.

### 1. Codebase analysis
- Done against the Component's repository at its current `main`.
- Affected modules and files are named by path.
- Existing code to **reuse** is named.
- Interfaces and contracts that cross a boundary are written down.

### 2. Sub-tasks exist
- Broken into sub-tasks in vertical slices where possible, each with the issue type that
  matches its work.
- Every sub-task satisfies the sub-task checklist.
- Together they cover every acceptance criterion of the parent.

### 3. Dependencies between sub-tasks
- Order modelled with *blocks* / *is blocked by*. No cycles.
- Independent sub-tasks are identified as parallelizable.
- The first executable sub-task is unblocked.

### 4. Test strategy
- Levels stated (unit, integration, end to end) and why.
- Every acceptance criterion is covered by an automated test or a named manual check.
- Fixtures, test data and infrastructure are identified.
- Sub-tasks suited to test-first work carry the `tdd` label.

### 5. Rollout
- With a feature flag: a sub-task creates it (default off) and a follow-up removes it.
- Migration and rollback steps are sub-tasks, not footnotes.

### 6. Access and environment
- Everything needed is available. Anything missing is a sub-task with Mode **HITL**, placed
  first.

### 7. Documentation
- Documentation that must change is listed. Substantial changes are their own
  **Documentation** sub-task.

### 8. Consistency
- The sum of the sub-task estimates is consistent with the Story Points. Wildly off means the
  points or the plan are wrong.
- A comment on the parent summarizes the plan: sub-tasks, order, what is parallel, what is
  HITL.

## Sub-task checklist

A sub-task is **self-contained**.
- **Goal**: one sentence on what is true when it is done.
- **Context**: the minimum background, with a link to the parent.
- **Where**: every file to create or change, each as a path from the repository root with what
  changes in it. This **includes the test files**: a sub-task whose Tests section names a test
  but whose Files section does not list that test's path fails. A directory alone, a module name
  or "the relevant files" is not a path. For an Analysis sub-task the path or page where the
  finding is written counts; for an Architecture Design sub-task, the path of the ADR; for a
  Documentation sub-task, the path or page being changed.
- **How**: concrete steps and the interface or signature to produce.
- **Acceptance**: the subset of the parent's criteria it satisfies.
- **Tests**: which tests to write and what they assert.
- **Estimate** in ideal hours, at most 8.
- **Issue type** matches the work, **Mode** is AFK or HITL, `tdd` when it applies.
- Component copied from the parent. Created in `Backlog`; moved to `Ready` by the iteration
  plan once the whole set passes Gate 2.

### Sub-task types, Mode and the tdd label

| Where | Value | Use when |
|---|---|---|
| Issue type | Development | Implements functionality. With `tdd`, unit tests live in the same sub-task |
| Issue type | Automation | Integration or end to end tests. Always its own sub-task |
| Issue type | Analysis | Time-boxed spike. The output is a written finding, not merged code |
| Issue type | Architecture Design | Interface or architecture decision. Always HITL |
| Issue type | Documentation | Writes or updates documentation, only when the Story needs it |
| Field Mode | AFK | Fully specified, deterministic, verifiable by tests, no judgement call |
| Field Mode | HITL | A human must be in the loop: design choices, ambiguity, security, credentials, production-like environments |
| Label | `tdd` | Logic specifiable by tests first: pure functions, parsers, validators, state machines, bug fixes. Not scaffolding, config or UI layout |

## Task variant of Gate 2

A small, obvious Task can go `Backlog → Ready` and skip refinement. It still needs:
- Entry checklist complete.
- Outcome and "done when" in two to five lines, testable.
- At most 3 Story Points. Bigger is a Story.
- Files to touch named, and the test approach stated.
- **Mode** set to AFK or HITL, and `tdd` when it applies. No sub-tasks needed unless it is
  bigger than one day.

## Send it back when

- A reviewer needs to ask what a criterion means.
- Acceptance criteria say "works", "is fast" or "as expected".
- The plan says "update the relevant files" without naming them.
- A sub-task lists a source file but not the test file its Tests section relies on, or lists a
  directory or module instead of file paths.
- A sub-task needs a decision nobody has made: that is an Architecture Design sub-task, HITL.
- The estimate moved by more than double once someone looked at the code.
