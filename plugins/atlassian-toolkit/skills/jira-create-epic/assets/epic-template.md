# Epic template

Source of truth for the body of a JTTC Epic. `confluence-sync-templates` mirrors this file to
Confluence; never edit the mirror. Everything between the `body` markers is posted as the Jira
description (markdown).

## Fields

| Jira field | Filled at | Rule |
|---|---|---|
| `summary` | creation | The outcome the Epic delivers, at most 100 characters |
| `issuetype` | creation | `Epic` |
| `components` | creation | Exactly one |
| PRD remote link | creation | Link to the PRD's Confluence page, or none when `No PRD` |
| ADR remote links | creation | Optional, one per related ADR |
| `labels` | creation | Optional |
| `priority` | creation | Optional |

An Epic has no refinement gate. It is complete at creation.

## Sections

| Section | Required at creation |
|---|---|
| Expected outcome | yes |
| Source | conditional: only when there is no PRD |
| Scope | no |
| Out of scope | yes |
| Success criteria | yes |

## Guidance (not posted)

- Success criteria: one line per criterion, keeping the PRD's `SC-n` numbering and a
  measurable target.
- Source: the PRD and the related ADRs are Jira remote links to their Confluence pages, not
  text. The `Source` section is written only when there is no PRD, with the reason; otherwise
  omit it.

<!-- body:start -->
## Expected outcome

{{outcome}}

## Source

- No PRD: {{no_prd_reason}}

## Scope

{{scope_bullets}}

## Out of scope

{{out_of_scope_bullets}}

## Success criteria

{{success_criteria}}
<!-- body:end -->
