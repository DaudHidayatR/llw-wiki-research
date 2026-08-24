---
schema_version: 2
id: "concept-openbao-policy-reconcile"
type: "concept"
title: "OpenBao Policy-as-Code and Host-Driven Reconciliation"
topics:
  - "homelab-devsecops"
  - "openbao"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-openbao-tls-policy.md"
source_count: 1
related:
  - "concept-openbao-http-behind-tls"
  - "project-homelab-devsecops"
relationships:
  - "related-to|project-homelab-devsecops"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# OpenBao Policy-as-Code and Host-Driven Reconciliation

## Definition

Keep OpenBao ACL policies as native HCL files, maintain a thin YAML mapping inventory for
principal-to-policy assignments, and reconcile them with a host-driven `bao` command
rather than an in-cluster controller. [C-001]

## Policies and Mappings

OpenBao natively documents ACL policies in HCL or JSON, not YAML. Policies should stay as
native HCL files (`bao policy write` accepts them directly); YAML should not be converted
into a home-grown ACL language. A thin YAML inventory (`openbao/mappings.yaml`) can bind
Kubernetes roles (serviceAccounts/namespaces/audience/policies/tokenTTL) and be translated
by a reconciler into `bao policy write` + `bao write auth/kubernetes/role/<name>`.
Validate the inventory against JSON Schema; reject unknown keys, empty names, wildcard
bindings unless approved, missing policy files, duplicate roles, and out-of-range TTLs.
[C-001]

## Host-Driven vs In-Cluster Controller

Host-driven reconciliation is preferred: a controller that repairs authentication may
depend on the same authentication it repairs, and Git write access becomes indirect
OpenBao administrative access. The OpenBao Secrets Operator is archived (February 2026)
and recommends External Secrets Operator instead; ESO supports OpenBao for secret
synchronization, not ACL/auth configuration. Flux should manage Kubernetes resources but
not OpenBao's internal control plane. [C-001]

## Root-Token Minimization

Root policy is not the same as `sudo`. Root-protected paths require the operation's
capability plus `sudo` on specific prefixes, so a non-root token can be delegated the
necessary capability plus narrowly scoped `sudo`. Bootstrap sequence: install →
initialize/unseal → distribute unseal/recovery material outside Git → use the initial
root token to enable auth + create scoped policies/roles → test → revoke the initial root
token; regenerate only via the recovery ceremony. Root tokens, unseal shares, recovery
keys, AppRole SecretIDs, and bootstrap tokens must never be committed to Git. [C-001]

## Auth Matrix

In-cluster workloads → Kubernetes auth (ServiceAccount JWT via TokenReview; Flux v2.9
supports direct OpenBao ServiceAccount-token auth for SOPS decryption). Human
administrators → OIDC (individual identity, groups, revocation, MFA). Off-cluster
automation → AppRole (RoleID + controlled SecretID, pull-mode, short TTL). Userpass only
as temporary bootstrap or break-glass. Suggested policy roles: flux-decrypt,
external-secrets-read, policy-reconciler, platform-auditor, platform-admin (selected
sudo), break-glass-admin. [C-001]

## Evidence Ledger

- C-001 | confidence=high | OpenBao ACLs are HCL/JSON native; a thin YAML mapping inventory is validated by JSON Schema; host-driven bao reconciliation is preferred over an in-cluster controller (OpenBao Secrets Operator archived); root-protected paths use delegated sudo, not the literal root token; auth matrix: kubernetes auth for workloads, OIDC for humans, AppRole for off-cluster automation, userpass for break-glass.
  - source: [[Raw/Sources/deep-research-openbao-tls-policy.md#Normalized Content]]
