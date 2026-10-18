---
name: analyze
description: Run a consistency analysis across a spec (GitHub issue written by /prd) and its technical plan (posted by /plan as a comment on the same issue). Detects duplication, ambiguity, underspecification, constitution violations, coverage gaps, and inconsistencies — then posts the findings back as a comment. Acts as a quality gate before running /prd-to-issues. Trigger when the user says "/analyze", "analyze issue #N", "analyze this PRD", "check spec and plan", "review consistency", "validate artifacts", or wants to cross-check spec and plan before breaking into issues.
context: fork
agent: analyze
background: false
allowed-tools: Bash(gh issue *), Bash(gh api *), Bash(gh project *), Bash(gh repo *), Read, Grep, Glob, AskUserQuestion
---

# /analyze — Consistency Analysis

Cross-check a spec and its technical plan for quality issues, then post the findings back as a
comment on the same issue. Acts as a quality gate before running `/prd-to-issues`.

This skill runs in an isolated `analyze` subagent with no visibility into the conversation that
triggered it — the issue number arrives as the input and everything else is re-derived from
GitHub (`gh issue view`) and the repo's constitution file. This keeps the spec, plan, and
constitution text out of the main session's context.

## Step 0 — Fetch the spec and plan

The spec and plan are always on the same GitHub issue. Read `references/github.md` for the exact
fetch and publish commands. If the plan is missing, stop and ask the user to run `/plan` first.

---

## Step 1 — Load the constitution

Look for `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or `ARCHITECTURE.md`, in that order —
first one found is the project's constitution for Pass D (constitution alignment), same
resolution order `plan` uses. If none exist, skip Pass D and note its absence in the report.

---

## Step 2 — Run 6 detection passes

Cap findings at 50 total across all passes. For each finding, record its ID, category, severity, location, a one-line summary, and a concrete recommendation.

**A. Duplication** — Requirements or user stories that say the same thing in different words. Mark the lower-quality phrasing as the duplicate.

**B. Ambiguity** — Vague adjectives without measurable criteria ("fast", "scalable", "secure", "easy to use"). Unresolved placeholders (`TODO`, `TBD`, `???`, `[NEEDS CLARIFICATION]`).

**C. Underspecification** — Requirements with a missing object or outcome. Success criteria without a measurable threshold. User stories with no acceptance criteria alignment.

**D. Constitution alignment** — Plan decisions that conflict with `CLAUDE.md` MUST rules. Constitution violations are always CRITICAL — no exceptions.

**E. Coverage gaps** — Functional requirements from the spec with no corresponding plan phase; plan phases that address no spec requirement; non-functional requirements absent from the plan.

**F. Inconsistencies** — Terminology drift (same concept named differently across spec and plan). Entities referenced in the plan but absent from the spec. Conflicting requirements.

---

## Step 3 — Assign severity

- **CRITICAL**: Constitution violation, missing core artifact, requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance criterion, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Wording improvements, minor redundancy

---

## Step 4 — Show the report for review

Show the full analysis to the user. Do NOT publish yet.

Use this template:

```markdown
## 🔍 Consistency Analysis

### Findings

| ID | Category | Severity | Location | Summary | Recommendation |
|----|----------|----------|----------|---------|----------------|
| A1 | Duplication | MEDIUM | REQ-3, REQ-7 | Both state the same upload constraint | Remove REQ-7, merge into REQ-3 |
| D1 | Constitution | CRITICAL | Plan › Modules | Proposes standalone `export function` | Wrap in a static class method |

### Coverage Summary

| Requirement | Has Plan Phase? | Phase | Notes |
|-------------|----------------|-------|-------|
| REQ-1 | ✅ | Phase 1 | |
| REQ-4 | ❌ | — | No phase maps to this requirement |

### Metrics
- Total functional requirements: N
- Requirements with plan coverage: N (N%)
- Critical issues: N
- High issues: N
- Medium issues: N
- Low issues: N

### Verdict
> ✅ Ready for `/prd-to-issues` — no critical issues found.
>
> — or —
>
> ❌ Not ready — N critical issue(s) must be resolved first. Re-run `/plan` to address D1.
```

---

## Step 5 — Iterate

Incorporate feedback (back to Step 2) until the user approves. If the user wants to fix a finding first, help them update the relevant artifact, then re-run the affected detection passes.

---

## Step 6 — Publish

Follow the publish instructions in `references/github.md` — post the analysis as a comment on
the same issue.

---

## Step 7 — Report

Tell the user where the analysis was posted. If no critical issues were found, confirm they can proceed with `/prd-to-issues`. If critical issues exist, explicitly recommend resolving them first and suggest which skill to re-run (`/prd` or `/plan`).

---

## Rules

- This skill is **read-only with respect to GitHub** until the user approves.
- Do not suggest rewriting the spec or plan inline — only report findings and recommendations.
- If the user asks to fix a finding, help them update the relevant artifact first, then re-run the affected passes.
- Constitution violations (`CLAUDE.md` MUST rules) are always CRITICAL — no exceptions.
- Do not invent issues — only report what is verifiably present in the artifacts.
