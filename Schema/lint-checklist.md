# Lint Checklist

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

### Lint behavior

`lint` must validate at minimum:

- schema version
- allowed location for each type
- constrained frontmatter grammar
- required fields
- filename slug validity
- unique stable IDs
- allowed types/status/confidence values
- `source_count == len(sources)`
- source links remain under `Raw/Sources/`
- linked Raw files exist
- `related` IDs resolve where required
- relationship target IDs resolve
- relationship grammar is valid
- `supersedes`/`superseded_by` are not self-referential
- active Decisions live under `Decisions/Active/`
- superseded Decisions live under `Decisions/Superseded/`
- Context Packs are never treated as canonical notes
- Evidence Ledger syntax and source resolution
- ISO date syntax for date fields when present (`YYYY-MM-DD`)

# Maintenance Gate

Before every meaningful commit:

```bash
python3 -m unittest discover -s tests
python3 scripts/wiki_tool.py doctor
python3 scripts/wiki_tool.py source-hash --check
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint --strict-evidence
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py graph-build
python3 scripts/audit_public.py
```

After source ingestion:

```bash
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-coverage
```

After research:

```bash
python3 scripts/wiki_tool.py research-status
python3 scripts/wiki_tool.py research-open
```

After decision changes:

```bash
python3 scripts/wiki_tool.py decision-list --status active
```

For complex LLM work:

```bash
python3 scripts/wiki_tool.py context-pack \
  --query "task question" \
  --profile "default-research"
```

Periodically:

```bash
python3 scripts/wiki_tool.py benchmark-retrieval
```
