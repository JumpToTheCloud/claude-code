# Bug template

Source of truth for the body of a JTTC Bug. `confluence-sync-templates` mirrors this file to
Confluence; never edit the mirror. Everything between the `body` markers is posted as the Jira
description (markdown).

## Fields

| Jira field | Filled at | Rule |
|---|---|---|
| `summary` | creation | What fails, in plain words, at most 100 characters, no `Bug:` prefix |
| `issuetype` | creation | `Bug` |
| `components` | creation | Exactly one |
| `parent` | creation | Optional Epic key |
| `priority` | creation | Reflects the severity |
| Affects versions `versions` | creation | Version where it was observed |
| Origin link | creation | Optional. *relates* issue link or remote link, see Guidance |
| `labels` | creation | Optional |
| Story Points `customfield_10041` | refinement | |
| Size `customfield_10100` | refinement | |

## Sections

| Section | Required at creation | Filled at |
|---|---|---|
| Environment | yes | creation |
| Steps to reproduce | yes | creation |
| Expected vs actual | yes | creation |
| Impact and severity | yes | creation |
| Root cause | no | refinement |
| Acceptance criteria | no | refinement |
| Non-functional requirements | no | refinement |
| Dependencies and assumptions | no | refinement |
| Change safety | no | refinement |

## Guidance (not posted)

- Origin: the issue or PR that introduced the bug is a Jira link (a *relates* issue link for a
  Jira issue, a remote link for a PR or a GitHub issue), not text. Traceability only, it never
  blocks anything. When unknown, add no link and no section.
- Root cause: a written root cause, or a time-boxed investigation sub-task.
- Non-functional requirements: one line is enough, for example `N/A for every category:
  defect fix, no new requirements`. Name a category only when the fix has a real effect.
- Dependencies and assumptions: blockers, and `Assumption:` lines.
- Change safety: feature flag, migrations, breaking changes.
- Acceptance criteria: one criterion must be the regression test, which fails without the fix
  and passes with it.

<!-- body:start -->
## Environment

{{environment}}

## Steps to reproduce

{{numbered_steps}}

## Expected vs actual

**Expected:** {{expected}}

**Actual:** {{actual}}

## Impact and severity

{{impact_and_severity}}

## Root cause

> _Pending refinement_

## Acceptance criteria

> _Pending refinement_

## Non-functional requirements

> _Pending refinement_

## Dependencies and assumptions

> _Pending refinement_

## Change safety

> _Pending refinement_
<!-- body:end -->
