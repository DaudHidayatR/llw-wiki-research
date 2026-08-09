# Relationship Contract

Canonical explicit relationships use a flat string list:

```yaml
relationships:
  - "requires|concept-container-isolation"
  - "contrasts-with|concept-host-execution"
  - "implemented-by|entity-gvisor"
```

Grammar:

```text
<relation>|<target-id>
```

Allowed relation names use lowercase kebab-case.

`graph-build` may additionally derive:

- `links-to` from wikilinks
- `supported-by` from `sources`
- `shares-source-with` as a derived edge only when explicitly requested in output mode

`graph-build` must never infer hidden semantic relations.

---
