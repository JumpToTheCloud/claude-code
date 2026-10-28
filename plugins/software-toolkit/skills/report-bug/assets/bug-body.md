# Bug body template

The issue body. Keep every section; write "Unknown — <assumption>" rather than dropping one.
Never add AI attribution.

---

<!-- report-bug:origin=<n|none> -->
## Origin

Introduced by #<origin> (<Feature|Bug> — <title>), PR #<pr>. Found <in review of #<pr> | while
executing #<feature> | in release candidate `<rc>`>.

Or "None — found independently".

## Summary

<one or two sentences: what is wrong and what it affects>

## Steps to reproduce

1. <state / setup>
2. <action — command, request, input>
3. <observe>

## Expected behavior

<what should happen, with the source of truth if there is one — an AC of #<origin>, an Interface
Contract, a spec>

## Actual behavior

<what happens instead — error, output, wrong value>

## Affected files

- `path/to/file.ts` — `<function>` (line <n>): <why it's involved>

## Acceptance criteria

- [ ] **AC-1** — Given <conditions>, when <action>, then <fixed behavior>.
- [ ] **AC-2 (regression)** — Given the conditions in Steps to reproduce, when the regression
  test runs, then it fails before the fix and passes after it.

## Blocks

- #<issue> — <why it can't proceed without the fix>

Or "None".

## Mode: <AFK|HITL>

<one line: why the fix can be done unattended, or which human decision it needs>

## Assumptions

- <named assumption, only if any>
