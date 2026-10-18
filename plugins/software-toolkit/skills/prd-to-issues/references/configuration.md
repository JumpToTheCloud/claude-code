# Configuration checklist — Project, Issue Type, Components

`prd` and `prd-to-issues` share this model. Before using either for the first time, a team
needs the following already set up — none of it is something the skill creates on its own:

1. **Issue Type "PRD"** — created at the organization level (Settings → Issue types). Issue
   Types require an organization; a personal-account owner has no Issue Types, and `prd` falls
   back to a `prd` label in that case.
2. **A shared GitHub Project (v2)** with two single-select custom fields:
   - `Component` — one option per repo these skills create issues into (e.g. `FACTORY CLUSTER`,
     `FACTORY DISPATCHER`).
   - `Phase` — at least a `Discovery` option (an `Execution` option too, for when a future
     GitHub port of `iteration-plan` starts setting it).
3. **`AGENTS.md`/`CLAUDE.md` config keys** (in the repo `/prd`/`/prd-to-issues` is invoked from):
   - `GitHub Project` — the Project's number or title.
   - `GitHub Project Owner` — the Project's owner login (user or org); also used as the org to
     search when discovering a Component's repo (see below).
4. **Every repo that can receive implementation issues has run `/init-repo`**, which writes
   its self-declaration as the exact line `GitHub Component: <name>` in its own `AGENTS.md`/
   `CLAUDE.md`. There is **no central Component → repo table** — `prd-to-issues` discovers the
   right repo by searching the org for this declaration (`gh search code`). A repo that never
   ran `/init-repo` can't be found, and a Component declared in more than one repo is a
   conflict `prd-to-issues` will refuse to guess through.
5. **A `gh` token with the `project` scope** — `gh auth status` shows it under "Token scopes";
   if missing, the user runs `gh auth refresh -s project` themselves (interactive, not something
   either skill runs on your behalf).

If any of these is missing, both skills stop and tell the user what's missing rather than
guessing or creating it automatically — Issue Types, Project fields, and options are
board/org-admin actions, and a missing or duplicate `GitHub Component` declaration is something
only the user can resolve (which repo is it supposed to be?).
