---
name: plan
description: Turn a spec (GitHub issue written by /prd) into a structured technical plan with architecture decisions, affected modules, interface contracts, and phased implementation — then post it back as a comment on the same issue. Trigger this skill when the user says "/plan", "plan issue #N", "plan this PRD", "create a technical plan", "implementation plan for #N", "how should we implement issue #N", "break this spec into phases", or any variation of wanting to plan a feature from a GitHub issue. Also trigger when the user has just created a PRD (via /prd) and wants to move to the planning stage.
---

# /plan — Technical Plan

Turn a spec (a GitHub issue written by `/prd`) into a structured technical plan with
implementation phases, then post it back as a comment on the same issue.

## Step 0 — Fetch the spec

The spec is always a GitHub issue. Read `references/github.md` for the exact fetch and publish
commands, then follow the instructions below. If the issue is empty or has no actionable
content, tell the user and stop.

---

## Step 0b — Check you're in the right repo (if a Component is set)

If the PRD issue has a `Component` set on the shared GitHub Project (see
`prd-to-issues/references/github.md` — "Resolving the shared Project", for how to look up the
issue's Project item and its `Component` value), discover which repo self-declares that
Component (same org-wide `gh search code` lookup `prd-to-issues` uses). Compare it against the
current repo (`gh repo view --json nameWithOwner`). If they don't match:

> _"This PRD's Component resolves to `<component-repo>`, but you're currently in `<current-
> repo>`. Switch to a checkout of `<component-repo>` for accurate codebase exploration, or
> continue with a plan based on the spec and constitution alone (no code exploration)?"_

If there's no Project/Component on this PRD at all, skip this check — plan from wherever you
are.

---

## Step 0c — Mark the PRD as `Planning` (best-effort)

If `GitHub Project`/`GitHub Project Owner` are configured in `AGENTS.md`/`CLAUDE.md`, find the
PRD's Project item (see `prd-to-issues/references/github.md` — "Finding a Project item for an
existing issue") and set its `Status` to `Planning`.

This is tracking, not a requirement: if the Project isn't configured, or the `Status` field is
missing the `Planning` option, warn once (e.g. "couldn't mark Status=Planning: <reason>") and
move on — never block producing the plan over this.

---

## Step 1 — Explore the codebase

Understand the impact area before drafting — a plan written without reading the code often
conflicts with existing patterns or misses key interfaces. Skip this step entirely if Step 0b
ended with the user choosing not to explore. Look for:
- Which packages and modules the feature touches
- Existing patterns to follow or extend (don't invent when convention exists)
- Relevant data structures and interfaces
- A project constitution — `CONSTITUTION.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or
  `ARCHITECTURE.md`, first one found in that order (none of these are written by this toolkit
  today — `init-repo` only writes repo identity, not rules — so this is only relevant for repos
  that already have one by other means) — note architecture rules and coding conventions to
  validate against later

Delegate this exploration to the `Explore` agent when the codebase is large or the impact area
is unclear, to keep this skill's own context focused on the spec and the plan being drafted.

---

## Step 2 — Resolve genuine unknowns

If exploration surfaces questions that would prevent a credible plan, ask them inline — max 3, one at a time, waiting for each answer before asking the next. Only ask what you genuinely can't determine from the code or spec. The final draft must have no open questions; if something remains unknowable, state it as a named assumption.

---

## Step 3 — Draft the plan

Use the template in `assets/plan-template.md`.

---

## Step 4 — Validate against project rules

If you found a project constitution in Step 1, check the plan against it. Flag any deviations with explicit justification. Skip the "Project Rules Check" section from the template if no constitution exists.

---

## Step 5 — Show the draft for review

Show the full plan to the user. Do NOT post yet.

---

## Step 6 — Iterate

Incorporate feedback (back to Step 3) until the user approves.

---

## Step 7 — Publish

Follow the publish instructions in `references/github.md` — post the plan as a comment on the
same issue.

---

## Step 8 — Report

Tell the user where the plan was posted. Suggest running `/analyze` next to cross-check the spec
and this plan before breaking the work into issues with `/prd-to-issues`.

---

## Rules

- **Phases map to the spec's user stories**: each phase delivers user-visible value, not internal scaffolding.
- **Phase 1 is always a tracer bullet**: a thin end-to-end slice that is demoable and validates the architecture early. If Phase 1 is "set up project structure" or "create the database schema", it's not a tracer bullet — push it to include a real user-facing interaction.
- **No open questions in the final draft**: unresolved items become named assumptions, never dangling questions.
- **Omit template sections that don't apply**: a plan without data model changes doesn't need a Data Model section. Shorter plans are easier to act on.
- **Don't re-specify what existing skills already own**: if the project has skills for conventional commits, testing, or linting, reference them by name — don't reproduce their rules in the plan.
- **Status tracking is best-effort**: missing Project config or a missing `Planning` option is a warning, never a reason to stop producing the plan.
