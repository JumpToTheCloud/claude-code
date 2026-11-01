---
name: confluence-create-doc
description: Create a document page in the Confluence space JTTC - a PRD, a Technical Plan, a Consistency Analysis, an ADR or a Runbook - from the template kept in this skill. Finds the right parent, builds the title from the naming pattern, checks that the title is unique, fills the summary table (with the status lozenge) and the sections, creates the page in one call, adds the type label and returns the page. Blocks creation when a required section or summary row is missing. Use whenever a PRD, plan, analysis, ADR or runbook page must be created, or the user says "create the PRD page", "publish the plan", "write an ADR", "crear el PRD en Confluence". Changing an existing page belongs to confluence-update-doc.
---

# confluence-create-doc

Creates documents in the Confluence space JTTC. The caller (`/prd`, `/plan`, `/analyze` or a
person) writes the content; this skill checks it, fits it into the template kept in `assets/`
and creates the page. Cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`, space key `JTTC`, space
ID `223412226`. The space has no custom instructions, so there is nothing to load first. Pages
are written in **English**, as **HTML** bodies. Never use Confluence storage XML
(`ac:structured-macro`): it renders as text.

The templates in `assets/` are the source of truth. The pages under `Templates` in Confluence
are mirrors for people to read, generated from them, and are never read or copied here.

## Status lozenge

The Status row of the summary table holds a **status lozenge**, a coloured macro written as
`<span data-type="status" data-color="<color>">TEXT</span>` (text in capitals), never as plain
text. It is the only place where the state of a page lives.

| Page | Value | `data-color` |
|---|---|---|
| PRD, Technical Plan | `DRAFT` | `neutral` |
| PRD, Technical Plan | `IN REVIEW` | `yellow` |
| PRD, Technical Plan | `APPROVED` | `green` |
| PRD, Technical Plan | `SUPERSEDED` | `purple` |
| ADR | `PROPOSED` | `blue` |
| ADR | `ACCEPTED` | `green` |
| ADR | `SUPERSEDED` | `purple` |

A Consistency Analysis and a Runbook have no Status row. Labels are not used for the state:
the only label of a page is its type.

## Where each type lives

| `type` | Template | Parent | Title | Label |
|---|---|---|---|---|
| `prd` | `assets/prd.html` | the page `<component> — PRDs` | `PRD: <title>` | `prd` |
| `plan` | `assets/plan.html` | the PRD page | `Technical Plan — <title>` (same title as the PRD) | `plan` |
| `analysis` | `assets/analysis.html` | the PRD page | `Consistency Analysis — <title>` | `analysis` |
| `adr` | `assets/adr.html` | `<component> — Decisions`, or `Platform → Decisions` (`261390337`) | `ADR-NNNN: <short imperative title>` | `adr` |
| `runbook` | `assets/runbook.html` | the page `<component> — Runbooks` | `<component> — Runbook: <task>` | `runbook` |

Other fixed pages: Components `261324818`, Archive `261357569`.

## Input

| Input | Needed for | Notes |
|---|---|---|
| `type` | all | One of the five types |
| `title` | all | The short title, without the prefix of the pattern |
| `component` | `prd`, `runbook`, `adr` of a component | The Jira Component name, exactly as the Confluence component page |
| `scope` | `adr` | `component` or `platform` |
| `prd` | `plan`, `analysis` | The PRD page URL or ID |
| `plan` | `analysis` | The Technical Plan page URL or ID of that PRD |
| `summary` | all | Map of summary-table row to value. Never contains `Status`, nor the rows the skill links itself (see below) |
| `sections` | all | Map of section heading to content in markdown |

**Rows the skill fills as links.** A row that points to another page is never passed as text:
the skill writes it as an inline smart link (`<a href="URL" data-card-appearance="inline"></a>`),
which shows the live title of the target. For a `plan` it fills `PRD`; for an `analysis` it
fills `PRD` and `Technical Plan` (from the `prd` and `plan` inputs). Passing one of these rows
in `summary` is a validation error.

Required **summary rows** (the others are written as `—`). The Status row is always written by
the skill as a lozenge: `DRAFT` for a PRD or plan, `PROPOSED` for an ADR. A `Status` passed in
`summary` is a validation error.

| Type | Required rows | Other rows |
|---|---|---|
| `prd` | Component, Audience, Priority | Deadline, Jira Epic(s), Technical Plan, Consistency Analysis, Related ADRs, Last updated |
| `plan` | Component | Phases, Analysis verdict, Last updated |
| `analysis` | Date | Passes, Findings, Requirement coverage, Verdict |
| `adr` | Date, Scope | Related |
| `runbook` | Component, Owner, Risk, Trigger | Last verified, Estimated time, Needs approval, Related |

Required **sections** (the others are optional and are removed from the page when not given):

| Type | Required | Optional |
|---|---|---|
| `prd` | Problem Statement, Solution, User Stories, Functional Requirements, Success Criteria, Out of Scope | Non-Functional Requirements, Open Questions, Key Entities, Assumptions, Edge Cases, Related Work |
| `plan` | Architecture, Modules, Interface Contracts, Phases, Assumptions, Project Rules Check | Data Model, Revision notes |
| `analysis` | Summary, Pass 1 — Initial Findings, Coverage Summary, Metrics, Verdict | Pass 2 — Final State (post-fix) |
| `adr` | Context, Decision, Alternatives considered, Consequences | none (Positive, Negative and risks, Follow-ups go inside Consequences as `###` headings) |
| `runbook` | Purpose, Prerequisites, Steps, Verification, Rollback | Troubleshooting |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   - **Parent.** For `prd`, `adr` of a component and `runbook`: `searchConfluence` with
     `cql: title = "<component> — PRDs" AND space = "JTTC"` (or `— Decisions`, `— Runbooks`).
     Exactly one result is the parent. None means the component pages do not exist: reject and
     say the component must be added first (recipe in `jttc-workspace`). For `adr` of the
     platform the parent is `261390337`.
   - **PRD.** For `plan` and `analysis`: `getConfluenceContent` of the `prd` page with
     `detail: full` and `content_format: html`. Take its title (without `PRD: `), its ID (the
     parent) and its Component row.
   - **Unique title.** Build the final title from the pattern, then `searchConfluence` with
     `cql: title = "<final title>" AND space = "JTTC"`. Any result is a duplicate: report it
     with its URL and do not create. Titles are unique across the whole space.
   - **ADR number.** `executeRead` with `name: getConfluenceContentDescendants`,
     `inputs: {contentId: <parent>}`. Take the highest `ADR-NNNN` among the titles and add one,
     four digits, never reused. Numbering is per scope. If two scopes reach the same number,
     add the component name to the title.
1. **Validate before writing.** Every required summary row and section is present and not
   empty; no `Status` was passed; for `plan` and `analysis` the PRD exists; the title fits the
   pattern. If anything fails, write nothing and return the problems.
2. **Build the body** from the template file of the type in `assets/`, without its leading
   comment:
   - replace each `{{row:<label>}}` with the value, or `—`; the Status row gets the initial
     lozenge;
   - replace each `{{section:<heading>}}` with the content converted from markdown to HTML
     (`<p>`, `<ul>`, `<ol>`, `<table>` with `<thead>`, `<pre><code>`, `<strong>`, `<em>`,
     `<code>`, `<a href>`, and `<h3>` for `###`). Requirement lists (`REQ-n`, `NFR-n`, `SC-n`)
     use `<ul data-type="task-list">` with `<li data-type="task-item"><input type="checkbox">
     ...`. Links to Confluence pages and Jira issues are inline smart links:
     `<a href="URL" data-card-appearance="inline"></a>`;
   - remove an optional section, heading included, when it was not given;
   - there is no "Template" note and no placeholder sentence in the result.
3. **Create the page in one call** with `createConfluenceContent`: `cloudId`,
   `contentType: page`, `title`, `parent: {parentContentId: <parent>}`,
   `body: {format: "html", value: <html>}`. If the body is rejected, load the format guide with
   `executeRead`, `name: getContentFormatGuide`, `inputs: {toolName: "createConfluencePage"}`
   and retry once. Keep the new page ID and URL.
4. **Add the type label** with `executeWrite`, `name: addLabelsToConfluenceContent`,
   `inputs: {contentId, labels: [{"name": "<label>", "prefix": "global"}]}`. It is the only
   label: the state is the Status lozenge, and nothing can remove a label.
5. **Link the new page from its PRD** (`plan` and `analysis` only). The PRD page was read in step
   0 and its `snapshotToken` is current unless something else changed it. With
   `updateConfluenceContent` and `edits`, run first with `dryRun: true`, then for real,
   `replaceNode` on the **paragraph** inside the cell of the row `Technical Plan` (for a plan) or
   `Consistency Analysis` (for an analysis), with a paragraph holding the inline smart link to
   the new page. On `snapshot_stale`, read the PRD again and reapply. The caller never has to
   update the PRD row afterwards.
6. **ADR only: check the number once.** Two ADRs created at the same moment under the same
   parent could both take the next number, and Confluence would not object because the
   titles differ. List the descendants of the parent again
   (`executeRead`, `name: getConfluenceContentDescendants`). If another page has the same
   `ADR-NNNN`, the page with the **lower page ID** keeps the number and the other one is renamed
   to the next free number with `updateConfluenceContent` and `title`. Report a rename in the
   Checks line. A PRD has **no number**: it is identified by its page ID, which does not change
   when it is renamed, and by its title.
7. **Read back.** `getConfluenceContent` with `detail: outline` must show every required
   heading and none of the removed ones; `searchConfluence` with
   `cql: id = <id> AND label = "<label>"` should return the page; for a PRD, plan or ADR the
   Status row must show the initial lozenge; for a `plan` or `analysis`, the PRD row of the new
   page and the matching row of the PRD must hold the links. **The search index lags** by a few seconds: if
   the label search returns nothing, run it once more after the other read-back steps and, if
   it still returns nothing, report `created, label not confirmed (search index lag)`. Never
   add the label a second time and never treat it as a failure of the page.

## Output

| type | title | id | url | status |
|---|---|---|---|---|
| prd | PRD: ... | 123456 | https://jumptothecloud.atlassian.net/wiki/spaces/JTTC/pages/123456 | `created`, `duplicate` or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you
actually did, for example `Checks: parent found by title (<id>); title unique; ADR number
computed (0004); body built from assets/adr.html; page created; label confirmed; read back
(outline, status lozenge)`. A check that is not listed was not done, and if it was not done
nothing may have been written.

## Never

- Create a page whose title already exists in the space, or outside its parent.
- Read or copy the pages under `Templates` in Confluence, or edit them.
- Put the state in a label or in plain text: it is a status lozenge in the summary table.
- Leave a template marker (`{{...}}`) or a placeholder sentence on the page.
- Write storage XML or put secrets, tokens or personal data in a page.
- Link the page to a Jira Epic: that is `jira-link-issues`.
