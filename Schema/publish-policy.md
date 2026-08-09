# Publish Policy

# Step 09: Human Web Publishing Exercise

The Knowledge OS must remain usable without a web server.

Publishing is one-way:

```text
canonical Markdown
      |
      v
public export
      |
      v
Quartz / web renderer
```

Default publish allow-list:

```text
Wiki/
Research/
Decisions/
Welcome.md
```

Default deny-list:

```text
Raw/
Memory/
Context/
Schema/
.agents/
scripts/
tests/
```

Create:

```text
scripts/export_public.py
scripts/audit_public.py
```

Run:

```bash
python3 scripts/export_public.py
python3 scripts/audit_public.py
```

Output:

```text
site-output/
```

Quartz is optional.

If used:

- Quartz is a renderer, not a knowledge engine
- preserve wikilinks/backlinks/graph navigation
- do not edit generated site output as canonical knowledge
- do not require Quartz for agent access

# Canonical Human Publishing Workflow

1. Rebuild canonical indexes.
2. Export allow-listed content:

```bash
python3 scripts/export_public.py
```

3. Audit:

```bash
python3 scripts/audit_public.py
```

4. Render `site-output/` with Quartz or another Markdown-native frontend.
5. Keep publication one-way.
6. Never treat generated site output as canonical.

# Public Audit Contract

`audit_public.py` should fail on obvious:

- secrets
- API tokens
- private keys
- `.env` values
- machine-local absolute paths
- plugin/cache state
- accidental binary content
- private Memory selected for publishing
- Context Packs selected for publishing
- deny-listed paths present in `site-output/`

The audit is a safety net, not a complete secret-scanning product.
