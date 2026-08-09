---
name: knowledge-context
description: "Use when operating schema-2 Knowledge OS. Use deterministic profile ranking and one-hop expansion; packs contain exact excerpts and paths, not invented summaries."
---
# knowledge-context

## When To Use

Use for multi-note, cross-domain, relationship-sensitive, architecture, comparison, strategy, synthesis, or long-running agent work. This skill executes the **Canonical Context Pack Workflow** and `Schema/retrieval-model.md`.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Select a profile under `Context/Profiles/`; default to `default-research` when appropriate.
2. Search catalog and identify the query classification in the agent layer. The deterministic tool must leave classification `unclassified` if none is supplied.
3. Build the pack:

```bash
python3 scripts/wiki_tool.py context-pack --query "task question" --profile "default-research"
```

4. Verify Stage A direct seed scoring, top-eight positive seeds, bounded one-hop Stage B expansion, profile type priority, deterministic tie-breaks, `max_items`, Memory exclusion unless enabled, and Raw fallback policy against `Schema/retrieval-model.md`.
5. Confirm the pack contains metadata, selected canonical paths, explicit relationships, and only bounded exact excerpts. It must not contain generated semantic summaries.
6. Read the selected canonical files and reason in the agent layer. Treat the pack as generated context, never permanent Memory.
7. Periodically verify retrieval quality:

```bash
python3 scripts/wiki_tool.py benchmark-retrieval
```

Completion criterion: identical repository state, query, profile, and tool version produce the same ranked file list; all items obey profile boundaries and resolve to canonical notes.

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
