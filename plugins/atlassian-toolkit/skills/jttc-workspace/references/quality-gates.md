# Quality gates: Definition of Ready and Definition of Done

**These are summaries.** The authoritative text lives in Confluence and is edited there. Read
the live page before applying a gate.

| Page | ID | Under |
|---|---|---|
| Definition of Ready | `223281170` | Platform → Process |
| Definition of Done | `223281157` | Platform → Process |

Every criterion is a yes/no check. If one does not apply, write `N/A` plus a one-line reason in
the Jira item. Never skip silently. If a gate fails, the item stays where it is.

## Contents

- [Definition of Ready: two gates](#definition-of-ready-two-gates): entry, gate 1 (Refined), gate 2 (Ready), bug and task variants, sub-task checklist
- [Sub-task types, Mode and the tdd label](#sub-task-types-mode-and-the-tdd-label)
- [Definition of Done](#definition-of-done): universal, Story, Bug, Epic, additions by component type, special cases, never acceptable

## Definition of Ready: two gates

Maps to the two refinement activities. The test of Ready: **a person or an AI agent can take
the item, read only it and its sub-tasks, and start without asking a question.**

| Type | Entry (Backlog) | Gate 1: Refined | Gate 2: Ready |
|---|---|---|---|
| Story | required | full | full |
| Bug | required + reproduction | bug variant (analysis) | full |
| Task | required | optional, only if unclear | task variant (lighter) |
| Sub-task | created by gate 2 | n/a | sub-task checklist |
| Epic | required | n/a | n/a |

**Entry (creating in Backlog).** Clear outcome in the summary; correct issue type; exactly one
Component; Parent set (Stories and Tasks belong to an Epic); source linked (PRD, ADR);
no duplicate.

**Gate 1: Refined** (leaving `In refinement`). Answers *what exactly are we building and how do
we know it is right?*
1. Traceability: traces to an approved PRD, linked to its Epic, Component correct.
2. Value and scope: *As a / I want / so that*; explicit **Out of scope**; small (mergeable in
   five working days, at most 8 Story Points, Size never `XXL`); independent.
3. Functional requirements: extracted, numbered `FR-n`, atomic, observable behaviour.
4. Non-functional requirements: every category answered or marked `N/A` with a reason
   (performance, reliability, security, compatibility, observability, operability, cost,
   maintainability).
5. Acceptance criteria: Given/When/Then, testable (no "fast", "robust"), happy path + edge +
   error cases, each mapped to a requirement and every requirement covered.
6. Dependencies and unknowns: blockers linked, no unresolved technical unknown (a spike is
   done and documented), assumptions written as `Assumption: …`, ADR at least proposed.
7. Estimation: Story Points, Size, Business Value, Risk (1/5/10), Priority.
8. Change safety: feature flag decided (name, default off), migrations and breaking changes
   identified.

**Bug variant of gate 1.** Exact reproduction steps and environment; expected vs actual;
impact and severity; a root cause (or a time-boxed investigation sub-task); Affects version;
one acceptance criterion that is the **regression test**.

**Gate 2: Ready** (leaving `Refined`). Answers *how exactly do we build it in this codebase?*
It is the output of the iteration plan and needs the real repository open.
1. Codebase analysis against the Component's repo at current `main`: files named by path,
   code to reuse named, boundary contracts written down.
2. Sub-tasks exist, in vertical slices, each with the issue type that matches its work, and
   together they cover every acceptance criterion.
3. Dependencies modelled with blocks / is blocked by, no cycles, parallelizable ones identified.
4. Test strategy: levels stated, every AC covered by a test or a named manual check, fixtures
   identified, `tdd` label where suited.
5. Rollout: flag-creation sub-task (default off) plus a removal follow-up; migration and
   rollback as sub-tasks.
6. Access and environment available; anything missing is a HITL sub-task placed first.
7. Documentation that must change is listed.
8. Sum of sub-task estimates consistent with the Story Points; a comment on the parent
   summarizes the plan.

**Sub-task checklist.** Self-contained: goal, minimal context, exact file paths, concrete steps
and signatures, the acceptance criteria it satisfies, tests to write, estimate in ideal hours
(**at most 8**), issue type matching the work, **Mode** AFK or HITL, `tdd` when it applies,
Component copied from the parent. Created in `Backlog` and moved to `Ready` by the iteration
plan when the whole set passes gate 2.

**Task variant of gate 2.** Entry complete; outcome and "done when" in 2 to 5 lines; at most 3
Story Points (bigger is a Story); files to touch named; Mode set.

**Send it back when** a criterion needs explaining, an AC says "works", the plan says "update
the relevant files", a sub-task needs an undecided decision (that is an Architecture Design
sub-task, HITL), or the estimate moved by more than double once the code was read.

### Sub-task types, Mode and the tdd label

| Where | Value | Use when |
|---|---|---|
| Issue type | Development | Implements functionality. With `tdd`, unit tests live in the same sub-task: never a separate unit-test sub-task. |
| Issue type | Automation | Integration or e2e tests. Always its own sub-task. |
| Issue type | Analysis | Time-boxed spike; output is a written finding. |
| Issue type | Architecture Design | Interface or architecture decision. Always HITL. |
| Issue type | Documentation | Only when the Story needs it. |
| Field Mode | AFK | Fully specified, deterministic, verifiable by tests, no judgement call. Safe for an agent unattended. |
| Field Mode | HITL | A human must be in the loop: design choices, ambiguity, security-sensitive change, credentials, production-like environments. |
| Label | `tdd` | Logic specifiable by tests first: pure functions, parsers, validators, state machines, bug fixes. Not scaffolding, config or UI layout. |

## Definition of Done

**Done means merged into `main`, safe, and left in a state nobody has to come back to.** It does
not mean released (GitHub tracks releases and deployments) and does not mean the feature flag is
on. Move to `Done` only after the PR is merged. Checklists are layered: sub-task, then Story,
Bug or Epic, then the component-type additions.

**Universal (every sub-task and pull request).**
- *Code:* does what the goal says; lint, format and type-check pass with no new warnings or
  suppressions; no dead or commented-out code; every TODO points to a Jira key; reused the
  utilities the plan named.
- *Tests:* `tdd` sub-tasks were test-first; new logic has unit tests, boundaries have
  integration tests; tests assert behaviour; coverage of changed code at least 80% and overall
  does not drop; no flaky, skipped or weakened tests; all green locally and in CI.
- *Version control:* branch `<type>/<JIRA-KEY>-short-slug` from an up-to-date `main`;
  Conventional Commits, atomic, with the Jira key; breaking changes marked with `!` or a
  `BREAKING CHANGE:` footer; short-lived branch.
- *PR and review:* PR title is a Conventional Commit; description says what, why and how to
  verify, and links the Jira item; author self-reviewed; at least one review pass by someone
  other than the author (human or the code-review tool), blocking findings resolved; a HITL
  sub-task had a human review.
- *CI:* every required check green on the latest commit; up to date with `main`.
- *Security:* no secrets or personal data anywhere; input validated at boundaries; every new
  dependency justified, license-compatible and pinned; least-privilege permissions.
- *Documentation:* README and API docs updated; ADR for any architectural decision, linked
  from the PR; runbook updated if operations changed.
- *Jira hygiene:* PR linked; closing comment with the outcome and any deviation; effort off by
  more than double the estimate is noted; Flagged cleared and no open blocker.

**Story, on top.** All sub-tasks Done; every acceptance criterion verified with evidence;
non-functional requirements verified or recorded; works end to end on integrated `main`;
feature flag exists with default **off** and its removal is tracked; no open Bug blocks it; the
PRD requirements it owns are covered.

**Bug, on top.** Root cause written down; regression test fails without the fix and passes
with it; original reproduction no longer reproduces; neighbouring code checked; Affects version
set; need for a patch release stated.

**Epic.** All children Done or cancelled with a reason; PRD success criteria evaluated (met and
unmet recorded); PRD status updated and its plan reflects what was built; ADRs accepted and
linked; short retrospective written in the PRD page; Epic-created flags removed or dated.

**Additions by component type** (the component's Overview states its type).

| Type | Also required |
|---|---|
| Library | API change classified major/minor/patch and commit type matches; public exports intentional; usage doc updated; package build dry run succeeds, known consumers still compile |
| Application | incomplete behaviour behind a flag, default off; artifact built once and promoted unchanged; configuration external; health checks and observability in place; migrations backward compatible; rollback considered |
| Infrastructure | plan or diff reviewed; applied in non-production first when one exists; idempotent; cost estimated, tags and ownership present; state and backups safe |
| Boilerplate / projen | a freshly generated repo builds and passes its checks; an existing repo upgrades cleanly with the synth diff explained; upgrade path documented |

**Special cases.** Analysis (spike): finding written with a recommendation and the parent
updated, no code merged unless the spike says so. Architecture Design: the ADR is
`adr-accepted` and the interface is documented where the implementer will find it.
Documentation: links valid, examples run, page in the right place with its labels. Hotfix: the
universal checklist still applies; a regression test is never skipped.

**Never acceptable.** Done with CI red or a required check disabled; weakening or deleting a
test to get green; merging a failing build to fix forward; a secret left in history even if
rotated; closing a Bug without a regression test.
