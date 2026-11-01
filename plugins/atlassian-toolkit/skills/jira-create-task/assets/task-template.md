# Task template

Source of truth for the body of a JTTC Task (technical work with no user story).
`confluence-sync-templates` mirrors this file to Confluence; never edit the mirror. Everything
between the `body` markers is posted as the Jira description (markdown).

## Fields

| Jira field | Filled at | Rule |
|---|---|---|
| `summary` | creation | Outcome in plain words, at most 100 characters |
| `issuetype` | creation | `Task` |
| `components` | creation | Exactly one |
| `parent` | creation | Epic key |
| Source remote link | creation | Link to the source's Confluence page, or none when `No source` |
| `labels` | creation | Optional |
| Mode `customfield_10231` | refinement | `AFK` or `HITL` |
| Story Points `customfield_10041` | refinement | At most 3. Bigger work is a Story |

## Sections

| Section | Required at creation | Filled at |
|---|---|---|
| Outcome | yes | creation |
| Done when | yes | creation |
| Source | conditional: only when there is no source link | creation |
| Files to touch | no | refinement |

## Guidance (not posted)

- Done when: two to five lines, each one verifiable.
- Source: the PRD, ADR or page that justifies the Task is a Jira remote link to its Confluence
  page, not text. The `Source` section is written only when there is none, with the reason;
  otherwise omit it.

<!-- body:start -->
## Outcome

{{outcome}}

## Done when

{{done_when}}

## Source

- No source: {{no_source_reason}}

## Files to touch

> _Pending refinement_
<!-- body:end -->
