# Sub-task template

Source of truth for the body of a JTTC sub-task. One template serves the five sub-task types.
`confluence-sync-templates` mirrors this file to Confluence; never edit the mirror. Everything
between the `body` markers is posted as the Jira description (markdown).

A sub-task is self-contained: a person or an agent can start by reading only this issue.

## Fields

| Jira field | Filled at | Rule |
|---|---|---|
| `summary` | creation | The work in plain words, at most 100 characters |
| `issuetype` | creation | One of `Development`, `Automation`, `Analysis`, `Architecture Design`, `Documentation` |
| `components` | creation | Copied from the parent |
| `parent` | creation | The Story, Task or Bug it belongs to |
| `timetracking.originalEstimate` | creation | Ideal hours, at most `8h` |
| Mode `customfield_10231` | creation | `AFK` or `HITL`. `Architecture Design` is always `HITL` |
| `labels` | creation | `tdd` when the logic can be specified by tests first |

Sub-tasks are created in `Backlog` (the workflow has one initial status). The iteration plan
moves the whole set to `Ready`.

## Sections

All required at creation. Documentation sub-tasks may mark Tests as `N/A: reason`.

## Guidance (not posted)

- Files: every file to create or change, as a path from the repository root with what changes
  in it, **test files included**. Never a directory or "the relevant files".

<!-- body:start -->
## Goal

{{goal}}

## Context

{{minimal_context}}

## Files

{{exact_paths_and_what_changes_in_each}}

## Steps

{{numbered_concrete_steps_with_signatures}}

## Acceptance criteria covered

{{ac_ids_and_text_from_the_parent}}

## Tests

{{tests_to_write_and_level}}

## Estimate

{{hours}}h ideal. Mode: {{AFK_or_HITL}}.
<!-- body:end -->
