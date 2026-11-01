---
name: confluence-update-doc
description: Change an existing document page in the Confluence space JTTC - set rows of its summary table, replace a section, change its status (the status lozenge in the summary table: DRAFT, IN REVIEW, APPROVED, SUPERSEDED, or PROPOSED, ACCEPTED for an ADR), retire it (SUPERSEDED, pointer to the replacement, move under Archive) and link its Jira Epic or child pages. Uses targeted edits on the page nodes, never a full rewrite, and never deletes a page or removes a label. Use when a PRD, plan, analysis, ADR or runbook changes after it was created, or the user says "approve the PRD", "update the status", "add the Epic to the PRD", "supersede this ADR", "archive this page", "aprobar el PRD". Creating a page belongs to confluence-create-doc.
---

# confluence-update-doc

Maintains documents that already exist in the Confluence space JTTC. The caller decides the
change; this skill checks it and applies it with targeted edits. Cloud ID
`41be3e35-e509-4a4c-93e1-5460248e11ab`, space key `JTTC`. Pages are HTML. Never use Confluence
storage XML. Archive page: `261357569`.

## Status lozenge (the state of a page)

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

## Input

A list of operations. Each has `page` (URL or ID) and one of:

| `op` | Fields | Effect |
|---|---|---|
| `summary` | `rows`: map of row label to new value (text or links) | Sets those rows of the summary table |
| `section` | `heading`, `content` (markdown) | Replaces the content under an existing heading |
| `status` | `value`, `date` | Replaces the Status lozenge with `value` (one of the values of the table above for that page) and sets Last updated |
| `retire` | `replacement` (URL), `date` | Sets the Status lozenge to `SUPERSEDED`, writes a first line pointing to the replacement and moves the page under Archive |

The caller always passes `date` as `YYYY-MM-DD`: the agent has no clock.

## Steps

0. **Mandatory reads. Do them first, even when the change looks trivial.** For every page:
   `getConfluenceContent` with `detail: full` and `content_format: html`. Keep its HTML, its
   `snapshotToken` and the `data-local-id` of the nodes you will touch. Never edit from memory
   or from an earlier read.
1. **Validate every operation before writing any.** If one fails, write nothing from the batch
   and return the problems per operation.
   - the page exists and is a document page (it has a type label; ask `searchConfluence` with
     `cql: id = <id> AND label in ("prd","plan","analysis","adr","runbook")`);
   - `summary`: every row label exists in the page's summary table;
   - `section`: the heading exists, and the new content is not empty;
   - `status`: the page has a Status row, `value` is valid for that page type, and it is not
     already the current value; a `SUPERSEDED` page cannot change status;
   - `status` `APPROVED` on a **Technical Plan**: its Consistency Analysis must exist and its
     verdict must be `Ready`. Find it with `searchConfluence`,
     `cql: parent = <PRD id> AND title ~ "Consistency Analysis"`, read it with
     `getConfluenceContent` (`detail: full`, `content_format: html`) and look at the `Verdict`
     row of its summary table. No analysis, or any verdict other than `Ready`, rejects the
     operation and says which. A human reviews the plan and decides; the skill only refuses to
     record an approval that the analysis does not support. A PRD has no such precondition;
   - `retire`: a `replacement` is given and it is an existing page of the space.
2. **Edit with targeted operations** through `updateConfluenceContent`: `contentId`,
   `snapshotToken`, `edits`, `versionMessage`. Always run first with `dryRun: true` and check
   the resulting HTML, then repeat without it. Use the latest `snapshotToken`; on
   `snapshot_stale` read the page again and reapply, never resend the same payload.
   - `summary`: `replaceNode` on the paragraph inside the cell next to the row label.
   - `section`: `insertNodeAfter` the heading with the new HTML, then `deleteNode` for each old
     node up to the next heading.
   - `status` and `retire`: `replaceNode` on the **paragraph** inside the Status cell with a new
     `<p><span data-type="status" data-color="..." data-status-style="bold">TEXT</span></p>`.
     Never replace the `<span>` itself: it nests a paragraph inside a paragraph and the dry run
     produces invalid HTML. Do the same on the paragraph of the Last updated cell, when the page
     has that row; for `retire` also
     `insertNodeBefore` the first node of the body with a paragraph
     `Superseded by <a href="<replacement>">...</a>`. If the edit is rejected, load the guide with
     `executeRead`, `name: getContentFormatGuide`, `inputs: {toolName: "updateConfluencePage"}`.
3. **Retire only:** move the page with `executeWrite`, `name: moveConfluenceContent`,
   `inputs: {id: <page>, position: "append", targetId: "261357569"}`. For an ADR, also edit the
   replacement page so it points back (a `summary` change on its Related row), so both pages
   link each other. Never delete a page.
4. **Read back** each page with `getConfluenceContent` (`detail: full`, `content_format: html`)
   and confirm the changed rows, the lozenge text and colour, the sections and the first line.

## Output

| page | op | status |
|---|---|---|
| PRD: ... | approve | `updated`, or `rejected: <reason>` |

**Checks line (mandatory).** After the table write one line `Checks:` that lists what you
actually did, per page, for example `Checks: page read (html, snapshot v:3); validated; dry run
clean; edit applied; lozenge APPROVED confirmed; read back`. A check that is not listed was not
done, and if it was not done nothing may have been written.

## Never

- Rewrite a whole page body: edit nodes.
- Delete a page.
- Change the status of a SUPERSEDED page, or set a status that is not in the table.
- Retire a page without a replacement, or leave it outside Archive.
- Apply an edit that the dry run did not accept.
- Edit a template page.
