---
name: knowledge-decision
description: "Use when operating schema-2 Knowledge OS. Record rationale/alternatives/trade-offs/revisit conditions and supersede deterministically without erasing history."
---
# knowledge-decision

## When To Use

Use when a meaningful choice is made or replaced. This skill executes the **Canonical Decision Workflow** in `Schema/workflow-examples.md` and follows `Schema/decision-model.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Search active Decisions for the same scope:

```bash
python3 scripts/wiki_tool.py decision-list --status active
```

2. Create/update the new Decision with decision, context, rationale, alternatives, trade-offs, consequences, evidence, and revisit condition.
3. Use claim-level evidence for material external factual justification; link related Wiki and Research.
4. When replacing an old Decision, create the new active Decision first, then run:

```bash
python3 scripts/wiki_tool.py decision-supersede --old "old-decision-id" --new "new-decision-id"
```

5. Verify old status is `superseded`, old file is under `Decisions/Superseded/`, links are bidirectional, old body/rationale remain intact, and no cycle exists.
6. Rebuild catalogs/graph and list active decisions.

Completion criterion: the current choice is active, history is preserved, deterministic supersession linked both records, and no rationale was invented or erased.

## Maintenance Verification

Before a meaningful commit, run the Maintenance Gate:

```bash
python3 -m unittest discover -s tests
python3 scripts/wiki_tool.py doctor
python3 scripts/wiki_tool.py source-hash --check
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint --strict-evidence
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py graph-build
python3 scripts/audit_public.py
```

Completion criterion: every command exits successfully; generated canonical indexes are deterministic; no source, evidence, relationship, publication, or migration issue remains unreported.

## Pitfalls

- Never invent citations, semantic relationships, summaries in deterministic output, or unsupported certainty.
- Never replace the canonical workflow with a skill-specific algorithm.
- Never make generated output or an external retrieval store canonical.
