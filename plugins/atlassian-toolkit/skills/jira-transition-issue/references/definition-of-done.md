# Definition of Done

**Done means merged into `main`, safe, and left in a state nobody has to come back to.** It does not mean released. Releasing and deploying are tracked in GitHub (tags, releases, deployments). Incomplete or risky behaviour merges behind a feature flag whose default is off.

## How to use this page

- The checklists are **layered**. A sub-task is Done when the universal checklist passes. A Story is Done when all its sub-tasks are Done and the Story checklist passes. Bugs and Epics add their own.
- On top of that, the **component type** additions apply: library, application, infrastructure or boilerplate.
- Every line is a yes/no check. Write `N/A` and a reason when one does not apply. Never skip silently.
- Evidence beats assertion: link the pull request, the CI run, the test, the output. "Done" without a link is not Done.
- The status moves to `Done` only after the pull request is merged into `main`.

## 1. Universal checklist (every sub-task and every pull request)

### Code

- Does what the sub-task's goal says, and satisfies the acceptance criteria assigned to it.
- Lint and format pass with the repository's own configuration, with no new warnings.
- Type checking passes (for TypeScript, `tsc --noEmit`), with no new suppressions and no `any` added without a comment justifying it.
- No dead code, commented-out code or debug output left behind.
- Every `TODO` or `FIXME` points to a Jira key. An anonymous TODO is not allowed.
- Existing utilities and patterns were reused where the plan named them. No duplicate implementation of something that already exists.

### Tests

- Sub-tasks labelled `tdd` were built test-first: a failing test existed before the code.
- New logic has unit tests. Boundaries (I/O, network, database, cloud API) have integration tests where the plan called for them.
- Tests assert behaviour, not implementation details. They would still pass after a refactor that keeps behaviour.
- Coverage of the changed code is at least 80%, and overall coverage does not drop.
- No flaky, skipped or order-dependent tests were added. No test was weakened to make CI green.
- All tests pass locally and in CI.

### Version control

- Branch is named `<type>/<JIRA-KEY>-short-slug`, for example `feature/JTTC-42-stack-construct`, and was branched from an up-to-date `main`.
- Commits follow Conventional Commits, are atomic (one logical change each), and carry the Jira key in the scope or footer.
- Breaking changes use `!` or a `BREAKING CHANGE:` footer with the migration path.
- The branch is short-lived: merged within days, not weeks, to keep trunk-based development honest.

### Pull request and review

- The PR title is a Conventional Commit. The description says what changed, why, and how to verify it, and links the Jira item.
- The author reviewed their own diff line by line before asking for review.
- At least one review pass by someone other than the author, either a human or the code-review tool. All blocking findings are resolved or turned into a linked Jira item with a reason.
- A sub-task with Mode **HITL** had a human review its result. An agent's output is never merged on its own say-so.

### Continuous integration

- Every required CI check is green on the latest commit: lint, typecheck, test, build, and security or dependency scans when the repository has them.
- The branch is up to date with `main` and merges without conflict.

### Security

- No secrets, tokens or personal data in code, tests, logs, commit history or PR text.
- External input is validated at the boundary. Errors do not leak internals.
- Every new dependency is justified in the PR, license-compatible, maintained and pinned. Nothing added for a one-line convenience.
- Permissions are least-privilege (IAM roles, tokens, workflow permissions).

### Documentation

- README and API docs reflect the change. Public API has doc comments.
- An ADR exists for any architectural decision made along the way, and it is linked from the PR.
- A runbook is created or updated if operational behaviour changed.

### Jira hygiene

- The PR is linked from the Jira item. A closing comment states the outcome, plus anything that deviated from the plan.
- If the effort was off by more than double the estimate, say so in the comment. That data feeds future estimates.
- The Flagged field is cleared and no "is blocked by" link points to an open issue.

## 2. Story checklist

On top of the universal checklist for every sub-task:

- All sub-tasks are Done. None was dropped without a written reason.
- **Every acceptance criterion is verified**, each with evidence: the test that proves it, or the output of a manual check.
- Every non-functional requirement was verified or its result recorded: performance numbers, security review, compatibility matrix.
- The feature works end to end, not only piece by piece, when the integrated `main` is exercised.
- If it is behind a feature flag: the flag exists, its default is **off**, and the removal is tracked in a Jira item.
- No open Bug linked to it blocks its use. Bugs found along the way are filed, not buried.
- The functional requirements from the PRD that this Story owns are all covered.

## 3. Bug checklist

On top of the universal checklist:

- The **root cause** is written in the Jira item, not only the symptom.
- A **regression test** exists. It fails without the fix and passes with it.
- The original reproduction steps no longer reproduce the defect.
- Neighbouring code with the same flaw was checked. Similar occurrences are fixed or filed.
- **Affects version** is set, so the defect is traceable to a release. While the project has no versions yet, saying so is enough.
- If it needs a patch release, that is stated, because release tracking lives in GitHub.

## 4. Epic checklist

- All child Stories, Tasks and Bugs are Done, or were explicitly cancelled with a reason.
- The success criteria of the PRD were evaluated. The page records which were met and which were not.
- The PRD page status is updated, and its Technical Plan reflects what was actually built.
- ADRs for the decisions taken are accepted and linked.
- A short retrospective is written in the PRD page: what went well, what hurt, what to change in this process.
- Feature flags created by the Epic are removed or have a dated removal item.

## 5. Additions by component type

The component's *Overview* page states its type. Add the rows for that type to the universal checklist. A component with no declared type has no additions.

| Type | Also required |
|---|---|
| **Library** | Public API change is classified as major, minor or patch, and the commit type matches. Public types and exports are intentional: nothing internal leaks. Usage example or doc updated. A package build dry run succeeds, and known consumers still compile |
| **Application** | Incomplete behaviour is behind a feature flag, default off. The artifact is built once and promoted unchanged through environments. Configuration is external: nothing is hardcoded per environment. Health checks and the logs or metrics that prove it works are in place. Migrations are backward compatible with the previous version, so rollback is safe. Rollback was considered and, for risky changes, rehearsed |
| **Infrastructure** | The plan or diff was read and reviewed: nothing destroyed or replaced by surprise. Applied in a non-production environment first, when one exists. Idempotent: applying twice changes nothing the second time. Cost impact estimated, tags and ownership present. State and backups are safe, and destroy paths are understood |
| **Boilerplate / projen** | A repository generated fresh from it builds and passes its own checks. An existing repository upgrades cleanly, and the synth diff is explained. The change and the upgrade path are documented for consumers |

## 6. Special cases

| Item | Done means |
|---|---|
| **Analysis** sub-task (spike) | The finding is written down with a recommendation, and the parent item is updated with it. No code is merged unless the spike says so |
| **Architecture Design** sub-task | The ADR is accepted, and the interface it defines is documented where the implementer will find it |
| **Documentation** sub-task | Links are valid, examples were run, and the page is in the right place of the tree with its labels |
| Hotfix | The universal checklist still applies. Only the process around it is faster. A regression test is never skipped |

## 7. What Done does not include

- It is not deployed to production. Deployment and release belong to GitHub.
- It does not mean the feature flag is on. Turning a flag on is a release decision.
- It does not mean perfect. Known limitations are written down and filed, not hidden.

## 8. Never acceptable

- Marking Done with CI red, or with a required check disabled.
- Weakening or deleting a test to get green.
- Merging a failing build "to fix forward".
- Leaving a secret in history, even if it was rotated.
- Closing a Bug without a regression test.

## Reviewing this page

Review it after every Epic, in the retrospective, and whenever a defect escaped that a criterion would have caught. Remove a criterion nobody has ever failed once it is enforced by tooling. Record changes in the pull request that edits this page.

Related: *Definition of Ready*, *Process*.
