# Configuration checklist — Project, Issue Type, Components

`prd`, `plan`, `analyze`, `prd-to-issues`, `refine-story`, `iteration-plan`, `execute-feature`,
`complete-feature`, `report-bug` and `tdd` share this model.
Before using them for the first time, a team needs the following already set up — none of it is
something the skills create on their own:

1. **Issue Types "PRD", "Feature", "Bug", and "Task"** — created at the organization level
   (Settings → Issue types). Issue Types require an organization; a personal-account owner has
   no Issue Types, and `prd`/`prd-to-issues`/`report-bug`/`iteration-plan` fall back to a
   `prd`/`feature`/`bug`/`task` label respectively in that case. A `Bug` (filed by `report-bug`)
   goes through the same `refine-story` → `iteration-plan` → `execute-feature` →
   `complete-feature` flow as a Feature.
2. **A shared GitHub Project (v2)** with these single-select/number custom fields:
   - `Component` — one option per repo these skills create issues into (e.g. `FACTORY CLUSTER`,
     `FACTORY DISPATCHER`).
   - `Phase` — `Discovery` and `Execution` both needed and both actively used: every PRD and
     Feature lives at `Discovery` until `iteration-plan` finishes breaking a Feature down, at
     which point the Feature (and every sub-task `iteration-plan` creates, from the start) moves
     to `Execution`. `prd`/`plan`/`analyze`/`prd-to-issues` only ever write `Discovery`.
   - `Status` — GitHub Projects' 5 defaults (`Backlog`, `Ready`, `In Progress`, `In Review`,
     `Done`) are reused across both phases — the same `Status` value means something different
     depending on `Phase` (e.g. `Ready` + `Discovery` means "ready for `/iteration-plan`"; `Ready`
     + `Execution` means "fully broken down, ready for the execution orchestrator" — always read
     `Status` and `Phase` together, never `Status` alone, past this point). Discovery needs 5
     more options added alongside the defaults: `Planning`, `Analysis`, `Ready for Breakdown`,
     `Broken Down`, and `Refining` — set by `plan`, `analyze`, `prd-to-issues`, and `refine-story`
     respectively as a PRD/Feature moves through Discovery; `iteration-plan` also reuses
     `Planning` while it's actively breaking a Feature down. `prd`/`plan`/`analyze`/
     `refine-story` treat a missing Status option as best-effort (warn, don't block); only
     `prd-to-issues` treats a missing `Component`/`Phase` option as a hard stop. Execution needs
     one more option after `Done`: `Released`. `Done` + `Execution` means "merged into the base
     branch" (set by `complete-feature`; dependents are unblocked); `Released` means "shipped
     and validated" — see "Release and release-candidate bugs" below.
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
triggered by a `Status`/`Phase` change on a Feature (`Status: Refining` for `refine-story`;
`Status: Ready` + `Phase: Discovery` for `iteration-plan` — `Status` alone is never enough to
trigger the right skill, since `Status: Ready` also occurs at `Phase: Execution`, meaning
something entirely different) — this is a current requirement of this pipeline, not a future
possibility. Both detect headless execution via the `GITHUB_ACTIONS` env var (set automatically
by every Actions job) and switch their behavior: no `AskUserQuestion`, gaps become named
assumptions instead of questions, and proposals publish directly instead of waiting for
approval. See each skill's own `SKILL.md` ("Detecting headless execution") for the exact
mechanism and what still fails visibly (a broken `Status`/`Phase` precondition always does,
headless or not). The webhook → Actions wiring itself is a separate, already in-progress piece
of work, not part of either skill.

`execute-feature` — the execution orchestrator `iteration-plan` hands off to — follows the same
detection when triggered on `Status: Ready` + `Phase: Execution` + Issue Type `Feature`/`Bug`.
`complete-feature` follows it too, triggered on a different kind of event: a PR merged into the
base branch (the job passes the PR number). So does `report-bug`, which has no board trigger of
its own: a job (or `execute-feature`'s final review, for faults outside the Feature's diff)
calls it with the fault and its origin as arguments.

## Execution (`execute-feature`)

On top of everything above, `execute-feature` needs:

- **`Status` options `In progress`, `In review`, `Done`** (GitHub defaults — matched
  case-insensitively). Missing ones are a warning, never a blocker.
- **A base branch.** `next` by default, or the `Base branch` key in `AGENTS.md`/`CLAUDE.md`.
  `main` stays the stable branch and only ever receives `next`. If `next` doesn't exist,
  `execute-feature` creates it from the default branch — the only push it ever makes outside a
  feature branch. Protecting `main`/`next` is up to the team.
- **Features merged into `next`**: `Closes #n` only fires on the default branch, so a merge into
  `next` leaves the issue open. `complete-feature` moves it to `Status: Done` (run by hand, or by
  the job on the PR merged event) and leaves it open until it is `Released`. `execute-feature`
  doesn't depend on that having run — it also treats a blocker as resolved once its
  `feature/<n>-*` PR is merged into the base branch.
- **The `task-executor` agent** (shipped with this plugin) — the worker that implements one
  sub-task in its own git worktree under `.claude/worktrees/`. The orchestrator never merges a
  PR: sub-task → feature branch is merged autonomously, feature branch → `next` always by a
  human.

## Release and release-candidate bugs

`Done` and `Released` are two different points in a Feature's life, on purpose:

- **`Done`** — merged into the base branch (`complete-feature`). The Feature still counts as a
  **resolved blocker**: every Feature that depends on it can be executed. The issue stays open.
- **`Released`** — shipped and validated. Only then is the issue closed.

Bugs are filed with `report-bug`. How a Bug relates to the issue that introduced it (its
**origin**) depends on where it was found:

- **In review or during execution** — the origin's own work is finished, so it is **never
  blocked**: it keeps moving `In review` → `Done`. The Bug records it under `## Origin` and
  comments on it. Whatever can't proceed without the fix is blocked explicitly (`--blocks`).
- **In a release candidate** (`report-bug --found-in <rc>`) — a release candidate is built from
  `next` and deployed; a fault there means the origin, already `Done`, must not be `Released`.
  The Bug is then also set as a native blocker (`blockedBy`) of the origin. Dependents stay
  unblocked — the origin is still `Done` — but it can't move to `Released` while any of its
  blockers is open.

Either way the origin's `Status` and state are never touched. The Bug runs on a `bugfix/<n>-*`
branch; a `Done` Feature is never executed again.

Moving Features to `Released` is not automated by any skill yet — until it is, it's done by
hand, checking that the Feature has no open blocker.
