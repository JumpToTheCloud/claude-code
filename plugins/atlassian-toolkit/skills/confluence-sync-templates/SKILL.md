---
name: confluence-sync-templates
description: Maintenance skill. Regenerates the read-only Confluence mirrors of what the atlassian-toolkit plugin keeps as source of truth - the issue templates (Epic, Story, Task, Bug, Sub-task), the document templates (PRD, Technical Plan, Consistency Analysis, ADR, Runbook), the Component Template tree, the Definition of Ready and Definition of Done pages, the Templates index and the page "How this space works" - each with a "generated, do not edit" notice. It always previews first with a summary of what would change on every page, and writes only after the maintainer has read the summary and confirmed. Use ONLY when a maintainer explicitly asks to sync, regenerate or refresh the Confluence templates or process pages after the plugin changed; never run it on your own initiative.
---

# confluence-sync-templates

The plugin is the source of truth for the templates, the Definition of Ready, the Definition of
Done and the space guide. Confluence only **mirrors** them for people to read. This skill
rewrites the mirrors from the plugin files, one way only: the plugin is read, Confluence is
written, and nothing is ever read back from a mirror to learn a rule. Because it overwrites pages
that the whole team reads, **it never writes without a confirmation from the maintainer**.

Cloud ID `41be3e35-e509-4a4c-93e1-5460248e11ab`, space key `JTTC`, space ID `223412226`. Pages are
written in **English**, as **HTML**. Never use Confluence storage XML.

**Plugin root.** `${CLAUDE_PLUGIN_ROOT}`. If it does not resolve to a path, `Glob`
`**/atlassian-toolkit/skills/jttc-workspace/SKILL.md` and take the folder three levels above it.
All sources below are relative to the plugin root.

## Two steps, and who does what

The agent that runs this skill cannot talk to the maintainer, so the confirmation belongs to the
session that called it.

1. **Preview.** The caller runs the skill with `confirmed` absent or `false`. The skill reads the
   sources and the current pages and returns a summary of what would change on every page. It
   writes nothing.
2. **Confirmation (the caller).** The caller shows the maintainer the summary, as it came, and
   asks whether they agree: apply everything, apply only some groups, or cancel. A silence, an
   earlier general approval or a "go on" that did not follow a summary is not a confirmation.
3. **Execution.** Only after a yes, the caller runs the skill again with `confirmed: true`, and
   with `only` if the maintainer narrowed the groups. The skill writes only what the preview
   announced.

**The skill writes only when it receives `confirmed: true` literally.** With anything else it
returns the preview.

## What is mirrored

| Group | Page (ID, or title) | Source | Rendering |
|---|---|---|---|
| `issues` | `Epic Template` (new, under Templates `261226498`) | `skills/jira-create-epic/assets/epic-template.md` | markdown |
| `issues` | `Story Template` | `skills/jira-create-story/assets/story-template.md` | markdown |
| `issues` | `Task Template` | `skills/jira-create-task/assets/task-template.md` | markdown |
| `issues` | `Bug Template` | `skills/jira-create-bug/assets/bug-template.md` | markdown |
| `issues` | `Sub-task Template` | `skills/jira-create-subtask/assets/subtask-template.md` | markdown |
| `documents` | PRD Template `261357620` | `skills/confluence-create-doc/assets/prd.html` | template |
| `documents` | Technical Plan Template `261423134` | `.../assets/plan.html` | template |
| `documents` | Consistency Analysis Template `261390366` | `.../assets/analysis.html` | template |
| `documents` | ADR Template `261324852` | `.../assets/adr.html` | template |
| `documents` | Runbook Template `261423105` | `.../assets/runbook.html` | template |
| `component` | Component Template `261259287` | `skills/confluence-sync-templates/assets/component-template-root.html` | verbatim |
| `component` | Component Template — Overview `261521416` | `skills/confluence-create-component/assets/overview.html` | template |
| `component` | Component Template — PRDs `261357639` | `.../assets/prds.html` | template |
| `component` | Component Template — Decisions `261324879` | `.../assets/decisions.html` | template |
| `component` | Component Template — Design `261324896` | `.../assets/design.html` | template |
| `component` | Component Template — Runbooks `261357656` | `.../assets/runbooks.html` | template |
| `quality` | Definition of Ready `223281170` | `skills/jira-transition-issue/references/definition-of-ready.md` | markdown |
| `quality` | Definition of Done `223281157` | `skills/jira-transition-issue/references/definition-of-done.md` | markdown |
| `guides` | Templates `261226498` | `skills/confluence-sync-templates/assets/templates-index.html` | verbatim |
| `guides` | How this space works `261390383` | `skills/confluence-sync-templates/assets/how-this-space-works.html` | verbatim |

## Input

| Input | Required | Notes |
|---|---|---|
| `date` | yes | `YYYY-MM-DD`: the agent has no clock |
| `only` | no | A list of groups (`issues`, `documents`, `component`, `quality`, `guides`). Default: all five |
| `confirmed` | no | `true` only after the maintainer confirmed a preview. Default `false`: preview only |

## Rendering

Every page starts with this notice, written as a warning panel, followed by the rendered source:

```
<div data-type="panel-warning"><p><strong>Generated mirror. Do not edit this page.</strong>
Source: <code>PATH</code> in the <code>atlassian-toolkit</code> plugin.
Synced on DATE. Anything written here is overwritten the next time the templates are synced.
To change it, open a pull request on the plugin.</p></div>
```

`PATH` is the source path relative to the plugin root. No version is written: a release would
make it stale.

- **verbatim**: the file, without its leading `<!-- ... -->` comment, after the notice.
- **template** (HTML templates with markers): remove the leading comment, then replace
  `{{component}}` with `&lt;component&gt;`; each `{{row:<label>}}` with `<em><label></em>`, except
  the Status row, which shows the initial lozenge (`DRAFT` neutral for a PRD or plan,
  `PROPOSED` blue for an ADR); each `{{section:<heading>}}` with
  `<p><em>The content of this section.</em></p>`. After the notice add an info panel listing the
  required and optional sections and the required summary rows of that type, copied from the
  tables of `skills/confluence-create-doc/SKILL.md` (for the Component Template children, none).
- **markdown**: convert to HTML with `<h2>`, `<h3>`, `<p>`, nested `<ul>` and `<ol>`, `<table>`
  with `<thead>`, `<strong>`, `<em>`, `<code>`, `<blockquote>` and `<pre><code>`. Drop the
  `<!-- body:start -->` and `<!-- body:end -->` markers and keep what is between them. A
  `{{placeholder}}` is shown as `<code>{{placeholder}}</code>`. Keep the file's headings, so the
  page reads like the file. Do not use task lists: plain lists only.

## Steps

0. **Mandatory reads. Do them first, even when only one group is asked and even in a preview.**
   - `Read` every source of the selected groups **in full**, without `limit` or `offset`: a page
     cannot be rendered from the first lines of its file. A source that cannot be read rejects
     the whole run: report it and write nothing.
   - For every page with an ID, `getConfluenceContent` with `detail: full` and
     `content_format: html`. Its title must be the expected one; it gives the current body, to
     compare with the new one, and the `snapshotToken`. A different title or a 404 means the ID
     changed: report it and skip that page, never guess another page.
   - For the `issues` group, `searchConfluence` with
     `cql: title in ("Epic Template","Story Template","Task Template","Bug Template","Sub-task Template") AND space = "JTTC"`
     to know which exist (update) and which do not (create).
1. **Validate.** `date` is `YYYY-MM-DD`; every group in `only` is one of the five; `confirmed` is
   `true`, `false` or absent. If not, write nothing.
2. **Render and compare.** Render every page and compare it with the current body, ignoring
   whitespace and the `data-local-id` attributes. A page whose rendered text equals the current
   text is `no change` and is never written. For the others, list **what changes**, in at most
   four short bullets per page: headings added or removed, rules whose wording changed (quote the
   old and the new phrase when it is a rule, a status or a label), tables whose rows changed, and
   whether the page is new.
3. **Preview, unless `confirmed` is `true`.** Return the summary table below, a count (pages to
   update, to create, unchanged), and stop. End the report with the sentence `Nothing was
   written. Show this summary to the maintainer and ask for confirmation before running again
   with confirmed: true.`
4. **Write, only with `confirmed: true`, and only the pages the summary announced** (`update`
   or `create`; never a `no change` page).
   - Existing page: `updateConfluenceContent` with `contentId`, the `snapshotToken` of step 0,
     `body: {format: "html", value: <rendered>}` and `versionMessage: "Synced from
     atlassian-toolkit on <date>"`. This is the one place where a whole body is replaced, because
     the whole page is generated. On `snapshot_stale`, read the page again and retry once; if
     the page changed since the preview, do not write it and report it.
   - Missing issue template: `createConfluenceContent` with `contentType: page`, the title, `parent:
     {parentContentId: "261226498"}` and the body; then `executeWrite` with `name:
     addLabelsToConfluenceContent`, `inputs: {contentId, labels: [{"name": "template", "prefix":
     "global"}]}`.
   - If a body is rejected, load the guide with `executeRead`, `name: getContentFormatGuide`,
     `inputs: {toolName: "updateConfluencePage"}` (or `createConfluencePage`) and retry once.
   - A page that fails does not stop the others. Run order: `guides`, `component`, `documents`,
     `issues`, `quality`.
5. **Read back** (only after writing). For every written page, `getConfluenceContent` with
   `detail: summary`: the excerpt must contain `Generated mirror`. Then list the descendants of
   Templates (`executeRead`, `name: getConfluenceContentDescendants`,
   `inputs: {contentId: "261226498"}`): it must show the 5 document templates, the Component
   Template with its 5 children and the 5 issue templates.

Running the skill twice gives the same pages: unchanged pages are skipped, and it creates only
what is missing.

## Output

| page | id | action | what changes | status |
|---|---|---|---|---|
| ADR Template | 261324852 | update | drops "add the label adr-proposed"; adds the status lozenge row | `preview`, `ok`, `no change` or `failed: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you
actually did, for example `Checks: 20 sources read in full; 15 page bodies read; 15 titles
matched their IDs; 5 issue templates searched (0 existed); rendered and compared; preview only
(confirmed not true)`, or `... confirmed: true received; 14 pages written; 1 unchanged skipped;
read back (notice found); Templates descendants listed`. A check that is not listed was not done,
and if it was not done nothing may have been written.

## Never

- Write anything without receiving `confirmed: true`, or treat the caller's prose as a
  confirmation.
- Write a page the preview did not announce, or a page that has `no change`.
- Read a mirror page to learn a rule or a template: the plugin files are the only source. (The
  current body is read only to compare it with the new one.)
- Edit a page that is not in the table, or leave a mirror without its notice.
- Delete or move a page.
- Run on your own initiative: only when a maintainer asks.
- Write storage XML or put secrets, tokens or personal data in a page.
