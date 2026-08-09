---
schema_version: 2
id: "synthesis-knowledge-os-architecture"
type: "synthesis"
title: "Knowledge OS Architecture"
topics:
  - "knowledge-os"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/knowledge-os-starter-demo.md"
source_count: 1
related:
  - "topic-knowledge-operating-systems"
  - "concept-knowledge-separation"
relationships:
  - "synthesizes|concept-knowledge-separation"
  - "synthesizes|topic-knowledge-operating-systems"
supersedes: []
superseded_by: []
last_verified: "2026-08-09"
review_after: ""
created: 2026-08-09
updated: 2026-08-09
---

# Knowledge OS Architecture

## Synthesis Question

How should durable knowledge be structured for human and agent use?

## Executive Understanding

Evidence remains in Raw; focused reusable explanations live in Wiki; Research preserves discovery and unknowns; Memory preserves relevant context; Decisions preserve rationale; generated Context Packs select connected material. [C-001]

## Relationships

[[Wiki/Topics/knowledge-operating-systems]] scopes the domain and [[Wiki/Concepts/knowledge-separation]] defines its foundational boundary. The synthesis connects more than one knowledge note.

## Contradictions

None observed in the creator-owned demo source.

## Unknowns

Retrieval behavior beyond this small corpus remains to be measured.

## Evidence Ledger

- C-001 | confidence=high | The demonstrated architecture separates evidence, reusable knowledge, research, memory, decisions, and assembled context.
  - source: [[Raw/Sources/knowledge-os-starter-demo.md#Normalized Content]]
