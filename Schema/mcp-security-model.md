# MCP/API Security Contract

MCP/API is optional and is **not part of the minimum core runtime**.

If enabled, create and follow `Schema/mcp-security-model.md`.

### Default network posture

- bind localhost only by default
- require explicit opt-in for LAN/remote exposure
- prefer TLS through a trusted reverse proxy for remote access
- use a strict origin policy for browser APIs
- never use wildcard CORS with authenticated mutation endpoints

### Authentication

Remote or non-local access requires authentication.

Supported implementation may use:

- local OS/user boundary
- bearer token
- mTLS
- trusted reverse-proxy identity
- another documented mechanism

The spec does not require one technology, but anonymous remote mutation is forbidden.

### Authorization

Use capability scopes rather than one all-powerful token.

Recommended scopes:

```text
knowledge.read
research.read
research.propose
memory.read
memory.propose
decision.read
decision.propose
wiki.propose
wiki.review
admin.maintenance
```

Example policy:

```text
normal agent:
  knowledge.read
  research.read

research agent:
  knowledge.read
  research.read
  research.propose

trusted assistant:
  + memory.propose
  + decision.propose
  + wiki.propose

reviewer/human:
  wiki.review

admin:
  admin.maintenance
```

Do not expose unrestricted filesystem mutation by default.

### Resource sensitivity

Default resource policy:

```text
Wiki       readable with knowledge.read
Research   readable with research.read
Decisions  readable with decision.read
Memory     separate scope; private by default
Raw        evidence access only when explicitly needed
Context    generated per request; not broad-listable by default
```

### Mutation model

Prefer proposal-oriented tools:

```text
research.propose_finding
memory.propose
 decision.propose
wiki.propose_update
```

Canonical mutation should pass review or a separately authorized commit path.

### Operational controls

Any networked MCP/API implementation should define:

- authentication
- authorization scopes
- rate limiting
- request/body size limits
- concurrent request limits
- audit logging
- secret redaction
- error handling without sensitive path leakage
- configurable bind host
- safe CORS/origin behavior if HTTP/browser accessible

### Audit record

Mutating operations should record:

```text
timestamp
principal/tool identity
operation
canonical target ID/path
result
review/approval reference if applicable
```

Do not log secrets or full sensitive Memory content by default.

---
