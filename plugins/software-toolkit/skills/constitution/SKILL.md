---
name: constitution
description: Initialize or update this repo's AGENTS.md/CLAUDE.md with its GitHub Component self-declaration and its project constitution (core principles, constraints, workflow, governance), inspired by GitHub spec-kit's /constitution command. Use whenever the user wants to set up a repo for the prd/plan/analyze/prd-to-issues workflow, declare which Component this repo is, write or update a project constitution, or run "/constitution", "init constitution", "set up this repo for PRD workflow", "what component is this repo", or any variation of registering a repo's identity and rules for this toolkit.
---

# /constitution — Repo Identity and Constitution

Initialize or update this repo's `AGENTS.md`/`CLAUDE.md` with two things: the repo's
**self-declared `GitHub Component`** (so `prd-to-issues` can discover this repo without a
hand-maintained central table), and its **project constitution** — the rules `plan` and
`analyze` validate future plans against.

## Step 0 — Check for an existing constitution

Look for `AGENTS.md` or `CLAUDE.md` in the repo root. If one exists and already has a
constitution (a `## Core Principles` section, or similar), show it to the user and ask:
*"This repo already has a constitution. Update it, or just review it as-is?"*
- **Review only** → print it and stop.
- **Update** → carry its current content into Step 3 as the starting draft, don't discard it.
- **Neither file exists** → continue to Step 1 with a blank draft.

---

## Step 1 — Declare the Component

Ask: *"Which GitHub Component is this repo? (e.g. `FACTORY CLUSTER`)"*

If a GitHub Project is already known (configured, or the user mentions one), check that this
Component is already a valid option on the Project's `Component` field:

```bash
gh project field-list <project-number> --owner <owner> --format json
```

If the option doesn't exist, **warn, don't create it**: *"The Project's `Component` field has
no option named `<component>` — ask a board admin to add it, or double-check the name."* The
user can still proceed (the self-declaration in `AGENTS.md` doesn't require the Project option
to exist yet), but they should know it's missing.

---

## Step 2 — Project config (optional)

Ask: *"Will `/prd` or `/prd-to-issues` ever be invoked directly from this repo?"*
- **Yes** → ask for `GitHub Project` (number or title) and `GitHub Project Owner`, to write into
  `AGENTS.md` alongside the Component.
- **No** → skip; this repo only needs its Component self-declaration so other repos' `/prd-to-
  issues` runs can discover it, plus its constitution for `plan`/`analyze` to validate against.

---

## Step 3 — Draft the constitution

Use `assets/constitution-template.md`. Gather with the user:
- **Core Principles** — the non-negotiable rules this codebase follows, each stated as a
  testable "MUST"/"MUST NOT", with a one-line reason. Pull from existing docs
  (`CONTRIBUTING.md`, `ARCHITECTURE.md`, READMEs) if they already state some of this — don't
  make the user re-type what's already written elsewhere, just confirm it still holds.
- **Additional Constraints** — stack/compliance/deployment constraints, only if genuinely
  non-negotiable. Omit the section if there are none.
- **Development Workflow** — what this repo actually enforces (review, testing gates,
  deployment approval), not an aspirational wishlist.
- **Governance** — how the constitution gets amended and how often it's revisited.

Show the full draft and iterate until the user approves. Keep it short — a constitution `plan`
and `analyze` will actually check against needs to be scannable, not exhaustive.

---

## Step 4 — Write the file

Write the Component declaration as its own section, with this **exact line** (the literal text
`GitHub Component: <name>` is what `prd-to-issues` greps for across the org — don't rephrase
it):

```markdown
## GitHub Component
GitHub Component: <name>
```

Then the constitution content from Step 3, and the `GitHub Project`/`GitHub Project Owner` keys
from Step 2 if collected.

- If **neither** `AGENTS.md` nor `CLAUDE.md` exists, create `AGENTS.md` with the full content,
  and create `CLAUDE.md` as a one-line pointer (`See AGENTS.md`).
- If **one exists already**, write the full content there; if the other is missing, add it as
  the one-line pointer.
- If **both exist with different content**, don't guess which is canonical — show both to the
  user and ask which one should hold the full content.

---

## Step 5 — Report

Tell the user what was written and where. Remind them: `plan` and `analyze` will read this file
to validate future plans against these rules, and `prd-to-issues` will find this repo by
searching for its `GitHub Component` declaration — if the Component name ever changes, this
skill needs to be re-run to update it (and any PRDs still referencing the old name on the shared
Project will need their `Component` field corrected too).

---

## Rules

- Never invent a Component name or constitution content without the user's input — this is
  their repo's identity, not a guess.
- Never create or modify the Project's `Component` field options — only warn if the option is
  missing.
- Keep the exact `GitHub Component: <name>` line unchanged in wording — `prd-to-issues` matches
  on this literal text.
- Don't discard an existing constitution when updating — carry it forward and edit, same as
  `analyze` never discarding existing acceptance criteria.
