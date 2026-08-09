# Deterministic Retrieval Model

This section is normative and must be copied into `Schema/retrieval-model.md`.

### Query normalization

Normalize query and candidate text as follows:

1. Unicode NFKC normalization.
2. Unicode `casefold()`.
3. Tokenize into consecutive Unicode alphanumeric characters using `str.isalnum()` semantics.
4. Remove tokens present in `Schema/search-stopwords.txt`.
5. Do not stem.
6. Deduplicate query tokens for scoring unless the rule explicitly counts occurrences.

`Schema/search-stopwords.txt` must be version-controlled and one normalized token per line.

### Stage A: direct seed scoring

For every candidate canonical note:

```text
exact normalized title equals full normalized query       +100
exact normalized alias equals full normalized query        +90

for each distinct query token present in title             +20
  cap title-token contribution at                          +60

for each distinct query token present in any alias          +15
  cap alias-token contribution at                          +45

for each distinct query token matching a topic              +10
  cap topic contribution at                                +30

for each distinct query token present anywhere in body       +5
  cap body contribution at                                 +25
```

No fuzzy matching or stemming is allowed in the core deterministic scorer.

Take the top **8** positive-scoring candidates as seeds.

Seed tie-break order:

1. score descending
2. profile type priority
3. `updated` descending, missing date last
4. canonical path ascending

### Default type priority

When no profile overrides it:

```text
synthesis
comparison
concept
topic
entity
project
```

### Stage B: one-hop expansion

Candidates connected to any Stage A seed may receive:

```text
explicit relationship to/from seed        +25
wikilink to/from seed                      +20
shared Raw source with seed                +10
active Research explicitly related        +15
active Decision explicitly related        +15
allowed Memory explicitly related         +10
```

Rules:

- graph expansion depth = 1
- expansion uses at most the top 8 seeds
- relationship bonuses are counted once per signal type per candidate, not once per edge
- Memory expansion is disabled unless the selected Context Profile sets `include_memory: true`
- Raw source items are not selected unless `include_raw` permits them

### Final selection

Sort using:

1. final score descending
2. profile type priority
3. `updated` descending
4. canonical path ascending

Return at most profile `max_items`, default 20.

The same repository state + query + profile + tool version must produce the same ranked Context Pack file list.

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

---

## Retrieval Benchmark Contract

Create and version:

```text
Schema/retrieval-benchmark.jsonl
```

One benchmark case per line:

```json
{"query":"agent sandboxing","profile":"default-research","expected_ids":["concept-agent-sandboxing"],"type":"concept"}
```

A serious repository should eventually contain at least **20 representative queries** before deciding that the core retrieval model is insufficient.

`benchmark-retrieval` must report at minimum:

- Recall@5
- Recall@10
- MRR@10
- zero-hit query count
- average selected Context Pack item count

Default quality target:

```text
Recall@10 >= 0.85
MRR@10    >= 0.65
zero-hit  <= 10%
```

These are default engineering gates, not universal truth. The repository may document different targets in `Schema/retrieval-model.md`.

### When to consider semantic/vector/graph retrieval

Do not add LightRAG, GraphRAG, a vector database, or an external graph service merely because the corpus is large.

First:

1. create representative benchmark cases
2. run baseline deterministic retrieval
3. inspect failure classes
4. tune note structure, aliases, relationships, synthesis, and context profiles
5. rerun benchmark

Consider an additional retrieval layer only when a documented bottleneck remains, such as:

- Recall@10 below the agreed target
- global questions consistently miss relevant synthesis
- synonym-heavy queries fail despite useful aliases
- relationship traversal needs more than bounded one-hop expansion
- latency or corpus scale exceeds the file-based implementation target

Any added retrieval layer remains derived and must resolve results back to canonical IDs/paths.
