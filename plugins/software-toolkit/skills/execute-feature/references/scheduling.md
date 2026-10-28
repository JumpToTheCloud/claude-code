# Scheduling — Tree, Worktrees, Quality Gate, Integration, Resume

Everything here runs from the user's checkout of the Feature's repo, but never changes it: every
command targets a worktree explicitly (`git -C <path>`, `pnpm --dir <path>`, `npm --prefix
<path>`) instead of `cd`-ing around.

---

## Building the tree

Nodes: the Feature's sub-issues. Edges: each sub-issue's native `blockedBy` pointing at a sibling.
Labels lowercased first.

1. **Cycle check** (DFS). A cycle is a hard stop naming the issues in it — `iteration-plan` is
   supposed to have prevented it, so it means the board was edited by hand.
2. **Classify**, in this order:
   - `done` — `state == CLOSED`.
   - `hitl` — open, and has `hitl`, or has neither/both of `afk`/`hitl`.
   - `skipped` — open `afk` with a `hitl` or `skipped` (or, during the run, `blocked`) sub-task
     anywhere among its transitive blockers.
   - `eligible` — open `afk`, every blocker `done` (cross-Feature blockers: closed only).
   - `waiting` — every other open `afk` sub-task.
3. Re-run classification after every integration and every block. `waiting` → `eligible` as
   blockers close; `waiting` → `skipped` when a blocker gets blocked.

What a worker should do is read off the labels:

| Labels | Worker approach |
|---|---|
| `development` + `tdd` | `tdd` skill, red-green-refactor, tests written first |
| `development` | implement per the body's Phases, plus the tests its ACs need |
| `automation` | integration tests per the body; prod code only for small bug fixes they expose |
| `documentation` | docs per the body |
| `spike`, `architecture-design` | always `hitl` per `iteration-plan` — never reaches a worker; if one is labelled `afk`, treat it as `hitl` anyway |

---

## Worktree layout

```
<repo-root>/.claude/worktrees/
├── _run/f<n>/                 # run directory: comment and PR body files for Feature <n>
├── f<n>/                      # integration worktree — feature branch checked out
└── f<n>-t<m>/                 # task worktree — temp branch <feature-branch>--t<m>
```

Before the first worktree, make sure the directory is ignored locally — never by committing a
`.gitignore` change:

```bash
git check-ignore -q .claude/worktrees/x || echo '/.claude/worktrees/' >> "$(git rev-parse --git-common-dir)/info/exclude"
```

**Integration worktree** (one per Feature):

```bash
git fetch origin
# fresh: new branch from the base
git worktree add .claude/worktrees/f<n> -b <feature-branch> origin/<base>
# resume: the pushed branch is the source of truth
git worktree add .claude/worktrees/f<n> -B <feature-branch> origin/<feature-branch>
```

**Task worktree** (one per running sub-task, always from the current feature tip):

```bash
git worktree add .claude/worktrees/f<n>-t<m> -b <feature-branch>--t<m> <feature-branch>
```

Leftover worktree or temp branch with the same name (from a crashed run) → remove it first
(`git worktree remove --force`, `git branch -D`).

**Dependencies**: install in every new worktree before dispatching or gating, by lockfile:
`pnpm-lock.yaml` → `pnpm --dir <wt> install --frozen-lockfile`; `package-lock.json` →
`npm --prefix <wt> ci`; `yarn.lock` → `yarn --cwd <wt> install --frozen-lockfile`; `go.mod` →
`go -C <wt> mod download`. An install failure is an environment problem, not a sub-task failure:
stop the run and report it.

---

## Quality gate

Resolved once in Step 3 from the repo, then run identically by workers (in their task worktree)
and by the orchestrator (in the integration worktree after each fast-forward).

**Node** (`<pm>` from the lockfile):
- **test** — the `test` script. If it runs `vitest` without `run`/`--run` (watch mode in a
  terminal), use `<pm> exec vitest run` instead so it never hangs.
- **typecheck** — a `typecheck`/`type-check`/`tsc` script if present; else, if `tsconfig.json`
  exists and `typescript` is a dependency, `<pm> exec tsc --noEmit`. Either way, tests must be
  type-checked too: if the root `tsconfig.json` excludes the test directory and a separate
  project exists for it (`test/tsconfig.json`, `tsconfig.test.json`, `tsconfig.spec.json`, …),
  add `<pm> exec tsc --noEmit -p <that file>` for each one.
- **lint** — the `lint` script, if present. No lint script → no lint step (never invent one).

**Go**: `go build ./...`, `go vet ./...`, `go test ./...`; plus `golangci-lint run` only if a
`.golangci.*` config exists.

**Neither**: `make test` / `make lint` if those targets exist; otherwise the gate is "the
sub-task's own verification steps" and the report says no automated gate was found.

**Baseline**: run the full gate once on the integration worktree right after creating it. Red at
baseline → hard stop before any sub-task starts (failures couldn't be attributed); report which
command fails.

A sub-task is done when, in its worktree: the full gate is green (whole suite, not just new
tests), every AC in its "Acceptance criteria covered" section maps to at least one test (or, for
`documentation`, to the doc section that satisfies it), and the worktree is clean (everything
committed).

---

## Dispatching a worker

`Agent` with `subagent_type: "software-toolkit:task-executor"`, `run_in_background: true`. The
prompt is self-contained — the worker sees nothing else:

```
Worktree: <absolute path to .claude/worktrees/f<n>-t<m>>   (work only here)
Feature: #<n> — <title>
Sub-task: #<m> — <title>
Labels: <lowercased labels>
Approach: <row from the table in "Building the tree">
Quality gate (run from the worktree): <test cmd> / <typecheck cmd> / <lint cmd>
Commit footer: Refs #<m> — the only trailer. No Co-Authored-By or any AI attribution, ever.

Sub-task body:
<full body, verbatim>

[Retry only] Previous attempt failed: <failure summary>. The worktree starts fresh from the
current feature tip, which now also contains: <sub-tasks integrated since>.
```

Never pass conversation history, other sub-tasks' summaries, or board state — only the above.

The worker answers in the format defined in `agents/task-executor.md`. Before treating
`RESULT: success` as success, verify it: commits listed exist on the temp branch
(`git -C <wt> log <feature-branch>..HEAD --oneline`), at least one commit exists, and
`git -C <wt> status --porcelain` is empty. Then check every new commit's message
(`git -C <wt> log <feature-branch>..HEAD --format='%s%n%b%n--'`): first line ≤ 72 characters,
ends with the `Refs #<m>` footer, and no `Co-Authored-By` or other AI attribution trailer. Any
mismatch is a failure — say exactly which rule in the retry prompt.

---

## Ready-queue loop

```
slots = 3 (global across Features in batch mode)
loop:
  while free slot and some sub-task is eligible:
      take lowest-numbered eligible → start it (comment, Status, worktree, deps, dispatch)
  if nothing running and nothing eligible: break
  wait for the next worker to finish
  success → integrate (serial); failure → retry once or block
  re-classify
```

Workers finish in any order; each completion is handled fully (integrate or block, re-classify,
refill slots) before looking at the next. Integration never runs in parallel.

---

## Integrating

In the integration worktree `<iwt>`, for task worktree `<twt>` and temp branch `<tb>`:

```bash
prev=$(git -C <iwt> rev-parse HEAD)
git -C <twt> rebase <feature-branch>          # conflict → git -C <twt> rebase --abort → failure
git -C <iwt> merge --ff-only <tb>
<gate in <iwt>>                                 # red → git -C <iwt> reset --hard $prev → failure
git -C <iwt> push -u origin <feature-branch>
git worktree remove <twt> && git branch -D <tb>
```

Only after the push succeeds: done comment, `Status: Done`, close. A rejected push (someone else
pushed to the feature branch) → stop the whole run and report; never force-push.

The integration worktree needs dependencies installed too (done at creation, refreshed with the
frozen-lockfile install when a sub-task changed the lockfile).

---

## Final review

Runs **exactly once per run**, from the orchestrator, only after the **last** sub-task has been
integrated and pushed — never per sub-task, never inside a task worktree, never by a worker.
Invoke the `code-review` skill at `medium` effort with the **feature branch** as its target
(`<feature-branch>`, reviewed against the base branch) — not the PR number, which makes it fetch
the PR into an extra local `pr-<number>` branch. Review only — no `--fix`, no `--comment`;
findings come back in-session. First separate the findings **outside the diff** — in code the
feature branch didn't change (`git diff --name-only origin/<base>...<feature-branch>`, plus the
changed hunks for a file that is in it). Then split the findings:
- **report** — out-of-diff faults that are real defects (not style or taste): not this Feature's
  to fix, so neither applied nor left as a note. File each with the `report-bug` skill —
  `--origin #<feature> --pr <pr>`, the finding as the description, no `--blocks`, never
  `--found-in` — headless-safe, it never asks when the run is headless. Its duplicate check
  keeps a resumed run from filing the same Bug twice. The Bugs never block this Feature: they're
  listed in the PR body under "Bugs reported". A `report-bug` failure → move the finding to
  **leave**, never block on it.
- **apply** — clear correctness bugs and mechanical cleanups with an obvious fix: dispatch one
  `task-executor` with them as its "sub-task body" (Approach: "apply these review fixes, nothing
  else"; footer `Refs #<feature>`), integrate it like any sub-task — but no issue comments, it's
  reported in the PR body instead.
- **leave** — anything needing judgement, and out-of-diff findings that aren't defects: listed
  in the PR body under "Review notes" for the human reviewer.

If the review or the fix run fails, note it in the PR body and still mark the PR ready — the
human review is the real gate.

---

## Resume

Re-running on a Feature at `Status: In progress`:
- feature branch from `origin` (integration worktree with `-B`, see above); open PR reused;
- closed sub-tasks are `done`;
- an open `afk` sub-task left at `Status: In progress` (crashed run) or with a previous blocked
  comment is `eligible` again with a fresh retry budget — a human may have fixed what blocked it;
- a `hitl` sub-task a human has closed is `done`, and its dependents become reachable;
- a `hitl` comment is not re-posted if the marker is already there.

---

## Cleanup

At the end of the run, whatever the outcome: remove every task worktree and temp branch of this
run, then the integration worktree (`git worktree remove`), then `git worktree prune`. The local
feature branch can stay; everything worth keeping is pushed. Remove the run directory
`.claude/worktrees/_run/` itself (not just its contents), then `.claude/worktrees/` if it's left
empty. Delete any local branch the final review created to read the PR (e.g. `pr-<number>`).
