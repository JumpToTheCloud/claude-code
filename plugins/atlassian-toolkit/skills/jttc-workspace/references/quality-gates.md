# Quality gates: Definition of Ready and Definition of Done

The criteria are **not kept here** any more. The source of truth is in the skill that applies
them, so there is a single copy:

| What | File |
|---|---|
| Definition of Ready: what must be true (entry, Gate 1, Gate 2, bug and task variants, sub-task checklist). The team's agreement, mirrored to Confluence | `skills/jira-transition-issue/references/definition-of-ready.md` |
| Definition of Done: what must be true (universal, Story, Bug, Epic, component types, special cases). The team's agreement, mirrored to Confluence | `skills/jira-transition-issue/references/definition-of-done.md` |
| How `jira-transition-issue` applies them in Jira: which move runs which gate, how each criterion is checked and encoded. Not mirrored | `skills/jira-transition-issue/references/how-gates-are-applied.md` |

The Confluence pages `Definition of Ready` (`223281170`) and `Definition of Done` (`223281157`),
under Platform → Process, are **mirrors for people to read**. They are generated from those
files by `confluence-sync-templates` (phase 5) and must not be edited by hand. Until that skill
exists they still hold the original text: if the two ever differ, the files in the skill win.

Rules that always apply:
- Every criterion is a yes/no check. `N/A` needs a one-line reason in the Jira item.
- A failed gate leaves the item where it is. It never moves forward with a promise to fix it
  later.
- Move issues with the `jira-transition-issue` skill, which applies the gates.
