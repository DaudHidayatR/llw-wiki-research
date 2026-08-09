# Agent Operating Rules

Markdown with constrained YAML frontmatter and wikilinks is canonical. Catalogs, graphs, Context Packs, embeddings, external databases, and site output are derived and rebuildable.

## Required Rules

- Treat `Raw/Sources/` as evidence, not compiled knowledge.
- Write reusable knowledge under `Wiki/`.
- Preserve investigation history under `Research/`.
- Store contextual history under `Memory/`, not `Wiki/`.
- Record meaningful choices under `Decisions/`.
- Search `Wiki/catalog.jsonl` before broad Raw reads.
- Search relevant Research and Decisions before duplicating investigation work.
- Use Memory only when it materially changes the current task.
- Build a Context Pack for complex multi-note questions.
- Keep compiled notes linked to Raw sources unless they are explicit navigation/index notes.
- Use the Evidence Ledger for material claims where required.
- Never invent citations or unsupported claims.
- Preserve competing views and unresolved contradictions.
- Prefer focused notes over giant monoliths.
- Supersede stale decisions rather than deleting history.
- Do not convert temporary task context into durable Memory automatically.
- Treat generated catalogs, graph files, Context Packs, embeddings, and site output as rebuildable.
- Never treat an external vector/graph database as canonical.
- Run deterministic tests plus the maintenance gate before meaningful commits.
- Do not enable MCP/API mutation without the security contract.

## Operating Order

1. Read the relevant contract under `Schema/`.
2. Search compiled Wiki knowledge first; inspect relevant Research and active Decisions before doing duplicate work.
3. Use Memory only when task-relevant, and never as external factual evidence.
4. For complex work, build a deterministic Context Pack using the selected profile.
5. Open Raw only for evidence verification, insufficient compiled knowledge, conflicts, or exact wording/figures.
6. Make semantic judgments in agent-authored canonical Markdown; deterministic scripts must not invent meaning.
7. Preserve uncertainty, contradictions, unresolved questions, stable IDs, provenance, and history.
8. Execute the single canonical workflow in `Schema/workflow-examples.md`; skills under `.agents/skills/` are actionable entry points to those workflows, not alternate algorithms.
9. Run the applicable workflow-specific checks and the Maintenance Gate.

## Evidence And Source Integrity

Every compiled note uses note-level `sources` and an exact `source_count`. Material factual conclusions in comparisons, syntheses, findings, investigation conclusions, and evidence-dependent decisions require local `[C-NNN]` references and an `## Evidence Ledger` whose sources resolve under `Raw/Sources/`.

Raw source `ContentHash` is the SHA-256 of the body after frontmatter after newline normalization. Never silently accept changed content. Use `source-hash --accept-change <path>` only deliberately; it resets `Processed`, clears accepted coverage, and requires review of affected Wiki notes.

## Memory Promotion Summary

```text
temporary task state
    -> working context

meaningful event that may matter later
    -> episodic memory

stable user/system preference confirmed or repeatedly observed
    -> preference memory

tentative pattern
    -> observation memory

chosen option with rationale
    -> Decision

supported reusable fact/concept
    -> Wiki
```

One-off details do not become durable Memory by default. A one-off observation is not a preference. Factual Memory must pass evidence review before Wiki promotion. Decisions belong in `Decisions/`.

## Maintenance Gate

Before every meaningful commit, run:

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

Then run the applicable post-work checks documented in `Schema/workflow-examples.md`: source acceptance/coverage after ingest, research status/open after research, active decision listing after decision changes, deterministic Context Pack generation for complex work, and retrieval benchmarking periodically.

## Publishing And MCP/API

Publishing is one-way from canonical Markdown through the allow-listed public export to a renderer. Run `python3 scripts/export_public.py` and `python3 scripts/audit_public.py`; never edit `site-output/` as canonical knowledge.

MCP/API is optional. If enabled, follow `Schema/mcp-security-model.md`: localhost by default, authenticated remote access, narrow capability scopes, private Memory scope, proposal-oriented mutation, no unrestricted filesystem mutation, operational limits, and auditable changes.
