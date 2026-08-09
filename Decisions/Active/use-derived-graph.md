---
schema_version: 2
id: "decision-use-derived-graph"
type: "decision"
title: "Use A Derived Explicit Relationship Graph"
status: "active"
scope: "knowledge-os-core"
supersedes:
  - "decision-use-flat-markdown-only"
superseded_by: []
related_wiki:
  - "synthesis-knowledge-os-architecture"
related_research:
  - "investigation-durable-knowledge-promotion"
created: "2026-08-09"
updated: "2026-08-09"
---

# Use A Derived Explicit Relationship Graph

## Decision

Keep Markdown canonical and generate `Wiki/graph.jsonl` from explicit metadata and wikilinks.

## Context

The core needs deterministic, inspectable storage and retrieval.

## Why

It improves deterministic relationship traversal without creating a second source of truth.

## Alternatives Considered

Flat Markdown only; external graph database.

## Trade-offs

Adds one rebuild step while preserving portability and auditability.

## Consequences

Maintenance remains portable and generated layers stay disposable.

## Evidence

The architecture is connected to [[Wiki/Synthesis/knowledge-os-architecture]]; this is an engineering choice, not an externally proven universal fact.

## Revisit When

Benchmarks show bounded file graph traversal is inadequate.

## Supersession History

Managed by `decision-supersede`; rationale above is preserved.

## Evidence Ledger
