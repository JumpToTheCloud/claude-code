# How the gates are applied

`definition-of-ready.md` and `definition-of-done.md` say **what must be true**. They are the
team's agreement and say nothing about Jira. This file says **how `jira-transition-issue` applies
them in the JTTC project**: when each gate runs, how each criterion is checked, and how things
are written in Jira. A change here is a change of the tool; a change in the two definitions is a
change of the agreement. Only the two definitions are mirrored to Confluence.

## Which move runs which gate

| Move | What is checked | Where the criteria are |
|---|---|---|
| `Backlog → In refinement` | Entry checklist | `definition-of-ready.md`, "Entry" |
| `In refinement → Refined` | Gate 1 (Bug: the Bug variant). Task: optional, only when unclear. Epic and sub-task: not applicable | "Gate 1", "Bug variant of Gate 1" |
| `Refined → Ready` | Gate 2. Task: the Task variant. Sub-task: the sub-task checklist | "Gate 2", "Task variant of Gate 2", "Sub-task checklist" |
| `Backlog → Ready` | The Task variant of Gate 2, **Task only**. Any other type is rejected | "Task variant of Gate 2" |
| `Ready → In Progress` | nothing | |
| `In Progress → In Review` | A pull request exists (`pr_url` given and linked on the issue) | |
| `In Review → Done` | The Definition of Done: universal, plus Story, Bug or Epic, plus the component type | `definition-of-done.md` |
| Any move to an earlier status | nothing, but a `reason` is needed and written as a comment | |

A parent and its sub-tasks move to `Ready` together: the whole set is checked first and nothing
moves if one fails.

## How each criterion is checked

A criterion that does not apply must say `N/A` and a reason **in the issue**. A criterion that is
silently missing fails.

| The definition says | In Jira it is checked as |
|---|---|
| Source is linked | A Jira remote link to the PRD, ADR or page, or a `No PRD: <reason>` line in the description |
| Traces back to an approved PRD | The PRD is a remote link on the issue (or on its Epic) and the Status row of its Confluence page reads `APPROVED`: read the page with `detail: summary`, whose excerpt starts with `Status APPROVED Green`. With `No PRD: <reason>` the criterion is `N/A` |
| Each requirement cites the PRD requirement | The `Requirements covered` line of the description |
| Linked to its Epic | The `parent` field |
| Estimation set | Story Points, Size, Business Value, Risk and Priority fields |
| Affects version is stated | The Affects version field, or `Affects version: none yet` (or the version name, when it does not exist in the project) in the Environment section |
| An ADR, at least proposed | The ADR page exists and has a Status row |
| Sub-task "Where" | The `Files` section lists real paths from the repository root, test files included, and a directory or "the relevant files" fails |
| Sub-task estimate | The original estimate in hours, at most 8 |
| Mode and `tdd` | The Mode field and the `tdd` label |
| Blockers | *Blocks* / *is blocked by* links with no cycle |

## The Definition of Done: what can be checked and how

| Kind | How it is checked |
|---|---|
| Jira facts: all sub-tasks Done, no open *is blocked by*, Flagged empty, Affects version stated, Epic children Done | Read from Jira |
| Facts about the pull request: merged, CI green, reviewed by someone other than the author, Conventional Commit title, branch name | Stated in the `evidence` the caller passes (PR URL, `merged`, CI result, reviewer). The skill rejects `Done` when any is missing, and does not call GitHub |
| Checks enforced by tooling (lint, types, tests, coverage, secrets scan) | Covered by green CI in the evidence |
| Judgement items (regression test fails without the fix, root cause written, ADR accepted) | Read from the issue and the evidence, or attested in `evidence` |

`Done` needs `evidence` and a `closing_comment`, and the Checks line says that the
component-type additions do not apply when the component has no Overview page or no declared
type (as `platform`).
