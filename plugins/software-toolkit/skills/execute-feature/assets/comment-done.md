# Comment template — sub-task integrated

Posted after the sub-task's commits are pushed on the feature branch, right before closing it.
Fill from the worker's summary; drop a section only if it is genuinely empty (never drop
"Acceptance criteria").

---

<!-- execute-feature:done -->
✅ **Integrated into `<feature-branch>`** — <one-sentence summary of what now exists>.

### Commits
- `<short-sha>` <conventional subject>

### Files
- `path/to/file.ts` — <created | modified>: <what>

### Acceptance criteria
| AC | Verified by |
|---|---|
| AC-1 | `<test name>` (`path/to/file.spec.ts`) |

### Deviations from the description
- <what differs from the body (Files to touch, Phases, Pattern) and why — or "None">

### Findings
- <anything the next sub-tasks or the reviewer should know: surprises in the codebase, follow-ups,
  a bug fixed in #x's code (with commit) — or "None">

### Quality gate
`<test cmd>` ✅ · `<typecheck cmd>` ✅ · `<lint cmd>` ✅
