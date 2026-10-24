---
name: refine-story
description: Refine a GitHub Feature issue (created by /prd-to-issues) into something ready to implement — full FR/NFR extraction, enriched Acceptance Criteria, Size/Estimate/Priority fields set, named assumptions instead of open questions. Moves Status from Backlog through Refining to Ready. Given an issue number, refines that one Feature; given none, refines every Feature currently in Backlog across the shared Project by dispatching one subagent per issue in parallel. Use whenever the user wants to refine a Feature, flesh out an issue before implementation, refine the whole backlog at once, or get a Feature ready for /iteration-plan. Also runs unattended inside a GitHub Actions job (no human present) when Status changes to Refining — trigger on "/refine-story", "refine issue #N", "refine this feature", "refine the backlog", "refine everything in backlog", "get this issue ready", or any variation of preparing one or more implementation issues for work.
context: fork
agent: refine-story
background: false
allowed-tools: Bash(gh issue *), Bash(gh api *), Bash(gh project *), Bash(gh repo *), Read, Grep, Glob, AskUserQuestion, Agent
---

# /refine-story — Refine a Feature

Take a GitHub Feature issue (created by `/prd-to-issues`, `Status: Backlog`) and refine it into
something a developer or AFK agent can implement without further clarification: full FR/NFR
coverage, enriched Acceptance Criteria, and `Size`/`Estimate`/`Priority` set on the Project.
Moves `Status` from `Backlog` → `Refining` → `Ready` (or leaves it at `Refining` with a comment
explaining what's missing).

Given an issue number, this refines that one Feature. Given no issue number, it instead refines
**every** Feature currently in `Backlog` across the shared Project — see Step 0.

This skill runs in an isolated `refine-story` subagent with no visibility into the conversation
that triggered it — the Feature issue number (or nothing, for the whole-backlog case) arrives as
the input and everything else (parent PRD, blockers, Project fields, management-repo docs) is
re-derived from GitHub.

**This also runs unattended.** A `Status` change to `Refining` is meant to trigger this skill
headless inside a GitHub Actions job, with no human able to answer a question — not as a future
plan, but as the real, current purpose of the `Refining` status. Every step below says exactly
what to do when no human is present. See "Detecting headless execution" right below — read it
before Step 1.

---

## Detecting headless execution

Check the environment once, at the start, and remember the answer for the rest of the run:

```bash
[ "$GITHUB_ACTIONS" = "true" ] && echo headless
```

`GITHUB_ACTIONS` is set by every GitHub Actions job automatically — no workflow-specific wiring
needed. Treat any other non-interactive indicator the invoking context gives you (e.g. a `CI`
env var, an explicit flag/argument passed in, or `AskUserQuestion` simply not being usable in
this particular run — see the note below) the same way. When headless:
- Never call `AskUserQuestion`. Every step that would normally ask instead records a **named
  assumption** in the issue and proceeds.
- Never wait for approval before publishing (Step 7). Publish directly; the review becomes
  post-hoc.
- Step 1's `Status` gate is a hard stop either way, not something that becomes a question with a
  human present — headless just means that stop has to be visible (non-zero exit / clear error
  message) so the Actions job shows red, instead of a message nobody reads.

**Never write any of this detection/mechanism into the issue** — not in the body, not in the
session comment, not anywhere published. Whether a run was headless, why `AskUserQuestion`
wasn't used, which environment variable triggered it, or who/what executed the skill, is never
relevant to a reader of the issue and only creates confusion. Write the assumption itself (what
was decided, and why, in terms of the actual feature) — never a sentence about the tooling or
session that produced it. This applies identically whether the run genuinely had no human
available or simply couldn't reach one in practice (e.g. `AskUserQuestion` not returning the way
expected even in an interactive session) — the reader never needs to know which case it was.

---

## Step 0 — Resolve scope: one issue, or every Backlog Feature

If an issue number was given as input, skip straight to Step 1 — everything in this step is
specific to the no-argument case.

**If no issue number was given**, this run becomes the **batch orchestrator**: refine every
Feature currently sitting in `Backlog` across the shared Project, each as its own independent
`refine-story` run, dispatched in parallel via the `Agent` tool rather than processed one after
another in this same context (same reasoning as everywhere else in this pipeline — keep each
Feature's refinement isolated, don't let fifteen Features' worth of context pile up in one run).

1. Resolve the Project (`GitHub Project`/`GitHub Project Owner`) exactly as
   `prd-to-issues/references/github.md` ("Resolving the shared Project") describes.
2. List every Project item with `Status: Backlog` **and** Issue Type `Feature` — see
   `references/github.md` ("Listing Backlog Features") for the exact query. This excludes PRDs
   (which also sit at `Backlog` before `/plan` runs) and `Task` sub-tasks (which
   `/iteration-plan` also creates at `Backlog`) — only Features are this skill's job.
3. If none are found, report that and stop — nothing to do.
4. **With a human present**: show the full list (issue number, title, repo) and ask for
   confirmation before dispatching anything — this fans out into one subagent per issue, so
   confirm scope first. **Headless**: proceed without asking; a scheduled batch run is expected
   to just run.
5. Dispatch one `refine-story` agent per Feature found, each given that Feature's issue number
   as its entire input — exactly as if `/refine-story #N` had been invoked on it directly. Issue
   all dispatches in the same turn so they run in parallel rather than queued one-by-one. If more
   than ~20 Features are found, process them in batches of 20 rather than firing everything at
   once, to keep the fan-out manageable.
6. Wait for every dispatched run to finish, then go straight to Step 10 and produce **one
   consolidated report** covering every issue (number, final `Status`, and why for any that
   didn't reach `Ready`) — do not execute Steps 1–9 yourself in this mode; that work happens
   inside each dispatched subagent, not here.

---

## Step 1 — Fetch and gate

Read `references/github.md` ("Fetching the Feature") and fetch the issue plus its Project item's
`Status`.

This skill only ever runs on a Feature whose `Status` is `Backlog` (the manual case — someone
invoking it directly on a freshly-broken-down Feature) or `Refining` (already picked up, re-
running). Any other `Status` is a hard stop, human or headless, no exception and no "proceed
anyway" — this isn't an ambiguity to negotiate, it means the Feature either hasn't reached this
point in the pipeline yet or has already moved past it:

> _"Issue #N is in `Status: <status>` — `/refine-story` only runs on `Backlog` or `Refining`.
> Nothing to do here."_

Report this and stop — do not touch the issue in any way.

If `Status` was `Backlog`, set `Status = Refining` immediately once the gate passes (best-effort
— see `references/github.md` for the field update; a missing `Refining` option is a warning, not
a blocker, same philosophy as the rest of the pipeline). If it was already `Refining`, leave it
as-is — it's already where it needs to be.

---

## Step 2 — Gather full context

- The Feature's own body (already has "What to build" / Acceptance criteria / "Blocked by" from
  `prd-to-issues`).
- The parent PRD: follow `Parent PRD: #N` → `gh issue view` on it, including its **Success
  Criteria** section — there's no separate Epic concept in this pipeline, the PRD itself fills
  that role.
- Issues that block this one, via the native `Issue.blockedBy` connector (see
  `references/github.md`) — not the text "Blocked by" section, which is just the human-readable
  mirror of the same data.

---

## Step 3 — Extract FRs/NFRs

Classify each as ✅ clear, ⚠️ ambiguous, or ❓ gap.

- **With a human present**: ask the genuine gaps, max 5 per round, one round at a time via
  `AskUserQuestion`.
- **Headless**: do not ask. For every ⚠️/❓, write a **named assumption** directly into the
  issue body (same mechanism `/plan` already uses — "no open questions in the final draft;
  unresolved items become named assumptions") and proceed on that basis. Never leave a bare `❓`
  in the published body. State the assumption itself only ("deliveryId is sourced from the
  `X-GitHub-Delivery` header") — never why it had to be assumed instead of asked; that's
  session mechanics, not content (see "Detecting headless execution" above).

---

## Step 4 — Enrich Acceptance Criteria

Never discard an AC `prd-to-issues` already wrote — only improve wording or add missing ones so
every FR has at least one AC in Given/When/Then form.

Best-effort: if `GitHub Management Repo` is configured (see `references/github.md` —
"Reading the Definition of Done"), try to read `docs/DEFINITION_OF_DONE.md` from it. NFRs
already covered by a global DoD criterion (e.g. "tests exist for behavior added/changed" covers
a generic "must be tested" NFR) don't need their own redundant AC — reference the DoD instead.
If the config key is missing, or the file doesn't exist, or the repo is unreachable: don't block
or warn loudly — just treat every NFR individually, as if the key were never set.

---

## Step 5 — Set Size / Estimate / Priority

All three by direct judgment — there is no formula (no Business Value/Risk/Order Rank scoring in
this pipeline; GitHub has no equivalent field and no replacement formula was designed):

- **Size** (`XS`–`XL`) — confirm or adjust whatever `prd-to-issues` might already have set.
- **Estimate** (number) — Story Points, Fibonacci scale (1, 2, 3, 5, 8, 13) by convention, even
  though the field itself accepts any number.
- **Priority** — if the Project's `Priority` field has zero options configured, warn (don't
  block): *"The Priority field has no options configured on this Project — ask a board admin to
  add some (e.g. Low/Medium/High/Urgent), then re-run to set it."* Setting Priority is skipped,
  not faked, when this happens.

---

## Step 5b — Judge TDD-suitability and set the `tdd` label

Before this Feature reaches `/iteration-plan` (which judges this again per sub-task, see its own
`SKILL.md`), judge whether the Feature as a whole — in case it's small enough to be implemented
directly without going through `/iteration-plan` — is suited to test-first development: is
there a clear, testable public interface behind the behavior described in its ACs (see the
`tdd` skill's own `deep-modules.md`/`interface-design.md` for what "testable" means here), as
opposed to being primarily a spike, an architecture/interface decision with no settled behavior
yet, pure documentation, or infra/deployment work with nothing meaningfully unit-testable.

If yes, add the `tdd` label (see `references/github.md` — "Ensuring the `tdd` label exists").
If the issue currently has the label but no longer deserves it (e.g. refinement revealed it's
actually a spike), remove it. This is a judgment call re-evaluated every time this skill runs,
not a one-way ratchet.

---

## Step 6 — Readiness check

This is the GitHub Definition of Ready (see `docs/DEFINITION_OF_READY.md` in the `GitHub
Management Repo` — this check is its machine-readable version):

- `Size` is set.
- `Estimate` is set.
- Every FR has at least one AC.
- No `❓`/`⚠️` remains unresolved as a bare open question — everything is either resolved or
  recorded as a named assumption (Step 3).

**With a human present**, also ask directly: *"Does the team have enough understanding to
implement this?"* — a human can know something is still unclear in a way text analysis can't
catch.

**Headless**, that last question can't be asked — treat it as satisfied if and only if no bare
`❓`/`⚠️` remains (i.e., Step 3 fully converted every gap to a named assumption). Never default
this to "yes" when something is still genuinely open — if Step 3 couldn't resolve something even
as an assumption (rare, but possible for a totally missing dependency), the check fails here and
`Status` stays at `Refining`.

---

## Step 7 — Show the proposal (or publish directly if headless)

**With a human present**: show the full refined Feature (FRs/NFRs, enriched ACs, Size/Estimate/
Priority, any named assumptions) and iterate until approved — mirrors `/plan`'s own review loop.

**Headless**: there's no one to approve. Publish directly (Step 8) without waiting, and make
sure every named assumption is visible in the session comment so a human can review it
after the fact — the review becomes post-hoc, not a gate before publishing.

---

## Step 8 — Update the issue

Read `references/github.md` ("Updating the Feature") and:
1. Rewrite the issue body — same skeleton `prd-to-issues` used, plus the FR/NFR list and
   enriched ACs.
2. Post a session comment: decisions made, named assumptions, anything still open — never the
   field values themselves (those live on the Project, not in a comment). Never mention
   `AskUserQuestion`, headless detection, or any other session/tooling mechanics here either —
   irrelevant to a reader and only confusing, regardless of who or what ran the skill (see
   "Detecting headless execution" above).
3. Set `Size`/`Estimate`/`Priority` on the Project item (Step 5's values).
4. Add or remove the `tdd` label per Step 5b's judgment.

---

## Step 9 — Final Status transition

If Step 6's check passed: `Status = Ready` — this is this pipeline's own "ready to implement"
signal; nothing more needs to happen to reach that meaning here.

If it didn't pass: stay at `Refining`, and make sure the session comment (Step 8.2) states
exactly what's missing — this is what whoever (or whatever job) looks at the issue next needs in
order to pick up where this run left off.

---

## Step 10 — Report

**Single-issue mode**: tell the user (or, headless, make sure the session comment covers it) the
issue number, the final `Status`, the Size/Estimate/Priority set, whether the `tdd` label was
added/removed/left as-is, and a one-line pointer to the suggested next step: `/iteration-plan`
once `Status` reaches `Ready`.

**Batch mode** (Step 0): report one line per dispatched issue (number, title, final `Status`),
grouped into "Reached Ready" and "Still Refining" (with the blocking reason for each in the
latter group, taken from that issue's own session comment) — plus the total count dispatched.

---

## Rules

- Never discard an Acceptance Criterion `prd-to-issues` already wrote — only enrich.
- Business Value, Risk, and Order Rank are gone for good — do not reintroduce them or invent a
  replacement formula.
- Headless execution is a first-class path through every step above, not a hypothetical —
  design and test against it, don't treat it as an edge case.
- This skill only ever runs on `Status: Backlog` or `Status: Refining` — any other `Status` is a
  hard stop with "cannot refine", human or headless, never a "proceed anyway?" question.
- Never set `Status = Ready` while a bare `❓`/`⚠️` remains unresolved as an open question —
  resolve it or convert it to a named assumption first.
- `Priority` with no configured options is a warning, never a reason to block refinement.
- The `tdd` label is re-judged every run, not set once and forgotten — add it when the Feature
  has a clear testable public interface, remove it when refinement reveals it doesn't.
- Never publish anything about `AskUserQuestion`, headless detection, or session/tooling
  mechanics into the issue body or comment — write assumptions as plain decisions (what and
  why, in terms of the Feature itself), never as narration about how or why the run produced
  them. This holds no matter who or what actually executed the skill.
- With no issue number given, this skill becomes a batch orchestrator over every `Backlog`
  Feature — it dispatches isolated subagents per issue rather than refining several Features in
  one shared context.
