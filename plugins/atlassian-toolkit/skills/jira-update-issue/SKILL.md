---
name: jira-update-issue
description: Update an existing Jira issue in the JTTC project - set Story Points, Size, Business Value, Risk, Mode, Priority, labels (including tdd), the Flagged marker, the original estimate of a sub-task, fill or replace sections of the description (removing the `Pending refinement` marker), and add a comment. Validates values against the allowed ones, never changes the status and never rewrites a section that does not exist. Use during refinement and planning, or when the user says "set the story points", "refine this story", "update the description", "flag this as blocked", "actualizar la historia", "add a comment". Status changes belong to jira-transition-issue.
---

# jira-update-issue

Edits fields and description sections of existing issues, and adds comments. The caller decides
the values; this skill checks them and writes them. Cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, project `JTTC`. Field IDs and allowed values:
`jttc-workspace`, `references/jira-project.md`.

## Input

A list of updates. For each: `key` and at least one of the following.

| Input | Allowed values | Notes |
|---|---|---|
| `summary` | text, at most 100 characters | Reword the title during refinement. Must state an outcome. No `Story:` or `Bug:` prefix |
| `story_points` | 1, 2, 3, 5, 8 | Fibonacci. A Task never above 3 |
| `size` | `XXS (0,25D)`, `XS (0,5D)`, `S (1D)`, `M (2D)`, `L (3D)`, `XL (4D)`, `XXL (EPIC - TOO BIG)` | Setting `XXL` is allowed: it means the item must be split. The Refined gate rejects it |
| `business_value` | a number | Used to rank |
| `risk` | 1, 5, 10 | |
| `mode` | `AFK`, `HITL` | Sub-tasks and Tasks. `Architecture Design` only `HITL` |
| `priority` | a priority name | |
| `labels_add`, `labels_remove` | label names | `tdd` only on `Development` sub-tasks and on Bugs |
| `flagged` | `true` or `false` | Marks blocked work. Set it together with an *is blocked by* link (`jira-link-issues`) |
| `estimate_hours` | number, at most 8 | Sub-tasks only. Written as `timetracking.originalEstimate` |
| `sections` | map `heading -> new content` | Replaces the content under an existing `##` heading of the description |
| `comment` | text (markdown) | Added as a new comment |

## Steps

1. **Read each issue** with `getJiraIssue` (`view: full`). Check it exists and take its type
   and current description.
2. **Validate every update before writing any.** If one fails, write nothing from the batch and
   return the problems per update. Never invent a value.
   - the value is in the allowed set; `estimate_hours` is only for sub-tasks;
   - `mode` and `tdd` follow the rules above for the issue's type;
   - **each `sections` heading exists** in the description. If it does not, reject: never
     append a section silently;
   - the new content of a section is not empty and is not the marker itself. Only the marker
     line `> _Pending refinement_` is forbidden; the words may appear inside real content (for
     example a requirement about that marker);
   - the issue's status, type, Component and parent are never changed here.
3. **Build the description edit.** Split the description at the `##` headings, replace the
   body of each named section (up to the next `##` heading) with the new content and leave
   every other section byte for byte as it was. A section replaced here loses its
   `> _Pending refinement_` marker because the marker is part of the old body. If the
   description contains inline media or panels, write it back with `contentFormat: html`;
   otherwise markdown.
4. **Write** with `editJiraIssue`: `cloudId`, `issueIdOrKey`, the new description inside
   `fields: {"description": "<markdown>"}` (the tool has **no** top-level `description`
   argument: passing one is dropped silently and the call still reports success), and
   `additional_fields` for the rest, keyed by field name (`"summary"`, `"Story Points"`, `"Size"`,
   `"Business Value"`, `"Risk"`, `"Mode"`, `"timetracking": {"originalEstimate": "<n>h"}`).
   Labels are **set, not appended**: send the full list (current plus added, minus removed).
   If an option field is rejected by name, look up the option ID
   (`GET /rest/api/3/field/<fieldId>/context`, then `/option`) and retry once with the ID.
   **Read the issue back** with `getJiraIssue` and confirm that every section you named now
   holds the new content and that the fields have the new values. If the description did not
   change, report `rejected: description not saved` and do not claim success. (`timetracking`
   is not returned by the MCP, so it cannot be read back.)
5. **Comment** with `addOrEditJiraIssueComment` (a new comment, never an edit of an existing
   one). Do not put comments in a transition or in `editJiraIssue`.
6. **All or nothing per update.** Every field and every section named in an update must be
   written and confirmed by the read-back. If any one was not applied, report the update as
   `rejected: <what was not written>` (or `partial: <what was written> / not written: <what>`
   when something was already saved). Never report `updated` when a named section or value is
   missing, and never decide on your own that a named section does not need writing.
7. **Return** one row per update.

## Output

| key | updated | status |
|---|---|---|
| JTTC-9 | story_points, size, sections: Functional requirements | `updated` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:`, and list there the exact headings you wrote and confirmed, per issue, that lists what you actually did, for example `Checks: issues read; values validated; description read back, sections confirmed`. A check that is not listed was not done, and if it was not done nothing may have been written.

## Never

- Change the status, the issue type, the Component or the parent.
- Replace a section that does not exist, or overwrite a section the update did not name.
- Set Story Points, Size, Business Value or Risk to a value outside the allowed ones.
- Leave the `> _Pending refinement_` marker line in a section it has just filled.
