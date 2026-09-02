# DRY — Don't Repeat Yourself

> Wiki/Concepts/principle-dry.md · part of the [engineering principles series](../Projects/homelab-devsecops.md)
> Code findings verified against `DaudHidayatR/homelab-devsecops` @ `e863f90` (re-grepped 2026-09-02).

## TL;DR

Every piece of knowledge gets one authoritative representation. The cost of duplication is not lines — it is **silent divergence**, and this repo already exhibits it: the same scanner is pinned to two different versions in two files. Duplication of *knowledge* (things likely to change together) is the sin; incidental textual similarity is not.

## Origin & canonical references

**Facts (documented):**
- Stated by **Andy Hunt & Dave Thomas** in *The Pragmatic Programmer* (1999; 20th-anniversary ed. 2019): "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system" ([Wikipedia: Don't repeat yourself](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)).
- The 20th-anniversary edition explicitly distinguishes **knowledge duplication** (must fix) from **textual/incidental duplication** (often fine — e.g. two structs that look alike but change for different reasons) — see [Milan Jovanović's summary](https://milanjovanovic.tech/blog/dry-is-the-most-misunderstood-rule-in-programming) and the book itself.
- **Rule of Three** (Fowler et al., *Refactoring*): tolerate duplication twice; extract at the third occurrence — the practical calibration for when extraction pays.
- Related: Page-Jones (1995) discussed redundancy costs under structured design; Hunt's "orthogonality" chapter treats DRY as its local case.

**Inference:** in infra repos the highest-value DRY targets are *versions/identifiers* (images, charts, actions) and *procedural idioms* (backup patterns, probes), because both drift silently.

## Core rules

1. One owner per piece of knowledge: version, image, path, idiom, table.
2. Distinguish knowledge duplication (fix now) from textual coincidence (leave).
3. Extract at the third occurrence (Rule of Three) — earlier only when drift is already visible or the item is a version pin.
4. When two files must agree, make one generate/validate the other.

## Code smells / anti-patterns

- The same version string in two files (guaranteed future drift).
- An idiom block repeated many times in one file (each copy a maintenance point).
- Parallel tables/lists restating one domain.
- Copy-pasted security-sensitive blocks (sanitizers) — divergence here is a vulnerability.

## Application to homelab-devsecops (verified @ e863f90)

| # | Finding | Location | Evidence |
|---|---------|----------|----------|
| D1 | Scanner-version drift (proof of DRY cost): `TRIVY_IMAGE` = **0.70.0** in `config.env.example:85` vs **0.61.0** in `.github/workflows/IaC.yml:51`; CHECKOV 3.2.473 vs 3.2.414. One logical value, two owners, already diverged. | `config.env.example` vs `.github/workflows/IaC.yml` | grep 2026-09-02 |
| D2 | Identity-Secret sanitizer python block — the exact key-popping list (`creationTimestamp, resourceVersion, uid, managedFields, selfLink, ownerReferences`) duplicated verbatim in two modules. Security-sensitive: a key added to one copy and not the other leaks metadata. | `scripts/lib/tailscale.sh:149` and `scripts/commands/tailscale.sh:370` | grep |
| D3 | Engine-enabled probe idiom `python3 -c "import json,sys; …"` repeated **17×** in `openbao.sh` — extract `openbao::engine_enabled <name>` once (counted 2026-09-02). | `scripts/commands/openbao.sh` | grep -c |
| D4 | temp-file + `chmod 0600` + atomic-`mv` backup pattern duplicated 3× (`commands/cluster.sh` ×2, `commands/tailscale.sh` reset ×1) — Rule-of-Three candidate for a `common::atomic_backup` helper. | `scripts/commands/*.sh` | grep |
| D5 | `POLICY_FILES` + `POLICY_MAPPINGS` restating policy knowledge (shared with TDA doc T3). | `scripts/commands/openbao.sh:319,338` | grep |
| D6 | **Positive:** `common::mktemp_var` shared primitive used across `lib/cluster.sh` and `homelab_test.sh`; include-guards preventing double-source; a single `.sops.yaml` owning the encryption policy; helper functions owning each scanner invocation (no per-tool copy-paste). | `scripts/lib/common.sh` et al. | read |

**Proposals (PROPOSAL):** `openbao::engine_enabled` (D3/D5); `sanitize_secret_json` helper owning D2; `common::atomic_backup` (D4); a single scanner-image inventory consumed by both config and CI (D1 — board card t_c6143b3f covers the ownership matrix; cite this doc as the principle-level rationale).

## When to break the rule

- Textual similarity between things that change for different reasons (anniversary-edition caveat) — forcing them through one abstraction couples unrelated changes.
- CI YAML: minor duplication of step blocks is often cheaper than composite actions; extract only once a third workflow needs it.

## Review checklist

- [ ] Every version/image pin declared in exactly one file?
- [ ] Any idiom past its third repetition?
- [ ] Security-relevant blocks (sanitizers, permission lists) owned by one helper?
- [ ] When two files must agree — does one generate or validate the other?
