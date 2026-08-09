---
name: knowledge-research
description: "Use when operating schema-2 Knowledge OS. Preserve question, strategy, opposing evidence, unknowns, bounded conclusion, and evidence-backed promotion."
---
# knowledge-research

## When To Use

Use when existing knowledge cannot adequately support a question. This skill executes the **Canonical Research Workflow** in `Schema/workflow-examples.md` and follows `Schema/research-model.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Search Wiki, existing Research, and relevant active Decisions. Build a Context Pack when the question spans multiple notes.
2. State what is already known; create/update a Research Question or Investigation.
3. Define the question, motivation, current hypothesis, and search strategy.
4. Add sources and record evidence for, evidence against, contradictions, findings, confidence, unknowns, and follow-up questions.
5. Use claim-level evidence for material factual findings and conclusions.
6. Write a conclusion no stronger than the evidence permits.
7. Promote only supported reusable knowledge into Wiki. Keep unresolved questions under `Research/Open/`.
8. Link Research to affected Wiki and Decisions, then rebuild catalogs and graph:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py graph-build
python3 scripts/wiki_tool.py research-status
python3 scripts/wiki_tool.py research-open
```

Completion criterion: the visible chain is question -> existing knowledge -> evidence -> finding -> supported Wiki update or unresolved question; opposing evidence and unknowns are preserved.

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
