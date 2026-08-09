# Knowledge Model

The system must preserve this distinction:

```text
Raw sources     = evidence
Wiki            = current reusable understanding
Research        = investigation process
Memory          = contextual history
Decisions       = chosen actions + rationale
Context         = task-specific selected knowledge
Git             = history and audit trail
Quartz/Web      = human presentation
MCP/API         = machine interface
Derived indexes = disposable acceleration
```

---

## Core Principles

Agents and tooling must follow these principles.

### 1. Raw is evidence

- Preserve source meaning.
- Do not silently rewrite Raw content to support a preferred conclusion.
- Record capture metadata and content integrity hashes.
- A changed source must be re-evaluated before previously compiled coverage is trusted.

### 2. Wiki is current reusable knowledge

- Wiki notes should explain, connect, compare, and synthesize.
- Do not use Wiki as an activity log or source dump.
- Prefer several focused notes connected by relationships over one giant note.

### 3. Research records discovery

Research should preserve:

- question
- motivation
- existing knowledge
- hypothesis
- search strategy
- sources examined
- evidence for
- evidence against
- contradictions
- findings
- confidence
- unknowns
- follow-up questions
- conclusion
- proposed knowledge changes

### 4. Memory is contextual, not universal truth

Memory may record:

- what happened
- a confirmed preference
- a tentative observation

Memory must not automatically become factual Wiki knowledge.

### 5. Decisions preserve why

A decision should preserve:

- what was chosen
- context
- rationale
- alternatives
- trade-offs
- consequences
- supporting evidence
- revisit conditions
- supersession history

Never silently overwrite a meaningful historical decision.

### 6. Claims should resolve to evidence

Note-level `sources` show overall coverage.

Material factual claims should additionally resolve to exact evidence using the Evidence Ledger defined in this specification.

### 7. Derived indexes are disposable

The following must be rebuildable:

- `catalog.jsonl`
- `graph.jsonl`
- generated `index.md` files
- Context Packs
- retrieval benchmark reports
- embeddings
- vector indexes
- graph databases
- Quartz/site output

### 8. Search compiled knowledge first

Do not repeatedly scan broad Raw sources if the Wiki already contains sufficient understanding.

### 9. Prefer connected context over disconnected chunks

For complex reasoning, prefer:

```text
synthesis
  + concepts
  + relationships
  + relevant research
  + active decisions
  + relevant memory
  + evidence fallback
```

over arbitrary similarity-ranked fragments.

### 10. Preserve uncertainty and disagreement

- Do not force consensus.
- Record conflicting sources.
- Distinguish fact, interpretation, hypothesis, and decision.
- Keep unresolved questions visible.

### 11. Separate LLM judgment from deterministic validation

```text
Agents  = semantic judgment and synthesis
Scripts = structure, validation, indexing, scoring, integrity, migration
```

Deterministic scripts must not invent meaning.

### 12. Never invent citations

Unsupported claims must be:

- removed
- marked uncertain
- or researched

### 13. Human and AI views share one canonical corpus

Quartz, Obsidian, APIs, MCP servers, search engines, and graph databases are consumers of canonical Markdown—not replacement sources of truth.

### 14. Prefer promotion over dumping

Information moves upward only when it earns durability:

```text
working context
      |
      v
observation
      |
      v
important and reusable?
   /           \
 no             yes
 |               |
expire          memory candidate
                    |
                    v
             repeated/confirmed?
                /         \
              no           yes
              |             |
           episodic       durable memory
                              |
                      factual knowledge?
                         /         \
                       no           yes
                       |             |
                    memory        evidence review
                                      |
                                      v
                                     Wiki
```
