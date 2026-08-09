---
name: knowledge-synthesis
description: "Use when operating schema-2 Knowledge OS. Connect multiple focused notes and sources; preserve contradictions; ledger every material conclusion."
---
# knowledge-synthesis

## When To Use

Use when multiple concepts, sources, or investigations must be connected into reusable understanding. Follow the **Canonical Complex Concept**, **Research**, **Query**, and **Context Pack** workflows; do not create a separate synthesis algorithm.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Search Wiki and locate or create the core Concept/Synthesis note; inspect relevant Research and Decisions.
2. Identify parent Topics, prerequisite Concepts, relevant Entities/technologies, Comparisons, Synthesis notes, active Research, and relevant Decisions.
3. Build the smallest connected Context Pack needed to explain the question.
4. Prefer mental models and explicit relationships over flat summaries. Preserve claim/fact -> concept -> topic -> comparison -> synthesis -> domain-understanding layers.
5. Connect multiple focused notes and sources; preserve competing models, contradictions, trade-offs, implications, and unknowns.
6. Verify material conclusions against Raw evidence when necessary. Every material synthesis conclusion requires `[C-NNN]` and a valid Evidence Ledger entry.
7. Add explicit semantic relationships only when justified; deterministic graph tooling must not infer them.
8. Rebuild and validate:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint --strict-evidence
python3 scripts/wiki_tool.py graph-build
```

Completion criterion: the synthesis connects more than one knowledge item, all material claims resolve to evidence, contradictions remain visible, and the overall model—not a source dump—is reusable.

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
