# atlassian-toolkit: design

Status: **agreed, not implemented** (decisions from a grill-me session, 2026-11-01).
Scope: this plugin only. `software-toolkit` is **not** touched yet.

## Goal

Let the spec-driven skills of `software-toolkit` (`prd`, `plan`, `analyze`, `prd-to-issues`,
`refine-story`, `iteration-plan`, `report-bug`, `execute-feature`, `complete-feature`) delegate
every Jira and Confluence write to this plugin. Some projects live in Jira, others in GitHub,
so the plugins are split by tracker and share one neutral contract.

## Decisions

| # | Decision |
|---|---|
| 1 | **Creation skills: one per top-level type, one for all sub-tasks.** The sub-task type (Development, Automation, Analysis, Architecture Design, Documentation) is a parameter. |
| 2 | **Three operation skills:** `jira-transition-issue` (finds the transition by target status, applies the gate: Gate 1 for `Refined`, Gate 2 for `Ready`, DoD for `Done`), `jira-update-issue` (fields, option IDs resolved at runtime, body sections), `jira-link-issues` (blocks, relates, PRD to Epic remote link, cycle check). Search and read use the MCP directly. |
| 3 | **One shared subagent, `atlassian-operator`,** preloads the skills (`skills:` frontmatter). The caller thinks and writes the content; the agent only validates, creates, links and returns keys. Callers pass **batches**, not one call per issue. Incomplete input is rejected, never invented. |
| 4 | **Two Confluence skills:** `confluence-create-doc` (type parameter: `prd`, `plan`, `analysis`, `adr`, `runbook`) and `confluence-update-doc` (status lozenge, Archive, Epic link, summary table, targeted edits by `data-local-id`). |
| 5 | **Issue-body templates: the skill is the source of truth** (`assets/` in the plugin). Confluence holds a read-only mirror under `Templates`, with a "generated, do not edit" disclaimer. |
| 6 | **The document templates (PRD, Technical Plan, Consistency Analysis, ADR, Runbook) also live in the plugin** (`confluence-create-doc/assets/*.html`), like the issue templates. This reverses the first decision (keep them in Confluence and copy by ID): after a copy the skill still has to read the copy, rebuild the whole body and rewrite it, so the copy saved nothing, and creating the page directly takes one call. The pages under `Templates` become generated mirrors. |
| 7 | **Neutral contract, Jira-specific implementation.** Input: `type`, `summary`, `sections`, `parent`, `blocked_by`, `mode`, `component`, `labels`, optional `extras` (Size, Risk, Business Value, ignored by other trackers). Output: `key`, `url`, `status`. A future `github-toolkit` implements the same contract. |
| 8 | **Two-level required fields.** The template carries every section from creation; only the entry-level ones block creation. The rest hold a `Pending refinement` marker that `refine-story` fills and removes. Gates are enforced in `jira-transition-issue`. |
| 9 | **Writes are automatic inside the agent.** The user approves the content in the main session; the agent does not ask again. `executeDestructive` is left out of the agent's `tools`. |
| 10 | **English everywhere** (templates, sections, skill names, issue content). Replies to the user follow the user's language. |
| 11 | **`confluence-sync-templates`:** manual maintenance skill (`disable-model-invocation`), OAuth through the MCP, no extra secrets. Converts the templates to Confluence HTML, adds the disclaimer, creates or updates the mirror pages. |
| 12 | **The Definition of Ready and Definition of Done live in the plugin** (`jira-transition-issue/references/`), like the issue templates, because the transition skill reads them on every gate and reading long Confluence pages costs time and tokens. The Confluence pages become generated mirrors. The only Confluence call a gate makes is the PRD approval check: it reads the PRD page and looks for the `APPROVED` status lozenge in its summary table. The PRD link may be a Jira remote link instead of text in the description. |
| 13 | **The Bug variant of Gate 1 is light.** It replaces Traceability, scope, requirements and the eight NFR categories with the bug analysis (component, origin when known, reproduction, expected vs actual, impact, root cause, affects version) and one NFR line. Acceptance criteria with the regression test, dependencies, estimation and change safety stay. `Affects version: none yet` is valid while the project has no versions; creating versions is later automation, not a blocker. |
| 14 | **The state of a Confluence page is a status lozenge, not a label.** The MCP has no operation to remove a label and the agent has no destructive tools, so a lifecycle label could never be changed. The Status row of the summary table holds a coloured status macro that can be replaced: `DRAFT`, `IN REVIEW`, `APPROVED`, `SUPERSEDED` for a PRD or plan; `PROPOSED`, `ACCEPTED`, `SUPERSEDED` for an ADR. The only label of a page is its type. Gate 1 reads the PRD's Status lozenge to check that the PRD is `APPROVED`. |
| 15 | **PRDs have no number, ADRs do.** A PRD is identified by its page ID and its unique title (the Epic key is the human reference). ADRs are numbered `ADR-NNNN`, consecutive per scope and never reused, because they form a chain of decisions that replace each other; the next number costs one query of the parent's children, plus one check afterwards that renames the page with the higher ID if two creations collided. |
| 16 | **A plan is approved only after its analysis says `Ready`.** There is no approval skill: `confluence-update-doc` with the operation `status` refuses to set a Technical Plan to `APPROVED` unless its Consistency Analysis exists and its Verdict row reads `Ready`. A human decides, the skill records it. ADR numbering is per component. |
| 17 | **`confluence-sync-templates` mirrors everything the plugin owns.** Besides the templates it regenerates the Definition of Ready and Done pages, the Templates index, the Component Template tree and "How this space works" (the page that said the state is a label), each with a generated-do-not-edit notice. It is not `disable-model-invocation`, because the agent that must run it preloads it (the main session would ask permission for each of the ~20 writes); its description limits it to explicit maintainer requests. |
| 18 | **The sync never writes without the maintainer's confirmation.** It runs in two steps: a preview that compares the rendered pages with the current ones and summarises what changes on each, and an execution that needs `confirmed: true`. The agent cannot talk to the maintainer, so the session that calls the skill shows the summary and asks; a general earlier approval does not count. Unchanged pages are skipped, so a run does not add empty versions. |
| 19 | **The Definition of Ready and Done say what must be true; `how-gates-are-applied.md` says how the skill applies it.** The two definitions are the team's agreement, free of Jira details, and are the only ones mirrored to Confluence. Which move runs which gate, how each criterion is checked or encoded in Jira (remote links, the `No PRD` line, the Status lozenge, `none yet`, the evidence for Done) and what the skill can and cannot verify live in `jira-transition-issue/references/how-gates-are-applied.md`. Changing a definition is a change of the agreement; changing the other file is a change of the tool; both go through a pull request. |

## Skill inventory

| Group | Skills |
|---|---|
| Jira creation | `jira-create-epic`, `jira-create-story`, `jira-create-task`, `jira-create-bug`, `jira-create-subtask` |
| Jira operations | `jira-transition-issue`, `jira-update-issue`, `jira-link-issues` |
| Confluence | `confluence-create-doc`, `confluence-update-doc`, `confluence-create-component` |
| Maintenance | `confluence-sync-templates` (also mirrors the DoR, DoD and the space guide) |
| Reference | `jttc-workspace` (exists) |
| Agent | `atlassian-operator` |

## Required fields by type

Always required by Jira at creation: project, issue type, summary, reporter, **Component**
(exactly one). A sub-task also requires **Parent**.

| Type | Required **at creation** (blocks) | Filled **at refinement** (`Pending refinement`) |
|---|---|---|
| **Epic** | Component, expected outcome, PRD link (or `No PRD` + reason), Out of scope, success criteria (SC-n) | n/a |
| **Story** | Component, Parent (Epic), As a / I want / so that, link to PRD and REQ-n, Out of scope, initial AC in Given/When/Then | FR-n, NFR per category, enriched AC, dependencies and `Assumption:` lines, feature flag, Story Points, Size, Business Value, Risk |
| **Task** | Component, Parent, outcome, *Done when* (2 to 5 lines), linked source | files to touch, Mode, estimate |
| **Bug** | Component, environment and Affects version, reproduction steps, expected vs actual, impact and severity | root cause (or investigation sub-task), AC with the regression test |
| **Sub-task** | Component, Parent, sub-task type, goal, minimal context, exact file paths, steps, AC covered, tests, estimate in hours (at most 8), Mode | n/a (born complete from Gate 2) |

**Do not repeat in the body what Jira already stores in a field or a link.** The Epic is the
`parent` field. The PRD and related ADRs are Jira remote links to their Confluence pages,
created by the creation skill right after the issue. The body only keeps a line when there is
no PRD (`No PRD: <reason>`) or requirement IDs to list. Later changes to links go through
`jira-link-issues` (phase 3).

Sub-tasks are created in `Backlog` (single initial status); the iteration plan moves the whole
set to `Ready` once it passes Gate 2. `tdd` is a label; AFK/HITL is the **Mode** field.

## Templates

Each template in `assets/` follows one uniform structure so the skill can validate it without a
duplicated list:

- sections are H2 headings with fixed names;
- a "Required fields" table: Jira field, who fills it (creation or refinement), allowed values;
- a "Template" notice panel, ignored when copying.

The Confluence mirror is generated from these files by `confluence-sync-templates`.
`jttc-workspace` Rule 1 ("read the live page") keeps applying to the Definition of Ready and
the Definition of Done, but no longer to issue-body templates.

## Permissions

The existing hook (`hooks/approve-read-only.sh`) approves reads only. It will be extended to
approve non-destructive writes (`createJiraIssue`, `editJiraIssue`, links, transitions,
comments, Confluence create/update). `tools` in an agent's frontmatter restricts what it can
call; it does not approve calls.

## Technical checks (phase 1 pilot, 2026-11-01)

1. `mcp__plugin_atlassian-toolkit_atlassian__*` tool names in a plugin agent's `tools`:
   **works**.
2. Hook identifying a subagent call: the hook approves on `agent_id` in its input. The agent
   wrote without blocking, but it was **not confirmed** that the hook (and not another
   mechanism) approved the calls. Re-check when a write is seen to prompt.
3. `skills:` frontmatter preload in a plugin agent: **works**.
4. Duplicate check: the same input a second time returned `duplicate` and created nothing.
5. Template guidance must stay outside the `body` markers, or it leaks into the issue. Each
   template has a "Guidance (not posted)" section for this.
6. Neither the agent nor the MCP can delete issues. Test data is removed with
   `acli jira workitem delete --key <KEYS> --yes`.
7. Batch failures: a **validation** failure creates nothing from the batch. An **execution**
   failure (API error half way) keeps what was created and reports `created` and `failed` per
   row; re-running the same batch is safe because the duplicate check skips what exists.
8. The estimate needs `timetracking` on `JTTC Default Screen`; the MCP cannot read it back.
9. **Skills must make skipped steps visible.** In the first runs the agent skipped reads that
   the skills only implied (the parent of a sub-task, the existing links before a cycle check,
   the Component list). Every skill now has a **step 0 of mandatory reads** with the exact
   call, and a mandatory `Checks:` line after its table listing what was done. The agent has
   hard rules: follow every step, report `not verified: <step>` instead of writing when one
   cannot be done, never fill a gap from the input. The hardened texts are **not yet tested**.
## Phases

| Phase | Content |
|---|---|
| 0 | This document (done) |
| 1 | Neutral contract, the five issue templates, pilot `jira-create-story`, agent `atlassian-operator`, hook extension (**done**, pilot verified against JTTC) |
| 2 | `jira-create-epic`, `jira-create-task`, `jira-create-bug`, `jira-create-subtask` (**done**, tested against JTTC: mixed batch of nine issues, estimate stored, remote links, a six-item invalid batch rejected with nothing created) |
| 3 | `jira-transition-issue`, `jira-update-issue`, `jira-link-issues` (**done**, fully tested against JTTC: links and cycle check; Gate 1 refusal and pass; light Bug Gate 1 pass; Gate 2 refusal for a sub-task whose Files lists a directory or omits its test file, and pass once fixed, with the sub-tasks moved together; Task from Ready to Done with and without evidence; update read-back and all-or-nothing batches) |
| 4 | `confluence-create-doc`, `confluence-update-doc`, `confluence-create-component` (**tested against Confluence**: the five document types from the templates in the plugin, rejections, automatic links between PRD, plan and analysis, status lozenge changes, retire to Archive, plan approval refused with a `Needs work` verdict and accepted with `Ready`, component bootstrap and its rejection. **Pending:** the Gate 1 check of the PRD status in Jira, and two ADRs created at the same time) |
| 5 | `confluence-sync-templates` (**done**: previewed, confirmed by the maintainer and run for 18 pages in four groups, with the 5 issue templates created under Templates; the group `quality` (Definition of Ready and Done) was previewed and **deliberately not applied**: the maintainer cancelled it because the plugin files had summarised some detail of the Confluence pages (the table of questions of the eight non-functional categories, the Epic retrospective detail, the branch-name example, `tsc --noEmit`, the rollback rehearsal). Both Confluence pages keep their old text until the files are completed and the sync is run again; the files stay the source of truth, changed by pull request); update `jttc-workspace` (Rule 1, gotchas) and the README |

## Out of scope

- Changing `software-toolkit` so its skills delegate here, and how a repo declares whether it
  uses Jira or GitHub (a later decision, probably through `init-repo`).
- The legacy unprefixed Jira skills (`refine-story`, `iteration-plan`, `user-story`) that still
  assume the old CDKX workflow.
- A `github-toolkit` plugin.
