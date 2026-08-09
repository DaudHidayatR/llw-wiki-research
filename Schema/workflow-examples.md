# Canonical Operating Workflows

The following workflows are the **single canonical definitions** used by build exercises and future operation.

Build steps should reference these workflows rather than copying them.

---

## Canonical Ingest Workflow

When a source arrives:

1. Put normalized Markdown under `Raw/Sources/`.
2. If an original binary exists, optionally store it under `Raw/Files/`.
3. Ensure source metadata is present.
4. Populate or verify `ContentHash`:

```bash
python3 scripts/wiki_tool.py source-hash --update-missing
python3 scripts/wiki_tool.py source-hash --check
```

5. Scan source state:

```bash
python3 scripts/wiki_tool.py source-scan --update
python3 scripts/wiki_tool.py source-delta
```

6. Search existing knowledge before opening broad Raw context:

```bash
python3 scripts/wiki_tool.py search-catalog --query "source topic"
```

7. Open only relevant Wiki notes.
8. Classify the source impact:
   - update existing knowledge
   - new concept/entity/topic/project
   - comparison input
   - synthesis input
   - contradiction
   - research question
9. Create/update focused Wiki notes.
10. Add note-level `sources`.
11. Keep `source_count` exact.
12. Mark material claims with claim IDs and Evidence Ledger entries where required.
13. Add explicit relationships only when semantically justified.
14. Preserve contradictions and uncertainty.
15. Create Research items for unresolved questions.
16. Run:

```bash
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint --strict-evidence
python3 scripts/wiki_tool.py graph-build
python3 scripts/wiki_tool.py source-scan --update --accept-covered
python3 scripts/wiki_tool.py source-lint
python3 scripts/wiki_tool.py source-coverage
```

17. Add a Log note only if the ingest meaningfully changed the Knowledge OS.

---

## Canonical Research Workflow

When existing knowledge cannot adequately support a question:

1. Search Wiki.
2. Search existing Research.
3. Inspect relevant active Decisions if project-specific.
4. Build a Context Pack if the question spans multiple notes.
5. State what is already known.
6. Create/update a Research Question or Investigation.
7. Define:
   - question
   - motivation
   - current hypothesis
   - search strategy
8. Add sources.
9. Record:
   - evidence for
   - evidence against
   - contradictions
   - findings
   - confidence
   - unknowns
   - follow-up questions
10. Use claim-level evidence for material factual findings/conclusions.
11. Write a conclusion only as strong as the evidence allows.
12. Promote only reusable supported knowledge into Wiki.
13. Keep unresolved questions under `Research/Open/`.
14. Link Research back to affected Wiki and Decisions.
15. Rebuild catalogs and graph.

Research should visibly preserve:

```text
question
  -> existing knowledge
  -> evidence
  -> finding
  -> Wiki update OR unresolved question
```

---

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

---

## Canonical Decision Workflow

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

---

## Canonical Query Workflow

When answering from the Knowledge OS:

1. Start with:

```text
Wiki/index.md
Wiki/catalog.jsonl
```

2. Classify the request semantically in the agent layer:
   - fact
   - concept
   - relationship
   - comparison
   - decision
   - research
   - global synthesis
3. Search:

```bash
python3 scripts/wiki_tool.py search-catalog --query "user topic"
```

4. Open the smallest useful set of relevant Wiki notes.
5. Expand explicit/direct relationships:

```bash
python3 scripts/wiki_tool.py related --id "note-id"
```

6. Inspect relevant Research.
7. Inspect active Decisions when project/architecture-specific.
8. Use Memory only if contextual personalization materially changes the answer.
9. Build a Context Pack for complex questions.
10. Open Raw sources only when:
    - evidence-level verification is necessary
    - compiled knowledge is insufficient
    - sources conflict
    - exact figures/wording are needed
11. Preserve uncertainty.
12. Cite compiled knowledge and Raw evidence as appropriate.
13. If durable new knowledge emerges:
    - record as Research/Finding when appropriate
    - validate evidence
    - promote into Wiki
14. Do not mutate canonical Wiki solely because an LLM produced a plausible answer.

---

## Canonical Complex Concept Workflow

For a complex concept:

1. Find/create the core Concept note.
2. Identify:
   - parent Topics
   - prerequisite Concepts
   - relevant Entities/technologies
   - Comparisons
   - Synthesis notes
   - active Research
   - relevant Decisions
3. Prefer mental models and relationships over flat summaries.
4. Preserve multiple abstraction levels:

```text
claim/fact
   -> concept
   -> topic
   -> comparison
   -> synthesis
   -> domain understanding
```

5. Build a Context Pack containing the smallest connected set that explains the concept.
6. Verify material claims against Raw evidence when necessary.
7. Update Synthesis when new knowledge changes the overall model.

---

## Canonical Context Pack Workflow

Use a Context Pack when:

- more than one Wiki note is needed
- the question spans domains
- relationships matter
- Research or Decisions affect the answer
- the user asks for architecture/comparison/strategy/synthesis
- a long-running agent task needs stable selected context

Selection order should generally favor:

```text
Synthesis
  -> Comparison
  -> Core Concepts
  -> Entities/Projects
  -> Research
  -> Decisions
  -> Relevant Memory
  -> Raw Evidence
```

But final ranking must follow the deterministic Retrieval Model and selected profile.

Context Packs:

- are generated
- are not permanent Memory
- must not contain invented semantic summaries
- should point to canonical full notes
- may contain bounded exact excerpts

---

## Canonical Human Publishing Workflow

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

---

## Maintenance Gate

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
