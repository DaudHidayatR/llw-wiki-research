---
name: knowledge-memory
description: "Use when operating schema-2 Knowledge OS. Promote only meaningful context; confirm preferences; keep observations tentative; never use Memory as factual evidence."
---
# knowledge-memory

## When To Use

Use when contextual information may matter beyond the current task. This skill executes the **Canonical Memory Workflow** and promotion policy in `Schema/memory-model.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Decide first whether the information is temporary working context. If so, do not create durable Memory.
2. If meaningful and reusable, classify it as an episodic event, confirmed/repeated preference, or tentative observation.
3. Do not create durable Memory for trivial information and do not promote one observation into a preference.
4. Store meaningful choices with rationale in `Decisions/`, not Memory.
5. Never use Memory as external factual evidence. Validate factual content against Raw evidence before promotion into Wiki.
6. Mark stale/superseded Memory rather than silently rewriting useful history.
7. Review the result:

```bash
python3 scripts/wiki_tool.py memory-list
python3 scripts/wiki_tool.py memory-list --type episodic-memory
python3 scripts/wiki_tool.py memory-list --status active
```

Completion criterion: each durable Memory has the correct type and status; preferences are confirmed/repeated, observations remain tentative or expire, and no factual Wiki promotion bypasses evidence review.

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
