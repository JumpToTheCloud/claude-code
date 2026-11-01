---
name: confluence-create-component
description: Bootstrap the Confluence side of a new component in the space JTTC - the component page under Components and its five children (Overview, PRDs, Decisions, Design, Runbooks), with the Overview summary table filled. The Jira Component must already exist: the skill checks it and refuses when it does not. Use whenever a new repository or library becomes a component (for example a new cdk8s library), or the user says "create the component", "bootstrap the component in Confluence", "nuevo componente", "crear el árbol del componente". It does not create the Jira Component (the MCP cannot) nor the repository.
---

# confluence-create-component

Creates the documentation tree of a component in the Confluence space JTTC. One component per
repository, with the **same name** as its Jira Component. Cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, space key `JTTC`, space ID `223412226`, Components page
`261324818`. Pages are written in **English**, as **HTML** bodies. Never use Confluence storage
XML. The templates are in `assets/`; the `Component Template` pages in Confluence are generated
mirrors that are neither copied nor read here (a copy would not bring the children anyway).

## The tree it creates

```
Components
└── <component>                  assets/component.html
    ├── <component> — Overview   assets/overview.html
    ├── <component> — PRDs       assets/prds.html
    ├── <component> — Decisions  assets/decisions.html
    ├── <component> — Design     assets/design.html
    └── <component> — Runbooks   assets/runbooks.html
```

PRDs, ADRs and runbooks are not part of it: they are created later with `confluence-create-doc`.

## Input

| Input | Required | Notes |
|---|---|---|
| `component` | yes | The name, exactly as the Jira Component |
| `lifecycle` | no | `Experimental` (default), `Active`, `Maintenance` or `Deprecated` |
| `repository` | yes | The repository URL |
| `owner` | yes | Who decides for this component |
| `stack` | yes | Language, framework, main tools |
| `purpose` | yes | What it is and why it exists, in two or three sentences |
| `release_process` | no | How it is released (written as `—` when absent) |
| `published_at` | no | Registry, URL or environment where it lives (`—` when absent) |

## Steps

0. **Mandatory reads. Do them first, in this order, even when the input looks complete.**
   Skipping one is a failure of the whole run, not a shortcut.
   - **Jira Component.** `executeRead` with `name: listJiraProjectComponents`,
     `inputs: {projectIdOrKey: "JTTC"}`. The `component` must be in the list. If it is not,
     reject: the Jira Component has to be created first (the MCP cannot create it: it is done in
     the Jira UI or with `jira_template.py`).
   - **Titles.** `searchConfluence` with
     `cql: title in ("<c>", "<c> — Overview", "<c> — PRDs", "<c> — Decisions", "<c> — Design", "<c> — Runbooks") AND space = "JTTC"`.
     Any result means the component already exists: report it and create nothing. Titles are
     unique across the whole space, so the component name is a prefix of every page.
1. **Validate before writing.** Every required input is present and not empty, `lifecycle`
   has an allowed value, `repository` is an absolute `https` URL. If anything fails,
   write nothing and return the problems.
2. **Create the component page** with `createConfluenceContent`: `cloudId`,
   `contentType: page`, `title: <component>`, `parent: {parentContentId: "261324818"}`,
   `body: {format: "html", value: <assets/component.html>}`. Replace `{{component}}` with the
   name. Keep its ID.
3. **Create the five children**, one call each, with `parent: {parentContentId: <component page
   ID>}` and the titles `<component> — Overview`, `— PRDs`, `— Decisions`, `— Design`,
   `— Runbooks`, each body built from its file. Build the Overview body from `overview.html`:
   - `{{row:Component}}` the name; `{{row:Lifecycle}}` the value;
   - `{{row:Repository}}` an inline smart link `<a href="URL" data-card-appearance="inline"></a>`;
   - `{{row:Jira}}` an inline smart link to
     `https://jumptothecloud.atlassian.net/issues/?jql=project%20%3D%20JTTC%20AND%20component%20%3D%20%22<component>%22`
     (the component name URL-encoded);
   - `{{row:Owner}}`, `{{row:Stack}}`, `{{row:Release process}}`, `{{row:Published at}}` the text, or
     `—`;
   - `{{section:Purpose}}` the purpose as `<p>`. The other Overview sections keep their short
     italic prompts: it is a starting point to fill in later, and this is the one place where a
     prompt sentence stays.
   If a body is rejected, load the format guide with `executeRead`, `name: getContentFormatGuide`,
   `inputs: {toolName: "createConfluencePage"}` and retry once.
4. **Read back.** `executeRead` with `name: getConfluenceContentDescendants`,
   `inputs: {contentId: <component page ID>}` must list exactly the five children with their
   titles; `getConfluenceContent` with `detail: outline` on the Overview must show the sections;
   no page may contain `{{`.

## Output

| page | id | url | status |
|---|---|---|---|
| <component> | 123456 | https://jumptothecloud.atlassian.net/wiki/spaces/JTTC/pages/123456 | `created` or `rejected: <reason>` |

Then one row per child. If a child fails after others were created, keep what exists and report
each page as `created` or `failed`; running the skill again reports the existing titles and
creates nothing, so finish the missing page by hand or with `confluence-create-doc` rules.

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you
actually did, for example `Checks: Jira Component listed; titles searched (none exist); input
validated; component page and five children created; descendants listed (5); Overview outline
read; no template marker left`. A check that is not listed was not done, and if it was not done
nothing may have been written.

## Never

- Create the tree when the Jira Component does not exist, or when any of the six titles exists.
- Copy the `Component Template` pages: a copy does not bring the children.
- Create a PRD, ADR or runbook here.
- Leave a template marker (`{{...}}`) on a page.
- Write storage XML or put secrets, tokens or personal data in a page.
