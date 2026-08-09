# Memory Promotion Rules

Copy this policy into `Schema/memory-model.md` and summarize it in `AGENTS.md`.

```text
temporary task state
    -> working context

meaningful event that may matter later
    -> episodic memory

stable user/system preference confirmed or repeatedly observed
    -> preference memory

tentative pattern
    -> observation memory

chosen option with rationale
    -> Decision

supported reusable fact/concept
    -> Wiki
```

Rules:

- One-off conversational details do not become durable Memory by default.
- A one-off observation must not become a durable preference.
- Preferences should be confirmed or repeatedly observed.
- Memory does not count as external factual evidence.
- Factual Memory must be validated against evidence before promotion into Wiki.
- Decisions belong in `Decisions/`, not `Memory/`.
- Stale Memory may remain for historical context when clearly marked.


## Canonical Memory Workflow

When new contextual information appears:

1. Decide whether it is temporary working context.
2. If likely reusable, classify it:
   - episodic event
   - preference
   - tentative observation
3. Do not create durable Memory for trivial information.
4. Do not promote one observation into a preference.
5. Do not treat Memory as external factual evidence.
6. If a factual memory should become Wiki knowledge, validate it against evidence first.
7. If Memory changes a meaningful choice, record the choice under Decisions.
8. Mark stale/superseded Memory rather than silently rewriting history when the old context remains useful.
