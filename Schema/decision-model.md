# Decision Model

### 5. Decisions preserve why

A decision should preserve:

- what was chosen
- context
- rationale
- alternatives
- trade-offs
- consequences
- supporting evidence
- revisit conditions
- supersession history

Never silently overwrite a meaningful historical decision.

### Decision supersession behavior

`decision-supersede` must only perform deterministic metadata/file-state changes.

It must:

- validate both IDs exist
- validate new Decision is active
- update old `status` to `superseded`
- add new ID to old `superseded_by`
- add old ID to new `supersedes`
- move old file to `Decisions/Superseded/`
- preserve body text
- refuse cycles

It must not invent rationale.

# Canonical Decision Workflow

When a meaningful choice is made:

1. Search active Decisions for the same scope.
2. Create/update the new Decision.
3. Record:
   - decision
   - context
   - rationale
   - alternatives
   - trade-offs
   - consequences
   - evidence
   - revisit condition
4. Use claim-level evidence for material external factual justification.
5. Link related Wiki and Research.
6. If replacing an old Decision:
   - create the new Decision first
   - run deterministic supersession
   - preserve old rationale/body
   - preserve bidirectional supersession links
7. Never delete historical rationale only because the current choice changed.
