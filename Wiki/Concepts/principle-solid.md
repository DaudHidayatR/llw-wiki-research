# SOLID — Applied to Shell & Declarative Infrastructure

> Wiki/Concepts/principle-solid.md · part of the [engineering principles series](../Projects/homelab-devsecops.md)
> Code findings verified against `DaudHidayatR/homelab-devsecops` @ `e863f90` (re-grepped 2026-09-02).

## TL;DR

SOLID was coined for OOP classes, but its *intent* — one reason to change per unit, stable contracts, depend on abstractions — transfers to shell and GitOps repos. Translated: **one job per function, one owner per file, dependencies passed in rather than hard-coded**. In this repo the layering is mostly right; the debt is concentrated in functions that kept growing past their single reason to change.

## Origin & canonical references

**Facts (documented):**
- Robert C. Martin introduced the principles in his 2000 paper *Design Principles and Design Patterns*; the SOLID acronym was later popularized by Michael Feathers ([Wikipedia: SOLID](https://en.wikipedia.org/wiki/SOLID)).
- SRP's canonical statement: "a class should have only one reason to change" ([seeleycoder summary of the 2000 paper](https://www.seeleycoder.com/solid-design-principles-five-principles-of-oop/); original paper: https://web.archive.org/web/20150906155800/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf).
- OCP (open for extension, closed for modification), LSP (substitutability), ISP (no client forced to depend on what it does not use), DIP (depend on abstractions) complete the set — all in the 2000 paper.

**Inference (explicitly a translation, not the original):** for Bash + Kubernetes YAML + Flux:
- SRP → a function/file owns one operational concern; a manifest directory owns one platform concern.
- OCP → add a scanner/policy by adding a file, not by editing a dispatcher's case list (the scanner submodule layout follows this).
- LSP → sibling subcommands/libs honor the same calling conventions (exit codes, stderr for errors).
- ISP → a library consumer shouldn't be forced to source unrelated helpers.
- DIP → shell functions receive paths/addresses via variables with documented defaults, not buried literals; manifests depend on declared contracts (Secret names), not on imperative side effects.

## Core rules (shell translation)

1. One function = one verb at one abstraction level; banner comments inside a body are a request for extraction.
2. One file = one owner of its knowledge (a scanner lib owns its tool invocation only).
3. Dependencies (paths, namespaces, images) arrive as parameters/env with defaults declared once.
4. Extension by addition: new case → new module wired in one line.

## Code smells / anti-patterns

- A "command" function doing backup + validate + mutate + report.
- Bootstrap functions mixing credential handling with service configuration.
- Hard-coded cluster names/paths repeated inside function bodies instead of the config layer.

## Application to homelab-devsecops (verified @ e863f90)

| # | Finding | Location | Assessment |
|---|---------|----------|------------|
| S1 | `command_cluster_down` (~70 lines, `scripts/commands/cluster.sh`) performs backup creation, validation, cluster deletion, and result reporting in one body — at least three reasons to change (backup policy, kind API, output format). | `scripts/commands/cluster.sh` | SRP violation |
| S2 | OpenBao bootstrap mixes init, unseal, auth methods, audit device, policy seeding, and user creation (see KISS doc K2) — each is an independent concern with an independent failure mode. | `scripts/commands/openbao.sh` | SRP violation |
| S3 | **Positive (SRP):** scanner logic is split per tool: `scripts/lib/scanners/{common,sca,sbom,secrets,iac,image}.sh` (476 lines total) — adding a scanner is additive. | `scripts/lib/scanners/` | good |
| S4 | **Positive (DIP):** `scripts/lib/openbao.sh` declares its defaults (`OPENBAO_NAMESPACE`, `OPENBAO_POD`, `OPENBAO_ADDR`, token source precedence) in one place; callers pass intent, not literals. | `scripts/lib/openbao.sh` | good |
| S5 | **Positive (OCP/ISP):** `scripts/homelab` dispatcher wires command modules in a flat case; each module sources only the libs it needs (include-guards). | `scripts/homelab`, `scripts/commands/*` | good |
| S6 | `tailscale::ensure_deploy_secret` implements an explicit SOPS→env precedence contract and hard-fails on missing material — a clean, documented dependency boundary between secrets and install flow. | `scripts/lib/tailscale.sh` | good |

**Proposals (PROPOSAL):** extract `cluster::backup_lifecycle`, `cluster::destroy`, `cluster::report` from S1; split openbao bootstrap into stage functions mirroring its banner sections (shared with the KISS fix — one refactor serves both docs).

## When to break the rule

- Top-level command functions may *orchestrate* many steps — that is their single responsibility. The smell is *doing* the steps inline, not *calling* them.
- DIP in shell has a floor: at some point a script touches real paths. Declare defaults in one place; that is enough.

## Review checklist

- [ ] One sentence per function, no "and"?
- [ ] Could a new scanner/policy/app be added by adding files only?
- [ ] Are paths/namespaces/images declared once, not inlined at call sites?
- [ ] Does each file own exactly one kind of knowledge?
