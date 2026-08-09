---
name: llm-wiki-lint
description: "Use when operating schema-2 Knowledge OS. Run tests, source integrity, deterministic build, strict evidence lint, graph build, and public audit."
---
# llm-wiki-lint

## When To Use

Use after canonical changes, before meaningful commits, or to diagnose structural compliance. This skill executes the **Maintenance Gate** in `Schema/workflow-examples.md` and the checks in `Schema/lint-checklist.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

Run in this order:

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

Check failures against `Schema/lint-checklist.md`: schema/location/frontmatter, slugs and stable IDs, enum/date values, source counts/paths/hashes, related and relationship resolution, decision state/supersession, Evidence Ledger syntax/resolution, and generated-pack exclusion.

After ingest, also run:

```bash
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-coverage
```

After research, run `research-status` and `research-open`; after decisions, run `decision-list --status active`; periodically run `benchmark-retrieval`.

Completion criterion: all applicable commands exit successfully and failures are fixed at the canonical source rather than hidden in generated output.

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
