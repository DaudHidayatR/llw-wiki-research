# Evidence Model
Every compiled note has note-level `sources` and exact `source_count`. Material factual claims in comparisons, syntheses, findings, investigation conclusions, and evidence-dependent decisions use `[C-NNN]` and an Evidence Ledger.

```text
- C-001 | confidence=low|medium|high|mixed | claim text
  - source: [[Raw/Sources/name.md#Optional Heading]]
```
Claims are local, unique, sequential identifiers. Ledger sources must exist under Raw/Sources; deterministic anchors must resolve. Source bodies are LF-normalized and SHA-256 hashed in `ContentHash`; changes require explicit acceptance and invalidate coverage.
