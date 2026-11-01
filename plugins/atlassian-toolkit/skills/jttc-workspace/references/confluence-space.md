# Confluence space JTTC

Space **Jump to the Cloud**, key `JTTC`, id `223412226`, type global. Home page id `223412335`.
Site `jumptothecloud.atlassian.net`, cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`.

The space has no custom space instructions. Pages are written in **English**, as HTML bodies.

## Contents

- [The tree and its page IDs](#the-tree-and-its-page-ids)
- [The principle](#the-principle)
- [Where does this go?](#where-does-this-go)
- [Naming](#naming) and [Labels](#labels)
- [Summary table](#summary-table): rows of each template
- [Recipes](#recipes): create from a template, add a component, write a PRD, record a decision, retire a page
- [PRD and Epic](#prd-and-epic)
- [Editing pages](#editing-pages)
- [What does not belong here](#what-does-not-belong-here)

## The tree and its page IDs

```
Jump to the Cloud Home                          223412335
├── Platform                                    261324801   cross-cutting, more than one component
│   ├── How this space works                    261390383   read this first
│   ├── Process                                 261324835   workflow, labels, Jira conventions
│   │   ├── Definition of Ready                 223281170
│   │   └── Definition of Done                  223281157
│   ├── Decisions                               261390337   ADRs affecting several components
│   ├── Standards                               261357586   engineering conventions
│   └── Roadmap                                 261357603
├── Components                                  261324818   one branch per repository
│   └── <component>/                            (none yet)
├── Templates                                   261226498   generated mirrors, never edit
│   ├── PRD Template                            261357620
│   ├── Technical Plan Template                 261423134
│   ├── Consistency Analysis Template           261390366
│   ├── ADR Template                            261324852
│   ├── Runbook Template                        261423105
│   └── Component Template                      261259287   a tree to copy
│       ├── Component Template — Overview       261521416
│       ├── Component Template — PRDs           261357639
│       ├── Component Template — Decisions      261324879
│       ├── Component Template — Design         261324896
│       └── Component Template — Runbooks       261357656
└── Archive                                     261357569   replaced pages, never deleted
```

Read a page directly with `getConfluenceContent` and its ID. Use `detail: full` and
`content_format: html` when you intend to edit it.

## The principle

The **type** of document decides where it lives. The **component** is its branch of the tree.
The **status** is a label. Nothing is stored in two places.

## Where does this go?

| Writing… | Parent | Create from |
|---|---|---|
| What to build and why, for one component | `<component> — PRDs` | PRD Template |
| How a PRD will be built | the PRD page | Technical Plan Template |
| The quality check on a plan | the PRD page | Consistency Analysis Template |
| A decision about one component | `<component> — Decisions` | ADR Template |
| A decision across components | `Platform → Decisions` | ADR Template |
| How a component is structured today | `<component> — Design` | free form |
| A procedure to operate something | `<component> — Runbooks` | Runbook Template |
| A rule every repository follows | `Platform → Standards` | free form |
| A change to how we work | `Platform → Process` | free form |

## Naming

Confluence needs **unique titles across the whole space**, so titles carry their context.

| Page | Title |
|---|---|
| Component | `<component>` (same name as the Jira Component) |
| Component sections | `<component> — Overview`, `— PRDs`, `— Decisions`, `— Design`, `— Runbooks` |
| PRD | `PRD: <title>`, no number: it is identified by its page, whose ID survives a rename |
| Technical plan | `Technical Plan — <title>` (same title as its PRD) |
| Consistency analysis | `Consistency Analysis — <title>` |
| ADR | `ADR-NNNN: short imperative title`, numbered per scope, never reused |
| Runbook | `<component> — Runbook: <task>` |

If two components both reach `ADR-0001`, add the component name to the title.

## Labels

| Kind | Labels |
|---|---|
| Type | `prd`, `plan`, `analysis`, `adr`, `runbook`, `design`, `process`, `template` |

**The state of a page is not a label.** Nothing can remove a label (the MCP has no such
operation), so the state lives in a **status lozenge** in the Status row of the summary table,
which can be replaced: `DRAFT`, `IN REVIEW`, `APPROVED`, `SUPERSEDED` for a PRD or a plan;
`PROPOSED`, `ACCEPTED`, `SUPERSEDED` for an ADR. A Consistency Analysis and a Runbook have no
Status row. The only label of a page is its type.

The component is **not** a label: it is the page's position in the tree. Add labels with
`addLabelsToConfluenceContent`.

## Summary table

Every document type opens with a two-column table of its key facts (status, component, owner,
links, dates). Keep it current. The templates already contain it:

| Document | Rows |
|---|---|
| PRD | Status, Component, Audience, Priority, Deadline, Jira Epic(s), Technical Plan, Consistency Analysis, Related ADRs, Last updated |
| Technical Plan | Status, PRD, Component, Phases, Analysis verdict, Last updated |
| Consistency Analysis | PRD, Technical Plan, Date, Passes, Findings, Requirement coverage, Verdict |
| ADR | Status, Date, Scope, Related |
| Runbook | Component, Owner, Last verified, Risk, Estimated time, Needs approval, Trigger, Related |
| Overview | Component, Type, Lifecycle, Repository, Jira, Owner, Stack, Release process, Published at |

The PRD, plan and analysis sections match what the `/prd`, `/plan` and `/analyze` skills
produce (REQ-n, NFR-n, SC-n, OQ-n; modules table, phases; findings table, coverage, verdict).

## Recipes

**Create a document page.** Use the `confluence-create-doc` skill. The templates of the PRD,
Technical Plan, Consistency Analysis, ADR and Runbook are kept in that skill (`assets/`) and the
page is created in one call; the pages under `Templates` are generated mirrors that are neither
copied nor read. Only the `Component Template` tree is still copied with
`copyConfluenceContent` (see "Add a component").

**Add a component.** Create the Jira Component first (the MCP cannot: Jira UI or
`jira_template.py`), then run the `confluence-create-component` skill, which does the rest. By
hand, the steps are:
1. Create the Jira Component in JTTC with the component name.
2. Copy `Component Template` (261259287) under `Components` (261324818), renaming it to the
   component name, and its five children renaming `Component Template` to the component name.
3. **Copying a page does not copy its children** (verified 2026-11-01: the copy of
   `Component Template` had no descendants). Copy each of the five children yourself under the
   new page, with its own title: Overview `261521416`, PRDs `261357639`, Decisions `261324879`,
   Design `261324896`, Runbooks `261357656`. Then list the descendants and check there are five.
4. Fill in the Overview summary table. Remove the warning panel from the copy.

**Write a PRD.** Copy PRD Template under `<component> — PRDs`, title `PRD: <title>`, label
`prd`. Create the two children from the plan and analysis templates when reaching
that stage. On approval set the Status lozenge to `APPROVED`. If an Epic is created, put its key in the
summary table and link the PRD from the Epic (`createJiraIssueRemoteIssueLink`).

**Record a decision.** Copy ADR Template under the right Decisions page, number it. Its Status
lozenge is `PROPOSED` until it is set to `ACCEPTED`. To reverse one, write a new ADR and mark the old one
`SUPERSEDED`, linking both ways.

**Approve a plan.** A Technical Plan can only go to `APPROVED` when its Consistency Analysis exists
and its verdict is `Ready`; `confluence-update-doc` refuses otherwise. The person who reviews the
plan decides, and the skill records it.

**Retire a page.** Set its Status lozenge to `SUPERSEDED` and add a first line pointing to the replacement, then move it
under Archive with `moveConfluenceContent` (`position: append`). Never delete.

## PRD and Epic

The common case is one PRD and one Epic. It is a default, not a rule: a PRD may produce
several Epics or only Stories, and a small Epic may have no PRD. When both exist, link them
both ways: the Epic key in the PRD summary table, and a link to the PRD from the Epic.

## Editing pages

Prefer targeted edits over rewriting a page. Read it with `detail: full` and
`content_format: html`, then use `edits` with `replaceNode` on the node's `data-local-id`. A
`dryRun: true` first validates the result without saving. Pass the latest `snapshotToken` and
re-read after any `snapshot_stale` error.

Use `<div data-type="extension" data-extension-key="children" ...>` for child-page lists, as
the existing section pages do. Never use Confluence storage XML (`ac:structured-macro`): it
renders as raw text.

## What does not belong here

Secrets, tokens or personal data (name where they live instead). Task status (it lives in
Jira). Release and deployment history (it lives in GitHub). Meeting notes with no lasting
decision.
