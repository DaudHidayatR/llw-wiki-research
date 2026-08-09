---
name: llm-wiki-query
description: "Use when operating schema-2 Knowledge OS. Search catalog first, expand explicit relations, include relevant research/decisions, and build context for complex queries."
---
# llm-wiki-query

## When To Use

Use when answering from the Knowledge OS. This skill executes the **Canonical Query Workflow** and, for complex questions, the **Canonical Context Pack Workflow** in `Schema/workflow-examples.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Start with `Wiki/index.md` and `Wiki/catalog.jsonl`.
2. Classify the request in the agent layer as fact, concept, relationship, comparison, decision, research, or global synthesis.
3. Search:

```bash
python3 scripts/wiki_tool.py search-catalog --query "user topic"
```

4. Open the smallest useful set of Wiki notes and expand explicit/direct relationships:

```bash
python3 scripts/wiki_tool.py related --id "note-id"
```

5. Inspect relevant Research and active Decisions. Use Memory only when contextual personalization materially changes the answer.
6. For multi-note, cross-domain, relationship-sensitive, architecture, comparison, strategy, synthesis, or long-running work, build a Context Pack:

```bash
python3 scripts/wiki_tool.py context-pack --query "task question" --profile "default-research"
```

7. Open Raw only for evidence-level verification, insufficient compiled knowledge, conflicts, or exact figures/wording.
8. Answer from organized context, preserve uncertainty, and cite compiled knowledge and Raw evidence appropriately.
9. If durable knowledge emerges, record Research/Finding where appropriate, validate evidence, and promote through the canonical Research workflow. Do not mutate Wiki solely because an LLM answer sounds plausible.

Completion criterion: the answer comes from the smallest connected context, relevant provenance resolves, uncertainty remains visible, and no generated Context Pack is mistaken for canonical Memory.

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
