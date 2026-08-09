# Context Model

#### `Context/Profiles/`

Canonical rules for context assembly.

#### `Context/Packs/`

Generated task-specific context bundles.

Ignored by Git by default.

### Context Pack content

The deterministic builder may include:

- metadata
- selected note paths
- explicit relationships
- bounded exact excerpts

It must not generate semantic summaries.

Recommended generated structure:

```markdown
# Context Pack

## Query

## Query Classification

## Ranking Metadata

## Primary Synthesis

## Core Knowledge

## Related Knowledge

## Active Research

## Relevant Decisions

## Relevant Memory

## Evidence Fallback

## Relationship Expansion

## Open Questions

## Files To Read
```

`Query Classification` may be supplied by the caller/agent. If omitted, the deterministic tool must leave it `unclassified` rather than infer semantics.

# Canonical Context Pack Workflow

Use a Context Pack when:

- more than one Wiki note is needed
- the question spans domains
- relationships matter
- Research or Decisions affect the answer
- the user asks for architecture/comparison/strategy/synthesis
- a long-running agent task needs stable selected context

Selection order should generally favor:

```text
Synthesis
  -> Comparison
  -> Core Concepts
  -> Entities/Projects
  -> Research
  -> Decisions
  -> Relevant Memory
  -> Raw Evidence
```

But final ranking must follow the deterministic Retrieval Model and selected profile.

Context Packs:

- are generated
- are not permanent Memory
- must not contain invented semantic summaries
- should point to canonical full notes
- may contain bounded exact excerpts
