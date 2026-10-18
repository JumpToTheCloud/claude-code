---
name: init-repo
description: Initialize this repo's AGENTS.md/CLAUDE.md with its GitHub Component self-declaration and (optionally) its GitHub Project, so prd-to-issues can discover this repo. Use whenever the user wants to set up a repo for the prd/plan/analyze/prd-to-issues workflow, declare which Component this repo is, link a repo to a GitHub Project, or run "/init-repo", "init repo", "set up this repo for PRD workflow", "what component is this repo", or any variation of registering a repo's identity for this toolkit.
context: fork
agent: init-repo
background: false
allowed-tools: Read, Grep, Glob, AskUserQuestion, Edit(AGENTS.md), Edit(CLAUDE.md), Bash(gh project *), Bash(gh repo *), Bash(git status*), Bash(git add*), Bash(git commit*), Bash(git push*)
---

# /init-repo — Repo Identity

Initialize or update this repo's `AGENTS.md`/`CLAUDE.md` with its **self-declared `GitHub
Component`** (and, if relevant, its `GitHub Project`/`GitHub Project Owner`) — so `prd-to-issues`
can discover this repo without a hand-maintained central table.

This skill runs in an isolated `init-repo` subagent with no visibility into the conversation
that triggered it, and with `bypassPermissions` — it only interrupts the user for the content
questions below (Component, Project, commit/push confirmation), never for permission to
read/write the two files it's scoped to.

This skill does **not** write any engineering rules/constitution — just repo identity. A
dedicated development-setup skill for that is planned separately.

## Step 1 — Declare the Component

Ask: *"Which GitHub Component is this repo? (e.g. `FACTORY CLUSTER`)"*

If a GitHub Project is already known (configured, or the user mentions one), check that this
Component is already a valid option on the Project's `Component` field:

```bash
gh project field-list <project-number> --owner <owner> --format json
```

If the option doesn't exist, **warn, don't create it**: *"The Project's `Component` field has
no option named `<component>` — ask a board admin to add it, or double-check the name."* The
user can still proceed (the self-declaration doesn't require the Project option to exist yet),
but they should know it's missing.

---

## Step 2 — Project config (optional)

Ask: *"Will `/prd` or `/prd-to-issues` ever be invoked directly from this repo?"*
- **Yes** → ask for `GitHub Project` (number or title) and `GitHub Project Owner`, to write into
  `AGENTS.md` alongside the Component.
- **No** → skip; this repo only needs its Component self-declaration so other repos' `/prd-to-
  issues` runs can discover it.

---

## Step 3 — Write the identity block

```markdown
GitHub Component: <name>
GitHub Project: <number-or-title>       (only if collected in Step 2)
GitHub Project Owner: <owner>           (only if collected in Step 2)
```

The literal line `GitHub Component: <name>` is what `prd-to-issues` greps for across the org —
don't rephrase it.

**Where this goes, depending on what's already there:**
- **Neither `AGENTS.md` nor `CLAUDE.md` exists** → create `AGENTS.md` with just this block
  (under a `## Project Identity` heading), and create `CLAUDE.md` as a one-line pointer
  (`See AGENTS.md`).
- **One exists already with unrelated content** (e.g. full of other project docs) → append the
  block at the end, under its own `## Project Identity` heading, separated by a blank line from
  whatever precedes it. Do not touch, reformat, or renumber the existing content's own headings
  — always give the block its own heading so it never reads as unlabeled trailing text.
- **One exists and already has a `## Project Identity` block** (Component or Project changed) →
  replace just that block in place, leaving the rest untouched.
- **Both exist with different substantial content** → don't guess which is canonical — show
  both to the user and ask which one should hold the full content; the other becomes (or stays)
  a one-line pointer.

---

## Step 4 — Report, then offer to commit and push

Tell the user what was written and where. Remind them: `prd-to-issues` will find this repo by
searching for its `GitHub Component` declaration — if the Component name ever changes, this
skill needs to be re-run to update it (and any PRDs still referencing the old name on the shared
Project will need their `Component` field corrected too).

**This declaration is invisible to `prd-to-issues` until it's on GitHub.** `gh search code`
indexes the remote repo, not your local working tree — writing the file isn't enough. Check
`git status`; if `AGENTS.md`/`CLAUDE.md` are uncommitted or unpushed, say so explicitly and ask:
*"These changes aren't committed/pushed yet, so `prd-to-issues` can't discover this repo until
they are. Want me to commit and push them now?"* If yes, commit directly with a Conventional
Commits message (e.g. `docs(repo): declare GitHub Component`) and push — no need to go through
the `conventional-commits` skill for a change this small. Don't commit or push without that
explicit go-ahead.

---

## Rules

- Never invent a Component name — this is the user's repo identity, not a guess.
- Never create or modify the Project's `Component` field options — only warn if the option is
  missing.
- Keep the exact `GitHub Component: <name>` line unchanged in wording — `prd-to-issues` matches
  on this literal text.
- Never commit or push without the user's explicit go-ahead in Step 4.
- Don't write any constitution/engineering-rules content — that's out of scope for this skill.
