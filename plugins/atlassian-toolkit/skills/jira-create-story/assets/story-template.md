# Story template

Source of truth for the body of a JTTC Story. `confluence-sync-templates` mirrors this file to
Confluence; never edit the mirror. Everything between the `body` markers is posted as the Jira
description (markdown). Everything else is for the skill and for humans.

## Fields

| Jira field | Filled at | Rule |
|---|---|---|
| `summary` | creation | Outcome in plain words, at most 100 characters, no `Story:` prefix |
| `issuetype` | creation | `Story` |
| `components` | creation | Exactly one, the repository's Component |
| `parent` | creation | Epic key. A Story always belongs to an Epic |
| PRD remote link | creation | Link to the PRD's Confluence page, or none when `No PRD` |
| `labels` | creation | Optional |
| `priority` | refinement | |
| Story Points `customfield_10041` | refinement | 1, 2, 3, 5, 8 |
| Size `customfield_10100` | refinement | Never `XXL (EPIC - TOO BIG)` |
| Business Value `customfield_10098` | refinement | Number, used to rank |
| Risk `customfield_10131` | refinement | 1, 5, 10 |

## Sections

| Section | Required at creation | Filled at |
|---|---|---|
| User story | yes | creation |
| Context and source | conditional: only when it has a line to show | creation |
| Out of scope | yes | creation |
| Acceptance criteria | yes (initial) | creation, enriched at refinement |
| Functional requirements | no | refinement |
| Non-functional requirements | no | refinement |
| Dependencies and assumptions | no | refinement |
| Change safety | no | refinement |

`Pending refinement` is the marker for a section that is not filled yet. `refine-story`
replaces the marker with content.

## Guidance (not posted)

- Acceptance criteria: Given / When / Then, testable, each naming the requirement it covers.
- Non-functional requirements: answer every category or mark it `N/A: reason` (performance,
  reliability, security, compatibility, observability, operability, cost, maintainability).
- Change safety: feature flag (name, default off), migrations, breaking changes.
- Context and source: each line is written only when it applies. `No PRD` only when there is
  no PRD; `Requirements covered` only when requirement IDs were given. If neither applies,
  omit the whole section. Never write `N/A` or a guess.
- The PRD is a Jira remote link to its Confluence page and the Epic is the `parent` field. Neither is
  repeated in the body.

<!-- body:start -->
## User story

As a {{as_a}}
I want {{i_want}}
so that {{so_that}}.

## Context and source

- No PRD: {{no_prd_reason}}
- Requirements covered: {{req_ids}}

## Out of scope

{{out_of_scope_bullets}}

## Acceptance criteria

{{acceptance_criteria}}

## Functional requirements

> _Pending refinement_

## Non-functional requirements

> _Pending refinement_

## Dependencies and assumptions

> _Pending refinement_

## Change safety

> _Pending refinement_
<!-- body:end -->
