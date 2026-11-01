# Definition of Done

Source of truth for the gate `jira-transition-issue` applies on the way to `Done`. The
Confluence page `Definition of Done` (223281157) is a mirror for people to read: it is
generated from this file, never edited by hand.

**Done means merged into `main`, safe, and left in a state nobody has to come back to.** It
does not mean released (GitHub tracks releases and deployments) and does not mean the feature
flag is on.

## How to apply

- Layered: a sub-task is Done when the universal checklist passes. A Story is Done when all its
  sub-tasks are Done and the Story checklist passes. Bugs and Epics add their own. The
  component-type additions apply on top.
- Every line is a yes/no check. `N/A` needs a reason. A silently missing line fails.
- Evidence beats assertion: the PR, the CI run, the test, the output. "Done" without a link is
  not Done.
- The status moves to `Done` only after the pull request is merged into `main`.

### What the transition skill can and cannot check

| Kind | How it is checked |
|---|---|
| Jira facts: all sub-tasks Done, no open *is blocked by*, Flagged empty, Affects version set, Epic children Done | Read from Jira |
| Facts about the pull request: merged, CI green, reviewed by someone other than the author, Conventional Commit title, branch name | Stated in the `evidence` the caller passes (PR URL, `merged`, CI result, reviewer). The skill rejects `Done` when any is missing, and does not call GitHub |
| Checks enforced by tooling (lint, types, tests, coverage, secrets scan) | Covered by green CI in the evidence |
| Judgement items (regression test fails without the fix, root cause written, ADR accepted) | Read from the issue and the evidence, or attested in `evidence` |

## 1. Universal checklist (every sub-task and pull request)

### Code
- Does what the sub-task's goal says and satisfies its acceptance criteria.
- Lint and format pass with no new warnings.
- Type checking passes, with no new suppressions and no unexplained `any`.
- No dead code, commented-out code or debug output.
- Every `TODO` or `FIXME` points to a Jira key.
- Existing utilities named by the plan were reused.

### Tests
- `tdd` sub-tasks were built test-first.
- New logic has unit tests; boundaries have integration tests where planned.
- Tests assert behaviour, not implementation.
- Coverage of changed code is at least 80% and overall coverage does not drop.
- No flaky, skipped or order-dependent tests; no test weakened to get green.
- All tests pass locally and in CI.

### Version control
- Branch named `<type>/<JIRA-KEY>-short-slug`, from an up-to-date `main`.
- Conventional Commits, atomic, with the Jira key in the scope or footer.
- Breaking changes use `!` or a `BREAKING CHANGE:` footer with the migration path.
- Short-lived branch.

### Pull request and review
- PR title is a Conventional Commit; the description says what, why and how to verify, and
  links the Jira item.
- The author reviewed their own diff.
- At least one review pass by someone other than the author (a human or the code-review tool);
  blocking findings resolved or filed with a reason.
- A **HITL** sub-task had a human review its result.

### Continuous integration
- Every required check is green on the latest commit.
- Up to date with `main` and merges without conflict.

### Security
- No secrets, tokens or personal data anywhere, history included.
- External input validated at the boundary; errors do not leak internals.
- Every new dependency justified, license-compatible, maintained and pinned.
- Least-privilege permissions.

### Documentation
- README and API docs reflect the change.
- An ADR exists for any architectural decision, linked from the PR.
- A runbook is created or updated if operations changed.

### Jira hygiene
- The PR is linked from the Jira item. A closing comment states the outcome and any deviation.
- An effort off by more than double the estimate is noted in the comment.
- The Flagged field is cleared and no *is blocked by* link points to an open issue.

## 2. Story checklist (on top of the universal one)

- All sub-tasks are Done, none dropped without a written reason.
- **Every acceptance criterion is verified**, each with evidence.
- Every non-functional requirement was verified or its result recorded.
- Works end to end on the integrated `main`.
- Behind a feature flag: the flag exists, its default is **off**, and its removal is tracked.
- No open Bug linked to it blocks its use.
- The PRD requirements this Story owns are all covered.

## 3. Bug checklist (on top of the universal one)

- The **root cause** is written in the Jira item.
- A **regression test** exists: it fails without the fix and passes with it.
- The original reproduction steps no longer reproduce the defect.
- Neighbouring code with the same flaw was checked; similar occurrences fixed or filed.
- **Affects version** is set, or `Affects version: none yet` while the project has no versions.
- If it needs a patch release, that is stated.

## 4. Epic checklist

- All child Stories, Tasks and Bugs are Done, or cancelled with a reason.
- The PRD success criteria were evaluated; the page records which were met and which were not.
- The PRD page status is updated and its Technical Plan reflects what was built.
- ADRs for the decisions taken are `ACCEPTED` and linked.
- A short retrospective is written in the PRD page.
- Feature flags created by the Epic are removed or have a dated removal item.

## 5. Additions by component type

The component's Overview page states its type. A component with no Overview page, or whose
Overview declares no type (such as `platform`), has no additions: they do not apply and the
transition says so in its `Checks` line.

| Type | Also required |
|---|---|
| Library | API change classified major, minor or patch with a matching commit type; public exports intentional; usage doc updated; package build dry run succeeds and known consumers still compile |
| Application | incomplete behaviour behind a flag, default off; artifact built once and promoted unchanged; configuration external; health checks and observability in place; migrations backward compatible; rollback considered |
| Infrastructure | plan or diff reviewed; applied in non-production first when one exists; idempotent; cost estimated, tags and ownership present; state and backups safe |
| Boilerplate / projen | a freshly generated repository builds and passes its checks; an existing repository upgrades cleanly with the synth diff explained; the upgrade path is documented |

## 6. Special cases

| Item | Done means |
|---|---|
| Analysis sub-task (spike) | The finding is written with a recommendation and the parent is updated. No code merged unless the spike says so |
| Architecture Design sub-task | The ADR is `ACCEPTED` (its Status row) and the interface it defines is documented where the implementer will find it |
| Documentation sub-task | Links valid, examples run, page in the right place with its labels |
| Hotfix | The universal checklist still applies; a regression test is never skipped |

## 7. Never acceptable

- Done with CI red, or a required check disabled.
- Weakening or deleting a test to get green.
- Merging a failing build to fix forward.
- A secret left in history, even if rotated.
- Closing a Bug without a regression test.
