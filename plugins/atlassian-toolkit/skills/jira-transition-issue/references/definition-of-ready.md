# Definition of Ready

**Ready means anyone can start without asking a question.** A person or an AI agent should be able to take a `Ready` item, read only the item and its sub-tasks, and begin implementing. If they would have to ask, the item is not Ready.

## How to use this page

- Every criterion is a yes/no check. If it does not apply, write `N/A` and one line of reason in the Jira item. Never silently skip a criterion.
- There are **two gates**, matching the two refinement activities. Gate 1 is passed when leaving `In refinement` (item becomes `Refined`). Gate 2 is passed when leaving `Refined` (item becomes `Ready`).
- The gates apply to the parent item (Story, Bug, Task). Sub-tasks are produced by gate 2 and have their own checklist below.
- If a gate fails, the item stays where it is. It never moves forward with a promise to fix it later.

## Which gates apply to which type

| Type | Entry (Backlog) | Gate 1: Refined | Gate 2: Ready |
|---|---|---|---|
| **Story** | Required | Full | Full |
| **Bug** | Required, plus reproduction | Bug variant (analysis) | Full |
| **Task** | Required | Optional: only if something is unclear | Task variant (lighter) |
| **Sub-tasks** (5 types) | Created by gate 2 | Not applicable | Sub-task checklist |
| **Epic** | Required | Not applicable | Not applicable |

## Entry: creating an item in Backlog

The minimum for an item to exist. Without these, it is noise.

- **Summary** is a clear outcome in the imperative or as a user goal, not a vague area ("Add Stack construct with App-typed scope", not "Stacks").
- **Issue type** is correct (Story for user-visible value, Task for technical work with no story, Bug for a defect in existing behaviour).
- **Component** is set to exactly one component. If it spans several, it is too big: split it per component.
- **Parent** is set: Stories and Tasks belong to an Epic.
- **Source** is linked: the PRD page, the ADR or the conversation that originated it. If there is none, the item says why.
- **No duplicate**: a search by summary keywords found nothing equivalent.

## Gate 1: Refined (leaving `In refinement`)

The question answered here is **what exactly are we building, and how do we know it is right?** It is about the problem, not the code.

### 1. Traceability

- Traces back to an approved PRD, or says why there is none (then this criterion is `N/A` with that reason). The PRD is linked from the item and each requirement below cites the PRD requirement it comes from.
- Linked to its Epic.
- Component is set and still correct after analysis.

### 2. Value and scope

- The Story states who benefits and why: *As a \<who\>, I want \<what\>, so that \<why\>*. Tasks state the outcome they unlock.
- An explicit **Out of scope** list exists, naming things a reader might otherwise assume are included.
- **Small**: it can be implemented, reviewed and merged within five working days. More than 8 Story Points, or a Size of `XXL (EPIC - TOO BIG)`, means it must be split.
- **Independent**: it delivers value without waiting for an unfinished sibling, or the dependency is declared (see section 6).

### 3. Functional requirements

- Every functional requirement is extracted, numbered (`FR-1`, `FR-2`…) and written as an observable behaviour ("The system shall…").
- Each requirement is atomic: one behaviour per line, no "and/or".
- Inputs, outputs, error behaviour and default values are stated wherever they matter.

### 4. Non-functional requirements

Go through every category. Each one is either specified with a measurable target or marked `N/A` with a reason.

| Category | Question to answer |
|---|---|
| Performance | Is there a latency, throughput or size budget? |
| Reliability | What happens on failure, retry, partial failure, idempotency? |
| Security | New inputs, secrets, permissions, data exposure, dependencies? |
| Compatibility | Backward compatibility, supported versions, breaking changes? |
| Observability | Which logs, metrics or traces prove it works in production? |
| Operability | Configuration, deployment, rollback, runbook impact? |
| Cost | Any cloud or licence cost impact? |
| Maintainability | Conventions to follow, documentation to update? |

### 5. Acceptance criteria

- Written in Given / When / Then.
- Each criterion is **testable**: a test or a concrete manual check can pass or fail it. No vague words ("fast", "user-friendly", "robust", "properly").
- Covers the happy path, the edge cases (empty, maximum, duplicates) and the error cases.
- Every functional requirement is covered by at least one criterion, and every criterion maps back to a requirement.

### 6. Dependencies and unknowns

- Blockers are linked with *is blocked by*, including external ones (access, accounts, another component).
- **No unresolved technical unknown**. If something was unknown, a spike was done and its outcome is documented in the item.
- Every assumption is written down as `Assumption: …`. There are no open questions left.
- Any architectural decision this needs has an ADR, at least proposed.

### 7. Estimation and priority

- **Story Points** set with the Fibonacci scale (1, 2, 3, 5, 8).
- **Size** set, from `XXS (0,25D)` up to `XL (4D)`. `XXL (EPIC - TOO BIG)` is never acceptable at this gate.
- **Business Value** set as a number, so items can be ranked against each other.
- **Risk** set to 1, 5 or 10. A Risk of 10 records what could go wrong and how it is mitigated in the description.
- **Priority** set, with a one-line reason if it is High or Highest.

### 8. Change safety

- Decided whether it ships behind a **feature flag**: yes or no, the flag name, and that its default is off. Because the project uses trunk-based development, anything incomplete or risky merges dark.
- Data, schema or state migrations are identified, with their reversibility.
- Breaking changes are declared up front, with their migration path.

### Bug variant of gate 1

A Bug is a defect in existing behaviour, not new scope, so the variant is lighter. Replace sections 1, 2, 3 and 4 with an analysis. A Bug is refined when:

- **Component** is set and still correct after analysis. A PRD and an Epic are not required. The commit or PR that introduced the defect is linked when known; when it is unknown, nothing is needed.
- **Reproduction steps** are exact and a second person could follow them. Environment and versions are stated.
- **Expected** and **actual** behaviour are both written down.
- **Impact** and severity are assessed: who is affected, how often, whether there is a workaround.
- A **root cause** is identified, or a time-boxed investigation sub-task exists. A fix is never attempted before the cause is understood.
- **Affects version** is stated. While the project has no versions yet, saying so ("none yet") satisfies this, and so does naming the version when it does not exist in the project.
- **Non-functional requirements** take one line, for example `N/A for every category: defect fix, no new requirements`. If the fix has a real non-functional effect (performance, compatibility, security), name the category and its target.
- One acceptance criterion is the **regression test**: it fails today and must pass after the fix (section 5).

Sections 6 (dependencies and unknowns), 7 (estimation and priority) and 8 (change safety) apply as written: a fix can still break compatibility or need a migration.

## Gate 2: Ready (leaving `Refined`)

The question answered here is **how exactly do we build it in this codebase?** It is the output of the iteration plan and it needs the real repository open, not a guess.

### 1. Codebase analysis

- Done against the repository of the item's Component, at its current `main`.
- Affected modules and files are named by path.
- Existing code to **reuse** is named (functions, classes, patterns, test helpers) so nothing is reinvented.
- Interfaces and contracts that cross a boundary are written down: signatures, types, schemas, error shapes.

### 2. Sub-tasks exist

- The item is broken into **sub-tasks** in vertical slices where possible: each slice delivers something verifiable end to end, not a layer. Each sub-task has the issue type that matches its work (see the table below).
- Every sub-task satisfies the sub-task checklist below.
- Together the sub-tasks cover every acceptance criterion of the parent. Nothing is left without an owner.

### 3. Dependencies between sub-tasks

- Order is modelled with *blocks* / *is blocked by* links. No cycles.
- Independent sub-tasks are identified as parallelizable.
- The first executable sub-task is unblocked.

### 4. Test strategy

- It says which levels apply (unit, integration, end to end) and why.
- Every acceptance criterion is covered by at least one automated test, or by a named manual check with a reason.
- Fixtures, test data and any test infrastructure needed are identified.
- Sub-tasks that are suited to test-first work carry the `tdd` label (see below).

### 5. Rollout

- If the item uses a feature flag, there is a sub-task that creates it with default off, and a follow-up that removes it.
- Migration and rollback steps are sub-tasks, not footnotes.

### 6. Access and environment

- Everything needed is available: credentials, accounts, cloud resources, environments, third-party access. Anything missing is a sub-task with Mode **HITL**, placed first.

### 7. Documentation

- Documentation that must change is listed: README, API docs, ADR, runbook. Substantial changes are their own **Documentation** sub-task.

### 8. Consistency

- Sum of the sub-task estimates is consistent with the Story Points. If it is wildly off, the points or the plan are wrong.
- A comment on the parent summarizes the plan: the sub-tasks, the order, what is parallel, what is HITL.

## Sub-task checklist

A sub-task is **self-contained**. Someone who reads only the sub-task can start.

- **Goal**: one sentence on what is true when it is done.
- **Context**: the minimum background, with a link to the parent. No need to read the PRD to understand it.
- **Where**: exact file paths to create or change, each from the repository root with what changes in it. This includes the test files: a sub-task whose Tests section names a test but whose Files do not list that test's path is not ready. A directory alone, a module name or "the relevant files" is not a path. For an Analysis sub-task, the path or page where the finding is written counts; for an Architecture Design sub-task, the path of the ADR; for a Documentation sub-task, the path or page being changed.
- **How**: concrete implementation steps and the interface or signature to produce.
- **Acceptance**: the subset of the parent's criteria this sub-task satisfies.
- **Tests**: which tests to write and what they assert.
- **Estimate** in ideal hours, at most 8. Larger means split it.
- **Issue type** matches the work (Development, Automation, Analysis, Architecture Design or Documentation), **Mode** is set to AFK or HITL, and the `tdd` label is added when it applies.
- Component copied from the parent. Created in `Backlog`, the only initial status, and moved to `Ready` by the iteration plan once the whole set of sub-tasks passes gate 2.

### Sub-task types, Mode and the tdd label

| Where | Value | Use when |
|---|---|---|
| Issue type | **Development** | Implements functionality. With `tdd`, its unit tests live inside the same sub-task: never create a separate unit-test sub-task. |
| Issue type | **Automation** | Integration or end to end tests. Always its own sub-task, even when the rest is test-first. |
| Issue type | **Analysis** | Time-boxed technical spike. The output is a written finding, not merged code. Created when a requirement has real technical uncertainty. |
| Issue type | **Architecture Design** | Defines an interface or an architecture decision. Always HITL. |
| Issue type | **Documentation** | Writes or updates documentation, only when the Story needs it. |
| Field **Mode** | **AFK** | Fully specified, deterministic, verifiable by tests, no judgement call needed. Safe to hand to an agent unattended. |
| Field **Mode** | **HITL** | A human must be in the loop: design choices, ambiguous behaviour, security-sensitive change, credentials, production-like environments, anything that needs taste or authority. |
| Label | `tdd` | Logic that can be specified by tests first: pure functions, parsers, validators, state machines, bug fixes. Not for scaffolding, config or UI layout. |

## Task variant of gate 2

A small, obvious Task can go `Backlog → Ready` and skip refinement. It still needs:

- Entry checklist complete.
- Outcome and "done when" written in two to five lines, testable.
- Estimated at 3 Story Points or fewer. Anything bigger is a Story.
- Files to touch named, and the test approach stated.
- **Mode** set to AFK or HITL, and the `tdd` label when it applies. No sub-tasks needed unless it is bigger than one day.

## Send it back when

- A reviewer needs to ask what a criterion means.
- Acceptance criteria say "works", "is fast" or "as expected".
- The plan says "update the relevant files" without naming them.
- A sub-task lists a source file but not the test file its Tests section relies on, or lists a directory or module instead of file paths.
- A sub-task needs a decision that nobody has made. That decision is an **Architecture Design** sub-task of its own, with Mode HITL.
- The estimate moved by more than double once someone looked at the code. Refine again.

## Reviewing this page

Review after every ten items that go through a gate, or when the same criterion is repeatedly skipped or repeatedly causes rework. A criterion nobody ever fails is a candidate for removal. A defect that escaped is a candidate for a new criterion. Record changes in the pull request that edits this page.

Related: *Definition of Done*, *Process*.
