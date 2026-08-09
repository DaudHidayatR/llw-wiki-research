---
schema_version: 2
id: "investigation-durable-knowledge-promotion"
type: "investigation"
title: "Durable Knowledge Promotion Investigation"
status: "active"
question: "What information should be promoted from research into durable Wiki knowledge?"
confidence: "medium"
sources:
  - "Raw/Sources/knowledge-os-starter-demo.md"
related_wiki:
  - "concept-knowledge-separation"
  - "synthesis-knowledge-os-architecture"
related_decisions: []
created: 2026-08-09
updated: 2026-08-09
---

# Durable Knowledge Promotion Investigation

## Research Question

What information should be promoted from research into durable Wiki knowledge?

## Motivation

Durability should be earned without discarding useful uncertainty or investigation history.

## Existing Knowledge

The compiled Wiki separates evidence, understanding, research, memory, and decisions.

## Current Hypothesis

Promote only reusable conclusions supported by inspectable evidence; leave contextual or unresolved material in Research or Memory.

## Search Strategy

Inspect the creator-owned source and compare its stated layer responsibilities with existing [[Wiki/Concepts/knowledge-separation]].

## Sources Examined

- [[Raw/Sources/knowledge-os-starter-demo.md]]

## Evidence For

The source explicitly assigns reusable understanding to Wiki while assigning discovery history and contextual history to separate layers. [C-001]

## Evidence Against

One short creator-owned source does not establish domain-independent thresholds for corroboration.

## Contradictions

No direct contradiction was found. The evidence is limited rather than conflicting.

## Findings

Layer assignment and support are separate tests: a statement belongs in Wiki only when reusable and supported; investigation-path details remain Research.

## Confidence

Medium, because the architecture is explicit but the corpus is intentionally small.

## Unknowns

- Appropriate corroboration thresholds in sparse domains.
- How review cadence should vary with source volatility.

## Follow-up Questions

What evidence threshold should apply to high-risk factual domains?

## Conclusion

Promote supported reusable understanding, preserve the supporting Raw path, and keep unresolved qualifications visible; do not promote the untested corroboration threshold.

## Proposed Wiki Updates

The supported layer boundary is already represented by [[Wiki/Concepts/knowledge-separation]].

## Proposed Decisions

None; this investigation does not choose an implementation policy beyond the established schema.

## Evidence Ledger

- C-001 | confidence=high | The demo source assigns reusable understanding, research history, and contextual memory to distinct layers.
  - source: [[Raw/Sources/knowledge-os-starter-demo.md#Normalized Content]]
