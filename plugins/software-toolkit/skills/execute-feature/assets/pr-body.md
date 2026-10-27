# PR body template

Rewritten in full after every integration and at the end of the run. Never add a "Generated
with Claude Code" line, a `Co-Authored-By` trailer or any other AI attribution to it.

---

Implements #<feature> — <Feature title>.

Closes #<feature>

> ⚠️ Merge keeping the commits (rebase or merge commit), **not squash**: every commit is a
> Conventional Commit tied to its sub-task (`Refs #<sub-task>`), which the changelog relies on.
> `Closes` only fires on the default branch — merging into `<base>` leaves #<feature> open until
> it is closed by the board automation or by hand.

## Sub-tasks
- [x] #7 Implement WebhookSignatureVerifier
- [ ] #9 Implement GithubWebhookRequestHandler — ⏳ waiting on #8
- [ ] #12 Provision GitHub App — 🙋 human needed
- [ ] #13 Create Secrets Store — ⛔ blocked: <one line>

## Review notes
<final review: fixes applied (commit), and judgement calls left for the reviewer — omit until the
final review ran>

## Warnings
<only if any: base branch `next` was created by this run; no `Base branch` declared in AGENTS.md
(using `next`); a `Status` option missing on the board; no automated quality gate found>
