# Jira project JTTC

Project **Jump to the Cloud**, key `JTTC`, id `10154`. Company-managed Scrum project.
Site `jumptothecloud.atlassian.net`, cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`.

## Contents

- [Workflow](#workflow-jttc-workflow): statuses, IDs, shortcuts, blocked work
- [Issue types](#issue-types): the nine types and their IDs
- [Fields](#fields): required fields, custom field IDs and values
- [Boards and filters](#boards-and-filters)
- [Components](#components)
- [Configuration objects](#configuration-objects-all-prefixed-jttc-no-colon): what is ours and what is shared
- [Querying](#querying): JQL examples
- [Rebuilding or checking the project](#rebuilding-or-checking-the-project)

## Workflow: `JTTC Workflow`

`Backlog → In refinement → Refined → Ready → In Progress → In Review → Done`

Every issue type uses it. Transitions are **global**: from any status you can go to any
other, and each transition is named after its target status. The only initial transition is
`Create`, into `Backlog`. There are no validators and no Blocked statuses.

| Status | ID | Category | Meaning | Leaves through |
|---|---|---|---|---|
| Backlog | 10023 | To do | Exists, nothing analysed | — |
| In refinement | 10015 | In progress | Being analysed (FR/NFR, AC, size) | Gate 1 |
| Refined | 10066 | To do | Specified, not yet broken into sub-tasks | Gate 2 |
| Ready | 10067 | To do | Self-contained sub-tasks exist, DoR met | Picked up |
| In Progress | 3 | In progress | Being worked on | PR opened |
| In Review | 10068 | In progress | PR open, awaiting review and green CI | Definition of Done |
| Done | 10011 | Done | Merged into `main` | Final |

To move an issue, call `listJiraIssueTransitions` and pick the transition whose **target
status** is the one you want. Do not guess transition IDs.

**Blocked work.** Set the **Flagged** field (`customfield_10021`) and add an *is blocked by*
link. The status does not change.

**Shortcuts.** Story: full path. Task: `Backlog → Ready` when small and obvious. Bug: through
`In refinement` first, to reproduce and find the cause. Sub-task: created in `Backlog`, moved
to `Ready` by the iteration plan once the whole set passes gate 2.

## Issue types

| Type | ID | Sub-task? | Use |
|---|---|---|---|
| Epic | 10000 | no | Groups Stories. Usually one per PRD. |
| Story | 10009 | no | User-visible value. |
| Task | 10007 | no | Technical work with no story. |
| Bug | 10010 | no | Defect in existing behaviour. |
| Development | 10013 | yes | Implements functionality. |
| Automation | 10027 | yes | Integration and end to end tests. Always its own sub-task. |
| Analysis | 10026 | yes | Time-boxed spike. Output is a finding, not merged code. |
| Architecture Design | 10012 | yes | Interface or architecture decision. Always HITL. |
| Documentation | 10014 | yes | Writes or updates documentation. |

There is **no generic `Sub-task`** in JTTC, so every sub-task is classified. There is no
`Initiative` type either (the existing `Iniciative` has a typo and a hierarchy level that
depends on the Jira plan).

## Fields

Required when **creating** an issue: project, issue type, summary, reporter, and
**Components**. A sub-task also requires **Parent**.

| Field | ID | Type | Set by | Values |
|---|---|---|---|---|
| Components | `components` | system | at creation | exactly one component |
| Parent | `parent` | system | at creation | Epic for Story/Task; Story for sub-tasks |
| Story Points | `customfield_10041` | number | refine-story | Fibonacci: 1, 2, 3, 5, 8 |
| Size | `customfield_10100` | option | refine-story | `XXS (0,25D)`, `XS (0,5D)`, `S (1D)`, `M (2D)`, `L (3D)`, `XL (4D)`, `XXL (EPIC - TOO BIG)` |
| Business Value | `customfield_10098` | number | refine-story | free number, used to rank |
| Risk | `customfield_10131` | option | refine-story | `1`, `5`, `10` |
| Mode | `customfield_10231` | option | iteration-plan | `AFK`, `HITL` (sub-tasks) |
| Flagged | `customfield_10021` | array | anyone | marks blocked work |
| Original estimate | `timetracking` | system | creation (sub-tasks) | ideal hours as `"4h"`; at most `8h`. Must be on `JTTC Default Screen`, added by `jira_template.py apply` |
| Sprint | `customfield_10020` | array | planning | |
| Priority, Labels, Fix versions, Affects versions, Linked issues, Attachment, Assignee | system | | | |

**Option fields (Size, Risk, Mode) need an option ID**, not the text. Look it up at runtime:
`GET /rest/api/3/field/<fieldId>/context`, then `/context/<contextId>/option`. All five custom
fields have a global context, so the same IDs work in every project.

Size `XXL (EPIC - TOO BIG)` is never acceptable at the Refined gate: split the item.

**Label** `tdd`: marks sub-tasks suited to test-first work. It is the only label with meaning
here. There is no `afk` / `hitl` label: that is the Mode field.

## Boards and filters

| Board | ID | Type | Filter | Columns (status) |
|---|---|---|---|---|
| JTTC: Discovery Board | 261 | Kanban | `JTTC: Discovery` (10262): `project = JTTC AND status in (Backlog, "In refinement", Refined, Ready)` | Backlog, In refinement, Refined, Ready |
| JTTC: Development Board | 262 | Scrum | `JTTC: Development` (10263): `project = JTTC AND status in (Ready, "In Progress", "In Review", Done)` | Ready, In Progress, In Review, Done |

`Ready` is the hand-off: the last column of Discovery and the first of Development. On the
Scrum board, `Ready` items that are not in a sprint appear in its Backlog tab. WIP limits are
not set.

## Components

One Component per repository, named exactly like the Confluence component page. Created in
Jira first. Existing: `platform` (id 10240), for cross-cutting work that belongs to no repo.

## Configuration objects (all prefixed `JTTC`, no colon)

| Object | Name | ID |
|---|---|---|
| Workflow | `JTTC Workflow` | — |
| Workflow scheme | `JTTC Unified Workflow Scheme` | 10223 |
| Issue type scheme | `JTTC Unified Issue Type Scheme` | 10655 |
| Issue type screen scheme | `JTTC Unified Issue Type Screen Scheme` | 10155 |
| Screen scheme | `JTTC Screen Scheme` | 10185 |
| Screen | `JTTC Default Screen` | 10194 |
| Field configuration | `JTTC Field Configuration` + its scheme | UI only, not visible in the REST API |

**Do not touch** the objects named `JTTC: …` (with a colon). They belong to the old JTTC
project and are shared by CDKX, ORKAI and others.

## Querying

```
project = JTTC AND status = Ready ORDER BY Rank
project = JTTC AND component = "<name>" AND status != Done
project = JTTC AND issuetype in (Development, Automation, Analysis, "Architecture Design", Documentation) AND parent = JTTC-12
project = JTTC AND status = "In refinement"
```

Status names with spaces need quotes. `In refinement` is lowercase after the first word.

## Rebuilding or checking the project

`scripts/jira_template.py`, inside this skill's directory, builds the workflow, schemes and
screen, and keeps an existing project in sync. Modes: `validate` (checks the workflow payload
against Jira, creates nothing) and `apply`. It needs `JIRA_API_TOKEN` in the environment (and
optionally `JIRA_EMAIL`, `JIRA_SITE`), only ever creates new resources, and is idempotent. It
cannot manage the field configuration, which is UI only. Never hardcode the token, and never
write it to a file in the repository.

Run it as `python3 <skill dir>/scripts/jira_template.py validate` first, then `apply`.

Real check of required fields: `GET /rest/api/3/issue/createmeta/JTTC/issuetypes/<typeId>`
and look for `required: true`. This reflects actual behaviour; the field configuration
listing in the REST API does not.
