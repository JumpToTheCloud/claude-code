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
| `In Progress → In Review` | A pull request exists (`pr_url` given and linked on the issue). **Not for an Epic** | |
| `In Review → Done` | The Definition of Done: universal, plus the Story or Bug checklist, and the evidence contract below | `definition-of-done.md` |
| Epic: `Backlog → In Progress` | nothing. It moves when its first child starts. An Epic may skip the refinement statuses | |
| Epic: `In Progress → Done` | The Epic checklist (all children Done or cancelled with a reason) and the Epic evidence below. An Epic has **no `In Review` and no pull request** | `definition-of-done.md`, "Epic checklist" |
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

## The Definition of Done: the evidence contract

The Definition of Done is long, and most of it is checked by the pull request review and by CI,
not by this skill. The skill asks for a **fixed contract** and nothing more, so that every
agent applies the same gate and the caller knows exactly what to pass.

**Read from Jira** (never taken from the caller's word): all sub-tasks Done, no open *is blocked
by* link, `Flagged` empty, no open Bug blocking the item, a closing comment, and for a Bug the
root cause written in the issue and the Affects version stated.

**The caller passes in `evidence`**, for every item except an Epic:

| Field | Meaning |
|---|---|
| `pr_url` | The pull request |
| `merged` | It is merged into `main` |
| `ci` | The result of the required checks on the latest commit |
| `reviewer` | Who reviewed it, and that it is not the author (a human or the code-review tool; a HITL sub-task had a human) |

and, by type:

| Type | Also in `evidence` |
|---|---|
| Story | One line per acceptance criterion with the test or check that proves it, the result of the non-functional requirements, and the feature flag state (none, or its name, default off, removal tracked) |
| Bug | The regression test (fails without the fix, passes with it) and that the original reproduction no longer reproduces |
| Task, Development, Automation, Documentation sub-task | nothing more |
| Analysis sub-task | The link to the written finding |
| Architecture Design sub-task | The ADR link: its Status row must read `ACCEPTED` (same read as the PRD check) |
| Epic (no `pr_url`) | Which success criteria of the PRD were met and which were not (or `N/A: no PRD`), the retrospective link or `N/A`, the ADRs accepted, and the flags removed or dated |

Everything else in the Definition of Done is covered by the pull request review and by green CI.
The skill does **not** ask for it line by line, and it rejects `Done` only when a field above is
missing, a Jira fact fails, or the caller's own words contradict a line.
