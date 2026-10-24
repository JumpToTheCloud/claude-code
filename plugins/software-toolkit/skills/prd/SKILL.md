---
name: prd
description: Convert a feature idea or description into a Product Requirements Document (PRD) and publish it as a GitHub issue with the native "PRD" Issue Type, added to the team's shared GitHub Project with its Component, Phase, and Status fields set. Use whenever the user wants to write a PRD, spec, or specification, formalize a feature, define requirements, create user stories, or document what to build. Always use this skill when the user mentions "prd", "spec", "specification", "requirements", "user stories", "acceptance criteria", or wants to turn any feature idea into a structured document.
---

# /prd — Product Requirements Document

Turn a feature description into a structured PRD and publish it as a GitHub issue. Always show
the full draft to the user for review before publishing.

## Step 0 — Resolve preconditions before drafting (fail fast)

Read `references/github.md` ("Step 0 — Resolve everything before drafting") and follow it now,
**before** asking the user anything in Step 1: resolve the "PRD" Issue Type, the shared Project,
the token's `project` scope, and the `Component`/`Phase` field IDs. If anything is missing, stop
and tell the user immediately — don't let them write and approve a whole PRD only to discover at
the end that the Project or Issue Type isn't set up. Also resolve the `Status` field's
`Backlog` option while you're there — unlike Component/Phase, treat a missing `Backlog` option
as best-effort (warn, don't block): it's a default GitHub Projects value, so its absence is
unusual, but losing it shouldn't stop a PRD from being created.

---

## Step 1 — Gather context

Scan the conversation history first. Prior discussion often already answers most of these. Only ask for what is genuinely missing or unclear — and batch all questions into a single message, never one at a time.

Collect:
- **Business motivation** — why is this being built? what problem does it solve and why now?
- **Audience** — who will read this PRD? (business stakeholders, engineers, or both — it affects tone and level of detail)
- **Priority** — how urgent is this? is it blocking anything? is there a deadline?
- **Related work** — is this related to an existing feature, PRD, or in-flight work?
- **Component** — which component/repo does this PRD belong to? Show the options already
  resolved from the Project's `Component` field in Step 0 (e.g. `FACTORY CLUSTER`,
  `FACTORY DISPATCHER`) — there is no separate table, the Project field options are the source
  of truth for valid names. A PRD belongs to exactly one Component — if the feature genuinely
  spans more than one repo, tell the user this should be split into separate PRDs rather than
  picking one Component arbitrarily. If the Component the user names isn't one of the Project's
  options, warn them (same as Step 0) but let them proceed if they insist — the repo still needs
  to have run `/init-repo` with that exact name for `prd-to-issues` to find it later.

---

## Step 2 — Research

Before drafting, gather relevant context from existing sources:
- Search for related issues on GitHub to avoid duplication and spot dependencies
- Explore the codebase if the feature touches something already implemented — understanding the current state makes requirements more precise
- Note any findings; they will inform the PRD content and the linking step at publish time

---

## Step 3 — Extract key concepts from the feature description

- Actors (who uses this?)
- Actions (what do they do?)
- Data (what entities are involved?)
- Constraints (what limits or rules apply?)

## Step 4 — Fill the PRD template

Use the template in `assets/prd-template.md`. Rules:
- All requirements must be testable — avoid vague verbs like "support", "handle", "manage"
- All success criteria must be measurable and tech-agnostic
- Mark genuine unknowns as `[NEEDS CLARIFICATION: <specific question>]` — max 3 total
- Remove optional sections that do not apply

## Step 5 — Resolve clarifications

If `[NEEDS CLARIFICATION]` markers remain, extract them and ask the user before showing the draft. At most 3 questions, prioritised by impact. The final draft must have zero unresolved markers.

## Step 6 — Show the draft for review

Show the full PRD to the user. Do NOT publish yet.

## Step 7 — Iterate

Incorporate feedback and go back to step 4 until the user approves.

## Step 8 — Confirm the destination and publish

Follow `references/github.md` Steps 1–3:
1. Show the resolved destination (repo, Project, Component, Phase) and get explicit
   confirmation — approving the PRD's content in Steps 6–7 is not the same as approving where
   it gets created.
2. Create the issue with the "PRD" Issue Type, directly inside the Project.
3. Set `Component` (from Step 1), `Phase = Discovery`, and `Status = Backlog` on the new
   Project item.

If related issues were found in Step 2, add cross-references in the issue body.

## Step 9 — Report

Tell the user the issue number, URL, Component, Phase, and Status, so they can share or
reference it.
Suggest running `/plan` next to turn this PRD into a technical plan.

---

## Rules

- Focus on **what** and **why**, never **how** — no languages, frameworks, file paths, or implementation details
- Tone and level of detail must match the audience identified in Step 1
- Written so any team member can understand it, not just engineers
- Keep it concise — every line must earn its place
- If the codebase needs exploring to validate assumptions, do it in Step 2 before drafting
- A PRD always has exactly one Component — never split field values across repos on the same PRD
- Never skip the Step 0 precondition check, even if the user seems in a hurry — failing fast
  here saves a full draft/review cycle if the Project or Issue Type isn't set up
