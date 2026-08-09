---
name: llm-wiki-maintain
description: "Use when operating schema-2 Knowledge OS. Keep generated catalogs rebuildable, review due/stale material, preserve IDs/history, and run the maintenance gate."
---
# llm-wiki-maintain

## When To Use

Use for routine Knowledge OS health, review-due notes, source changes, catalog rebuilding, migration checks, or pre-publication maintenance. Follow the canonical workflows in `Schema/workflow-examples.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Diagnose without mutation:

```bash
python3 scripts/wiki_tool.py doctor
python3 scripts/wiki_tool.py migrate --check
python3 scripts/wiki_tool.py source-hash --check
python3 scripts/wiki_tool.py source-delta
```

2. Review stale source hashes and notes past `review_after`. A review-due note is not automatically false; changed Raw evidence is not fresh until explicitly reviewed.
3. Preserve stable IDs across title, alias, and allowed path changes. Preserve Research, Memory, and Decision history rather than rewriting it away.
4. Rebuild disposable artifacts from canonical Markdown:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py graph-build
```

5. Inspect open work and active state:

```bash
python3 scripts/wiki_tool.py source-coverage
python3 scripts/wiki_tool.py research-status
python3 scripts/wiki_tool.py research-open
python3 scripts/wiki_tool.py memory-list
python3 scripts/wiki_tool.py decision-list --status active
```

6. Publish only through the one-way canonical publishing workflow:

```bash
python3 scripts/export_public.py
python3 scripts/audit_public.py
```

7. Run the full Maintenance Gate.

Completion criterion: doctor reports no unresolved migration, source integrity is explicit, canonical IDs/history remain intact, derived artifacts rebuild deterministically, and public audit passes.

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
