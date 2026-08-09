# Knowledge OS

This repository is a durable, human-readable, AI-friendly Knowledge OS. Markdown with constrained YAML frontmatter and wikilinks is canonical. Catalogs, graph files, Context Packs, retrieval reports, embeddings, external indexes, and web output are derived and rebuildable.

## Layers

- **Raw** is normalized source evidence. Original binaries may live in `Raw/Files/`.
- **Wiki** is current reusable understanding: topics, concepts, entities, projects, comparisons, syntheses, and meaningful change logs.
- **Research** preserves investigation paths, hypotheses, search strategy, evidence for and against, contradictions, findings, confidence, unknowns, and conclusions.
- **Memory** stores relevant contextual history, confirmed preferences, and tentative observations; it is not universal truth or external evidence.
- **Decisions** preserve choices, rationale, alternatives, trade-offs, consequences, revisit conditions, and supersession history.
- **Context** defines deterministic selection profiles and generated task-specific Context Packs.
- **Git** preserves history and an audit trail.
- **Web/MCP/API** consume canonical Markdown; they never replace it.

## Start Here

Humans should start at [Wiki/index.md](Wiki/index.md), follow links into focused notes, and use the source and Evidence Ledger links when exact support matters.

Agents should first read [AGENTS.md](AGENTS.md), then search `Wiki/catalog.jsonl` before opening broad Raw sources. For complex questions, generate a Context Pack using a profile under `Context/Profiles/`. The authoritative in-repository contracts are under `Schema/`; the canonical operating workflows are in `Schema/workflow-examples.md`.

The system is usable directly as Markdown and does not require Quartz, a web server, embeddings, a vector database, or an external graph service.
