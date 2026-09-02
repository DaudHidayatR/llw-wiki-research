---
schema_version: 2
id: "concept-principle-kiss"
type: "concept"
title: "KISS — Keep It Simple, Stupid"
topics:
  - "homelab-devsecops"
  - "simplicity"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-principle-kiss.md"
source_count: 1
related:
  - "project-homelab-devsecops"
  - "concept-principle-yagni"
  - "concept-principle-solid"
  - "concept-principle-tda"
  - "concept-principle-dry"
relationships:
  - "applies-to|project-homelab-devsecops"
supersedes: []
superseded_by: []
last_verified: "2026-09-02"
review_after: "2026-12-02"
created: 2026-09-02
updated: 2026-09-02
---
# KISS — Keep It Simple, Stupid

> Wiki/Concepts/principle-kiss.md · part of the [engineering principles series](../Projects/homelab-devsecops.md)
> Code findings verified against `DaudHidayatR/homelab-devsecops` @ `e863f90` (re-grepped 2026-09-02).

## TL;DR

Prefer the simplest thing that solves the *actual* problem. Complexity is a cost paid every time someone reads, debugs, or changes the code — not just when it is written. In this repository the recurring KISS failure mode is the **one giant function** that bundles many jobs, and **duplicated near-identical targets** in the Makefile.

## Origin & canonical references

**Facts (documented):**
- KISS was articulated at Lockheed's Skunk Works by lead engineer **Kelly Johnson**; the U.S. Navy noted the design principle in 1960. The canonical story: Johnson handed engineers a handful of tools and required that the aircraft be repairable in the field by an average mechanic with only those tools — "stupid" refers to the mismatch between how things break and the sophistication available to fix them. ([Wikipedia: KISS principle](https://en.wikipedia.org/wiki/KISS_principle); [Ben Rich, biographical memoir of C. L. Johnson, National Academies Press, 1995](https://www.nasonline.org/wp-content/uploads/2024/06/johnson-clarence.pdf))
- Johnson's own transcription was "Keep it simple stupid" (no comma); the "Keep It Short and Simple" backronym is a later folk variant ([Wikipedia](https://en.wikipedia.org/wiki/KISS_principle)).
- Relation to Occam's razor: both prefer fewer assumptions/moving parts, but KISS is an *engineering-maintainability* heuristic, not a logic principle ([lawsofsoftwareengineering.com](https://lawsofsoftwareengineering.com/laws/kiss-principle/)).

**Inference (opinion, low confidence on attribution details):** modern software statements ("simplest thing that could possibly work" — XP) descend more from the maintainability reading than from the field-repair anecdote.

## Core rules

1. Solve the problem you have, not the one you imagine (overlap with YAGNI).
2. A function does one job at one level of abstraction; if you need "and" to describe it, split it.
3. Prefer flat and boring (linear scripts, explicit steps) over clever and nested.
4. Duplication of *structure* (copy-paste targets, near-identical blocks) is a smell: extract a parameterized form.
5. Complexity budget: every layer, flag, and special case must pay rent.

## Code smells / anti-patterns

- God-function: >100 lines, mixed abstraction levels, section banner comments doing the job of functions.
- Copy-paste configuration targets differing by one argument.
- Duplicated section numbering / commented "sections" inside one function body.
- Help text maintained by hand in parallel with the code it documents.

## Application to homelab-devsecops (verified @ e863f90)

| # | Finding | Location | Severity |
|---|---------|----------|----------|
| K1 | `command_cluster_up` is a single ~100-line function (lines 5–104 of `scripts/commands/cluster.sh`): validates config, renders kind config, creates cluster, installs Flux, waits for kustomizations — all in one body with banner comments standing in for function boundaries. | `scripts/commands/cluster.sh:5–104` | high |
| K2 | `openbao bootstrap` path is one ~278-line function mixing init, unseal, auth enablement, audit device, seeding, and user creation. | `scripts/commands/openbao.sh` (bootstrap) | high |
| K3 | Section numbering inside bootstrap is duplicated — two blocks both claim "── 11." (≈ lines 220 and 271), a symptom of growing a function by paste instead of extracting stages. | `scripts/commands/openbao.sh:~220, ~271` | low |
| K4 | Four near-identical shell-lint targets (`check-sh`, `fmt-sh`, `lint-sh`, `syntax-sh`) each re-derive the same script list; ~33 lines of hand-written `help` duplicate the `##` comments. | `Makefile:154,161,166,171` + help block | medium |
| K5 | **Positive:** dispatcher `scripts/homelab` is ~27 lines of pure case-dispatch; libraries use include-guards; `flux::converge_source` + `flux::verify_source_sync` hide a multi-step reconcile behind two intent-level calls. | `scripts/homelab`, `scripts/lib/*.sh`, `scripts/lib/flux.sh` | good |

**Proposals (labeled PROPOSAL, not implemented here):**
- Split `command_cluster_up` into `cluster::validate_config`, `cluster::render_kind_config`, `cluster::create`, `cluster::bootstrap_flux` — each independently testable.
- Collapse the four lint targets into one parameterized target (`lint-sh` calling a shared loop); generate help from `##` comments (already the stated convention).
- Extract openbao bootstrap stages into functions named after the sections the banners already declare.

## When to break the rule

- Safety-critical explicitness: a long, flat, obvious recovery procedure beats a "simple" abstraction that hides failure modes (OpenBao recovery is a good candidate for explicitness).
- One-off scripts with no maintenance horizon.

## Review checklist

- [ ] Can each function be described in one sentence without "and"?
- [ ] Are there copy-paste siblings that differ by one parameter?
- [ ] Is hand-maintained help/config duplicated anywhere?
- [ ] Would a newcomer find the entry point (`scripts/homelab`) boring? (It should be.)

## Deep-research provenance

Cited primary sources were validated by Open Deep Research
job `deep-research-job-60f2c929124c410d9ad8d74aa0a66edd` (2026-09-02); the full source ledger lives in
[[Raw/Sources/deep-research-principle-kiss.md]]. Top canonical references:

- https://www.lockheedmartin.com/en-us/news/features/history/kelly-14-rules.html
- https://www.lockheedmartin.com/en-us/news/features/history/u2-dragon-lady.html
- https://web.mit.edu/Saltzer/www/publications/protection/
- https://www.rfc-editor.org/rfc/rfc3439
- https://www.cs.dartmouth.edu/~doug/reader.pdf
- https://www.cs.umd.edu/class/spring2003/cmsc838p/Design/criteria.pdf
