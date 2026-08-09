---
schema_version: 2
id: "decision-use-flat-markdown-only"
type: "decision"
title: "Use Flat Markdown Only"
status: "superseded"
scope: "knowledge-os-core"
supersedes: []
superseded_by:
  - "decision-use-derived-graph"
related_wiki:
  - "synthesis-knowledge-os-architecture"
related_research:
  - "investigation-durable-knowledge-promotion"
created: "2026-08-09"
updated: "2026-08-09"
---

# Use Flat Markdown Only

## Decision

Use canonical Markdown without any generated relationship graph.

## Context

The core needs deterministic, inspectable storage and retrieval.

## Why

This was the smallest initial representation.

## Alternatives Considered

A rebuildable graph index; an external graph database.

## Trade-offs

Simple storage, but direct relationship inspection is slower.

## Consequences

Maintenance remains portable and generated layers stay disposable.

## Evidence

The architecture is connected to [[Wiki/Synthesis/knowledge-os-architecture]]; this is an engineering choice, not an externally proven universal fact.

## Revisit When

Explicit relationships become important for context assembly.

## Supersession History

Managed by `decision-supersede`; rationale above is preserved.

## Evidence Ledger
