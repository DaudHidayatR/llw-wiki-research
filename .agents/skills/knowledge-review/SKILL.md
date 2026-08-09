---
name: knowledge-review
description: "Use when operating schema-2 Knowledge OS. Check provenance, uncertainty, relationships, duplication, promotion boundaries, and deterministic maintenance gates."
---
# knowledge-review

## When To Use

Use to review proposed canonical changes before acceptance or publication. Apply the contracts in `Schema/` and the existing canonical workflow that produced the change; this skill defines no competing workflow.

## Prerequisites

- Read `AGENTS.md` and the named `Schema/` contracts before mutation.
- Run commands from the repository root with Python 3.
- Treat canonical Markdown as source of truth and generated artifacts as disposable.

## Procedure

1. Classify each changed artifact as canonical or derived. Reject edits that make catalogs, graphs, packs, indexes, databases, or site output authoritative.
2. Check stable IDs, valid locations/slugs/frontmatter, focused scope, and repository-wide uniqueness.
3. Check note-level sources and exact `source_count`; verify each material `[C-NNN]` resolves exactly once to valid Raw evidence and allowed confidence.
4. Check source integrity. Changed source bodies require explicit acceptance and coverage review; never silently refresh hashes.
5. Check explicit relationship grammar/targets and reject inferred hidden semantics.
6. Check uncertainty, contradictions, competing views, open questions, and conclusions bounded by evidence.
7. Check promotion boundaries: Research is not fact until reviewed, Memory is not evidence, one-offs are not preferences, Decisions are not Memory, and Context Packs are generated.
8. Check Decision supersession preserves bodies/history, bidirectional links, correct locations, and acyclicity.
9. Check public export against `Schema/publish-policy.md` and optional MCP/API work against `Schema/mcp-security-model.md`.
10. Run the Maintenance Gate and applicable post-work checks.

Completion criterion: every changed canonical claim and relationship is traceable, history and uncertainty are preserved, promotion boundaries hold, generated/public/security boundaries hold, and all deterministic gates pass.

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
