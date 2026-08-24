---
schema_version: 2
id: "synthesis-phase2-openbao-scanner-cli"
type: "synthesis"
title: "Phase-2 Synthesis — OpenBao, Scanner Consolidation, CLI Architecture"
topics:
  - "homelab-devsecops"
  - "openbao"
  - "security"
  - "cli"
aliases:
  - "phase 2"
status: "active"
confidence: "high"
sources:
  - "https://openbao.org/docs/concepts/policies"
  - "https://openbao.org/docs/auth/kubernetes"
  - "https://trivy.dev/latest/docs/"
  - "https://github.com/gitleaks/gitleaks"
source_count: 17
related:
  - "synthesis-flux-tailscale-redesign"
  - "comparison-deep-research-gap-analysis"
  - "project-homelab-devsecops-research"
relationships:
  - "part-of|project-homelab-devsecops-research"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Phase-2 Synthesis — OpenBao, Scanner Consolidation, CLI Architecture

## Overview

Phase-2 deep-research job `5480273985814cbd9f2af190a71d7949` (async, ~10.7 min,
gpt-5.6-sol, 17 sources) answers the Gap B research questions. This fills the open
questions from [[comparison-deep-research-gap-analysis]].

## 1. OpenBao policy-as-code

- **Policies = native HCL** files (OpenBao-native, accepted by `bao policy write`).
  JSON equally native but verbose for ACLs (only if machine-generated). **YAML is NOT a
  native OpenBao ACL language — do not build a home-grown ACL from YAML.**
- **Mappings = thin YAML inventory** (`openbao/mappings.yaml`) binding
  kubernetesRoles → serviceAccounts/namespaces/audience/policies/tokenTTL — translated
  by a reconciler into `bao policy write` + `bao write auth/kubernetes/role/<name>`.
- Suggested repo shape: `openbao/{policies/*.hcl, mappings.yaml, mappings.schema.json}`.

### Host-driven vs in-cluster controller

**Host-driven `homelab openbao reconcile` wins** for this homelab. Reasons:
- A controller that repairs authentication may depend on the very auth it repairs.
- Git write access becomes indirect OpenBao admin access.
- **OpenBao Secrets Operator is ARCHIVED (Feb 2026, read-only)** → use External Secrets
  Operator (Vault provider) for secret sync, NOT for config control-plane.
- Flux should manage K8s resources (OpenBao manifests, SA) but NOT OpenBao's internal
  control plane.
- `bao` writes converge ("write desired again"); policy deletion idempotent.

### Root-token minimization

- Root policy ≠ sudo. Root-protected paths = normal capability + `sudo` on specific
  prefixes — delegable to non-root tokens.
- Init/unseal/recovery material must live OUTSIDE Git.
- Bootstrap: enable auth → create scoped policies/roles → test → **revoke initial root
  token**; regenerate only via recovery ceremony.
- **Auth matrix:** in-cluster workloads → **kubernetes auth** (SA JWT, Flux v2.9 direct
  OA auth for SOPS); humans → **OIDC**; off-cluster automation → **AppRole** (pull-mode,
  short TTL); userpass → break-glass only.

Roles: flux-decrypt, external-secrets-read, policy-reconciler, platform-auditor,
platform-admin (selected sudo), break-glass-admin.

## 2. Scanner consolidation

- **Trivy** = broad consolidated baseline; **Grype** = vuln (overlaps Trivy); **gitleaks**
  = dedicated secrets (complementary); **Checkov/KICS** = IaC policy (overlap each other).
- **Mandatory PR gate = Trivy + gitleaks.** Native validators first (schema, kustomize
  build, helm lint). Image gate scans exact digest + SBOM. **Scheduled deep scan** adds
  Grype comparison + Checkov OR KICS (not both) + full-history rescan.
- **SARIF** (GitHub code scanning) for source-linked alerts: gitleaks owns secrets,
  Trivy owns IaC. **JSON** for full evidence/archival/dedup. Avoid flooding code scanning.

## 3. CLI language

**Retain Bash for phase 2.** Remove responsibilities owned by Flux/scanners/schema first;
remaining is process orchestration (Bash-suitable). Typed config via **JSON Schema +
yq/jq** (not Go). Bash dispatcher + **one Go subcommand** (e.g. `openbao-reconcile`) ONLY
when it outgrows shell. Go justified when direct K8s API integration, persistent recovery
state machines, or complex reconciliation become CENTRAL — not speculative. ADR-006 holds.

## Sources

Full 17 sources in the phase-2 report (`/tmp/phase2_report_clean.md`, ephemeral).
Key: OpenBao policies/auth/AppRole/kubernetes-auth; Flux+OpenBao blog;
Trivy/Grype/Gitleaks/Checkov/KICS docs; GitHub SARIF support.