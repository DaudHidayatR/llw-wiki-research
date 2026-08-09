# Command Reference

Invoke commands as `python3 scripts/wiki_tool.py <command>`.

### Required commands

#### Core

```text
doctor
build
lint
lint --strict-evidence
migrate --check
migrate --apply
```

`migrate --apply` creates an integrity-checked anonymous rollback snapshot, applies only an unambiguous safe plan, rebuilds derived artifacts, and runs deterministic lint. It **does not execute repository-controlled Python tests inside the privileged migration process**. After a successful apply, the caller must run:

```bash
python3 -m unittest discover -s tests
```

This separation is deliberate: tests remain a required acceptance check, but migration never grants untrusted repository code the authority to mutate the vault or external filesystem.

#### Source management

```text
source-scan
source-scan --update
source-scan --update --accept-covered
source-lint
source-delta
source-coverage
source-hash --check
source-hash --update-missing
source-hash --accept-change <path>
```

#### Search and graph

```text
search-catalog --query "text"
related --id "note-id"
graph-build
context-pack --query "text"
context-pack --query "text" --profile "default-research"
benchmark-retrieval
```

#### Research

```text
research-status
research-open
```

#### Memory

```text
memory-list
memory-list --type episodic-memory
memory-list --status active
```

#### Decisions

```text
decision-list
decision-list --status active
decision-supersede --old "decision-id" --new "decision-id"
```

#### Logs

```text
log --title "title" --details "details"
```

### `doctor`

Non-mutating checks should include:

- repository structure
- schema version
- Python version
- Git state when available
- canonical note counts
- duplicate IDs
- missing catalogs
- stale source hashes
- review-due notes from `review_after`
- unresolved migration requirement
- basic test availability

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
