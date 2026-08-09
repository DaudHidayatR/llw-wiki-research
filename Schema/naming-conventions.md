# Naming And Stable ID Contract

This section is normative and must be copied into `Schema/naming-conventions.md`.

### Filename slugs

Generated canonical note filenames use lowercase ASCII kebab-case.

Slug algorithm:

1. Unicode normalize with NFKD.
2. Remove combining marks.
3. Encode to ASCII, dropping unsupported characters.
4. Lowercase.
5. Replace every run of non `[a-z0-9]` characters with `-`.
6. Collapse repeated `-`.
7. Trim leading/trailing `-`.

Example:

```text
"Agent Sandboxing: gVisor vs. Kata"
-> agent-sandboxing-gvisor-vs-kata
```

If normalization produces an empty or misleading slug, the agent/human must supply an explicit short ASCII slug while preserving the original title in frontmatter.

### File names

Default:

```text
<slug>.md
```

Logs may use:

```text
YYYY-MM-DD-<slug>.md
```

Do not include the note type in the filename unless needed to disambiguate a legacy repository.

### Stable IDs

On creation, generate:

```text
<type>-<slug>
```

Example:

```text
concept-agent-sandboxing
```

Once assigned, an ID **must not change automatically** when:

- title changes
- aliases change
- file moves within the allowed folder for its type

If `<type>-<slug>` already exists, append:

```text
-<hash6>
```

where `hash6` is the first six lowercase hex characters of:

```text
SHA256(type + "\n" + initial_relative_path)
```

Example:

```text
concept-agent-sandboxing-4fa82b
```

### ID validation

IDs must:

- be unique repository-wide
- use lowercase `[a-z0-9-]`
- start with the exact note `type` followed by `-`, except migrated legacy IDs explicitly grandfathered by migration metadata
- remain stable after creation

### Relation targets

Relationships reference stable IDs, never filenames.

Source evidence references canonical Raw paths because exact source identity is path + integrity metadata.

---
