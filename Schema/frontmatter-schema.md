# Frontmatter Schema

### Canonical frontmatter schema version

Every canonical note created by this specification should contain:

```yaml
schema_version: 2
```

Generated indexes and Context Packs do not require canonical note schema frontmatter.

# Frontmatter Parser Contract

To keep standard-library tooling deterministic, canonical frontmatter uses a constrained YAML subset only:

Supported:

- string scalar
- integer scalar
- boolean scalar
- empty/null string
- flat list of strings

Do not require arbitrary nested YAML maps in the core schema.

Complex structures should use:

- flat encoded strings
- body sections
- JSONL derived artifacts

This allows `wiki_tool.py` to implement a small deterministic parser without depending on PyYAML.

### Common canonical frontmatter

All canonical notes should begin with:

```yaml
---
schema_version: 2
id: ""
type: ""
title: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Type-specific templates extend this subset.

### Source Note Template

```yaml
---
schema_version: 2
id: "source-example"
type: "source"
title: ""
Author: ""
Reference: ""
SourceType: "markdown"
ContentType:
  - "markdown"
Published: ""
Captured: YYYY-MM-DD
Created: YYYY-MM-DD
ContentHash: ""
Processed: false
tags:
  - "source"
---
```

Allowed `SourceType` values:

```text
markdown
web
pdf
book
video
audio
code
repository
documentation
meeting
dataset
note
other
```

Recommended body:

```markdown
# Source Title

## Source Metadata

## Normalized Content

## Figures Or Tables

## References

## Capture Notes
```

Interpretation should not be inserted into `Normalized Content` unless clearly separated from source material.

### Compiled Wiki Frontmatter

```yaml
---
schema_version: 2
id: "concept-example"
type: "concept"
title: "Example"
topics: []
aliases: []
status: "seed"
confidence: "medium"
sources: []
source_count: 0
related: []
relationships: []
supersedes: []
superseded_by: []
last_verified: ""
review_after: ""
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Allowed Wiki types:

```text
topic
concept
entity
project
comparison
synthesis
log
```

Allowed statuses:

```text
seed
active
mature
needs-review
deprecated
```

Allowed confidence:

```text
low
medium
high
mixed
```

`last_verified` and `review_after` are optional ISO dates.

`doctor` should report notes past `review_after` as review-due, not as automatically false.
