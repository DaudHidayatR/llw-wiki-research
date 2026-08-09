---
name: llm-wiki-ingest
description: "Use when operating schema-2 Knowledge OS. Hash/scan Raw, search compiled knowledge, create focused evidence-backed notes, then build/lint/accept coverage."
---
# llm-wiki-ingest

## When To Use

Use when a normalized source is added or changed under `Raw/Sources/`. This skill executes the **Canonical Ingest Workflow** in `Schema/workflow-examples.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Put normalized Markdown under `Raw/Sources/`; optionally put an original binary under `Raw/Files/`.
2. Ensure source metadata is present. Populate or verify the body hash:

```bash
python3 scripts/wiki_tool.py source-hash --update-missing
python3 scripts/wiki_tool.py source-hash --check
```

3. Scan source state:

```bash
python3 scripts/wiki_tool.py source-scan --update
python3 scripts/wiki_tool.py source-delta
```

4. Search before broad Raw reading:

```bash
python3 scripts/wiki_tool.py search-catalog --query "source topic"
```

5. Open only relevant Wiki notes. Classify impact as an update, new focused note, comparison/synthesis input, contradiction, or research question.
6. Create/update focused Wiki notes. Add note-level `sources`, keep `source_count` exact, add `[C-NNN]` and valid Evidence Ledger entries where required, and add explicit relationships only when justified.
7. Preserve contradictions and uncertainty; create Research items for unresolved questions.
8. Validate before accepting coverage:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint --strict-evidence
python3 scripts/wiki_tool.py graph-build
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py source-coverage
```

9. Add a Log only when ingest meaningfully changed the Knowledge OS.

Completion criterion: the source hash is valid, compiled coverage is evidence-backed, strict lint passes, graph/catalogs rebuild, and coverage is accepted only after validation.

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
