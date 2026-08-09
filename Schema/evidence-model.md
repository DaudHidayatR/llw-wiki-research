# Evidence And Claim Provenance Contract

This section is normative and must be copied into `Schema/evidence-model.md`.

### Two provenance levels

#### Note-level provenance

Every compiled knowledge note keeps:

```yaml
sources: []
source_count: 0
```

This indicates broad note coverage.

#### Claim-level provenance

Material factual claims use local claim IDs and an Evidence Ledger.

In prose:

```markdown
gVisor intercepts application system calls before they reach the host kernel. [C-001]
```

At the end of the note:

```markdown
## Evidence Ledger

- C-001 | confidence=high | gVisor intercepts application system calls before they reach the host kernel.
  - source: [[Raw/Sources/gvisor-architecture.md#Userspace-kernel]]
```

Claim IDs are local to one note and use:

```text
C-001
C-002
C-003
...
```

### Evidence Ledger grammar

Claim line:

```text
- C-NNN | confidence=<low|medium|high|mixed> | <claim text>
```

Evidence line:

```text
  - source: [[Raw/Sources/<path>.md]]
```

or with anchor:

```text
  - source: [[Raw/Sources/<path>.md#Heading]]
```

### Required claim-level evidence

Claim-level evidence is required for material factual conclusions in:

- `comparison`
- `synthesis`
- Research `finding`
- Research `investigation` conclusions
- Decision evidence when external factual claims materially justify the choice

It is strongly recommended for:

- `concept`
- `entity`
- `topic`
- `project`

It is not required for:

- navigation/index notes
- logs
- purely personal Memory

### Deterministic evidence lint

`lint` must verify where Evidence Ledgers exist:

- claim references `[C-NNN]` resolve to exactly one ledger entry
- duplicate claim IDs fail
- ledger confidence uses an allowed value
- every evidence `source:` points under `Raw/Sources/`
- referenced source files exist
- referenced anchors are checked when the source heading can be deterministically resolved
- no ledger entry references a missing source

`lint --strict-evidence` must additionally fail required note types that contain an `## Evidence Ledger` section with zero valid claims.

Scripts do not attempt to semantically detect every unsupported sentence. Agents remain responsible for marking material claims.

---

## Source Integrity Contract

Each Raw source contains:

```yaml
ContentHash: "sha256:<hex>"
```

The hash is computed from the source note body **after the closing frontmatter delimiter**, using:

1. UTF-8 decoding
2. CRLF/CR normalization to LF
3. preserve all other body characters exactly
4. UTF-8 encoding
5. SHA-256

Frontmatter changes do not change `ContentHash`.

### Source change behavior

If current body hash differs from `ContentHash`:

- `source-lint` fails
- `doctor` reports the source as changed/stale
- existing coverage must not be considered fresh

The tool must support:

```text
source-hash --check
source-hash --update-missing
source-hash --accept-change <path>
```

`--update-missing` may populate only empty/missing hashes.

`--accept-change` must:

- write the new hash
- set `Processed: false`
- clear accepted coverage for the changed source in the source manifest
- report Wiki notes that referenced the source and may require review

It must never silently accept changed source content.
