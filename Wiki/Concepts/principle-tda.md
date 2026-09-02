# TDA — Tell, Don't Ask (and Command–Query Separation)

> Wiki/Concepts/principle-tda.md · part of the [engineering principles series](../Projects/homelab-devsecops.md)
> Code findings verified against `DaudHidayatR/homelab-devsecops` @ `e863f90` (re-grepped 2026-09-02).

## TL;DR

Tell a module what to do; don't reach past it to inspect and decide for it. In shell terms: **the wrapper function owns the `kubectl` idiom; callers pass intent.** The repo already has good intent-level helpers — the debt is that `openbao.sh` bypasses them with raw `kubectl` probes and keeps the same policy knowledge in two parallel tables.

## Origin & canonical references

**Facts (documented):**
- "Tell, Don't Ask" was named by Allen Holub (2000 column) and popularized in *The Pragmatic Programmer* (Hunt & Thomas) as a design guideline: rather than asking an object for data and acting on it, tell the object to act ([crustyoldev summary](https://crustyoldev.wordpress.com/2012/05/06/i-give-the-orders-around-here/); Pragmatic Programmer, Addison-Wesley 1999/2019).
- The related smell-avoidance rule is the **Law of Demeter** (only talk to your immediate friends) — Northeastern University, Lieberherr & Holland, 1987/89.
- **Command–Query Separation** (Bertrand Meyer, *Object-Oriented Software Construction*, 1988): a routine should either do something or answer something, not both — queries don't change state; commands don't answer.
- Holub's formulation: instances shouldn't make decisions about other instances' state based on inspection; behavior belongs where the state lives.

**Inference (shell translation):** "ask" = grepping/`kubectl get`-ing raw state at the call site; "tell" = calling a named helper that encodes that check once (`k8s::pod_exists`, `k8s::wait_pod_ready`). CQS in shell: a function returns data *or* performs an action with logging — both is a smell.

## Core rules

1. One idiom per recurring probe: the helper owns it; call sites never re-derive it.
2. Callers express intent ("wait for the pod"), not plumbing (`kubectl … &>/dev/null`).
3. Knowledge lives in one registry; consumers ask the registry, they don't restate it.
4. A function either reports status or changes state (CQS), not both.

## Code smells / anti-patterns

- The same raw command pattern repeated ≥5 times across one file.
- Two tables/lists encoding the same domain knowledge that must be manually kept consistent.
- Call-site `grep`/`awk` pipelines that duplicate what a lib function already returns.

## Application to homelab-devsecops (verified @ e863f90)

| # | Finding | Location | Evidence |
|---|---------|----------|----------|
| T1 | `openbao.sh` bypasses the existing helpers with raw `kubectl get pod "$OPENBAO_POD" -n "$OPENBAO_NS" &>/dev/null` / `>/dev/null 2>&1` probes at **5 sites** (lines 35, 432, 559, 674, 832) even though `k8s::pod_exists` and `k8s::wait_pod_ready` exist in `scripts/lib/kubernetes.sh`; inline `kubectl wait` duplicates `k8s::wait_pod_ready` at 4+ more sites. Two idioms for the same ask in one file. | `scripts/commands/openbao.sh:35,432,559,674,832` | re-grepped |
| T2 | The engine-enabled check idiom (`python3 -c "import json,sys; …"`) is repeated **17×** in one file — a probe that deserves one `openbao::engine_enabled <name>` helper (see DRY doc; counted 2026-09-02). | `scripts/commands/openbao.sh` | grep -c |
| T3 | `POLICY_FILES` (line 319) and `POLICY_MAPPINGS` (line 338) encode the same policy knowledge in two tables, with a validation step checking consistency between them — the mapping should reference the registry, not restate it. | `scripts/commands/openbao.sh:319,338` | grep |
| T4 | **Positive:** `flux::converge_source` + `flux::verify_source_sync` — the caller tells the lib "converge and verify", the lib owns the `flux`/`kubectl` plumbing and stale-artifact guard. | `scripts/lib/flux.sh` | read |
| T5 | **Positive:** `cluster.sh` validates cluster names via `cluster::exists`/name-validation before destructive ops — ask once, act with confidence. | `scripts/lib/cluster.sh`, `scripts/commands/cluster.sh` | read |

**Proposals (PROPOSAL):** route T1's probes through the existing `k8s::*` helpers (or delete the helpers — pick one idiom, see YAGNI doc Y1); introduce `openbao::engine_enabled`; derive `POLICY_MAPPINGS` from `POLICY_FILES` programmatically.

## When to break the rule

- Debugging/diagnostics code may inspect raw state at the call site — that is its job.
- A one-off probe in a throwaway branch is cheaper than a new helper; extract at the second or third occurrence (Rule of Three, see DRY doc).

## Review checklist

- [ ] Does every recurring `kubectl`/`grep` probe have exactly one owning helper?
- [ ] Do call sites read as intent ("wait for pod") rather than plumbing?
- [ ] Is any domain list stated in two places?
- [ ] Does each function either answer or act (CQS)?
