# Configuration checklist — Project, Issue Type, Components

`prd`, `plan`, `analyze`, `prd-to-issues`, `refine-story`, `iteration-plan`, and `tdd` share this
model.
Before using them for the first time, a team needs the following already set up — none of it is
something the skills create on their own:

1. **Issue Types "PRD", "Feature", and "Task"** — created at the organization level (Settings →
   Issue types). Issue Types require an organization; a personal-account owner has no Issue
   Types, and `prd`/`prd-to-issues`/`iteration-plan` fall back to a `prd`/`feature`/`task` label
   respectively in that case.
2. **A shared GitHub Project (v2)** with these single-select/number custom fields:
   - `Component` — one option per repo these skills create issues into (e.g. `FACTORY CLUSTER`,
     `FACTORY DISPATCHER`).
   - `Phase` — at least a `Discovery` option (an `Execution` option too, for when a future phase
     of this pipeline starts setting it — nothing today does, `iteration-plan`'s sub-tasks stay
     at `Discovery` same as their parent Feature).
   - `Status` — GitHub Projects' 5 defaults (`Backlog`, `Ready`, `In Progress`, `In Review`,
     `Done`) cover the Execution phase. Discovery needs 5 more options added alongside them:
     `Planning`, `Analysis`, `Ready for Breakdown`, `Broken Down`, and `Refining` — set by `plan`,
     `analyze`, `prd-to-issues`, and `refine-story` respectively as work moves through the
     pipeline. `prd`/`plan`/`analyze`/`refine-story` treat a missing Status option as
     best-effort (warn, don't block); only `prd-to-issues` treats a missing `Component`/`Phase`
     option as a hard stop.
   - `Size` (single-select, `XS`–`XL`) and `Estimate` (number, Story Points) — set by
     `refine-story` on the Feature. `iteration-plan` reads both but never writes `Estimate` (its
     own sub-task hour estimates live in the issue body text, not this field, to avoid mixing
     units).
   - `Priority` (single-select) — set by `refine-story` if the Project has options configured;
     otherwise `refine-story` warns and skips it rather than blocking. No default options ship
     with GitHub Projects, so a team that wants `Priority` actually used needs to add options
     itself (e.g. Low/Medium/High/Urgent) — same board-admin-action rule as everything else here.

   Both `refine-story` (on the Feature) and `iteration-plan` (per `development` sub-task) also
   set a `tdd` **label** — not a Project field, an ordinary repo label, created by either skill
   if missing (same low-stakes-local philosophy as `afk`/`hitl`). It marks work judged to have a
   clear, testable public interface; the `tdd` skill itself picks that label up as one of its own
   triggers when someone starts implementing the issue.
3. **`AGENTS.md`/`CLAUDE.md` config keys** (in the repo these skills are invoked from):
   - `GitHub Project` — the Project's number or title.
   - `GitHub Project Owner` — the Project's owner login (user or org); also used as the org to
     search when discovering a Component's repo (see below).
   - `GitHub Management Repo` (optional, format `<owner>/<repo>`) — a repo holding
     `docs/DEFINITION_OF_DONE.md` and `docs/DEFINITION_OF_READY.md` that `refine-story` tries to
     read best-effort when enriching Acceptance Criteria. Missing key, missing file, or
     unreachable repo are all treated the same way — fall through to enriching every NFR
     individually, never block or warn loudly. Not used by any other skill in this pipeline.
4. **Every repo that can receive implementation issues has run `/init-repo`**, which writes
   its self-declaration as the exact line `GitHub Component: <name>` in its own `AGENTS.md`/
   `CLAUDE.md`. There is **no central Component → repo table** — `prd-to-issues` discovers the
   right repo by searching the org for this declaration (`gh search code`). A repo that never
   ran `/init-repo` can't be found, and a Component declared in more than one repo is a
   conflict `prd-to-issues` will refuse to guess through.
5. **A `gh` token with the `project` scope** — `gh auth status` shows it under "Token scopes";
   if missing, the user runs `gh auth refresh -s project` themselves (interactive, not something
   either skill runs on your behalf).

If any of these is missing, all skills stop and tell the user what's missing rather than
guessing or creating it automatically — Issue Types, Project fields, and options are
board/org-admin actions, and a missing or duplicate `GitHub Component` declaration is something
only the user can resolve (which repo is it supposed to be?).

## Headless execution (GitHub Actions)

`refine-story` and `iteration-plan` are designed to run unattended inside a GitHub Actions job
triggered by a `Status` change (to `Refining` or `Ready` respectively) — this is a current
requirement of this pipeline, not a future possibility. Both detect this via the `GITHUB_ACTIONS`
env var (set automatically by every Actions job) and switch their behavior: no
`AskUserQuestion`, gaps become named assumptions instead of questions, and proposals publish
directly instead of waiting for approval. See each skill's own `SKILL.md` ("Detecting headless
execution") for the exact mechanism and what still fails visibly (a broken `Status` precondition
always does, headless or not). The webhook → Actions wiring itself is a separate, already
in-progress piece of work, not part of either skill.
