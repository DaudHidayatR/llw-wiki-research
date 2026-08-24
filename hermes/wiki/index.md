---
schema_version: 2
id: "project-homelab-devsecops-research"
type: "project"
title: "Homelab DevSecOps — Flux × Tailscale Research"
topics:
  - "homelab-devsecops"
  - "tailscale"
  - "flux"
aliases:
  - "homelab research"
status: "active"
confidence: "high"
sources:
  - "https://pkgs.tailscale.com/helmcharts/index.yaml"
  - "https://fluxcd.io/flux/components/kustomize/kustomizations/"
  - "https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting"
source_count: 21
related:
  - "concept-tailscale-operator-helm"
  - "concept-tailscale-l7-ingress"
  - "concept-tailnet-lock-rebuilds"
  - "concept-flux-gitops-graph"
  - "concept-openbao-http-behind-tls"
relationships:
  - "part-of|project-homelab-devsecops-research"
supersedes: []
superseded_by: []
last_verified: "2026-08-24"
review_after: "2026-11-24"
created: 2026-08-24
updated: 2026-08-24
---

# Homelab DevSecOps — Flux × Tailscale Research

## Overview

Deep research validating and correcting the architecture-audit v2 redesign for
[`DaudHidayatR/homelab-devsecops`](https://github.com/DaudHidayatR/homelab-devsecops):
make **Flux** own persistent Kubernetes desired state, make **Tailscale** exposure
Kubernetes-native (operator + L7 Ingress), keep shell to bootstrap/recovery/diagnostics,
and make CI validation-only.

Method: local LLM-Wiki first (empty on these topics), then an async Open Deep Research
job (`f5139ca8a1534ac2b1f92fb1ce6c323d`, Firecrawl-backed, ~11 min, 21 cited sources,
model gpt-5.6-sol). Full report archived at `/tmp/deep-research-report.md` (ephemeral
sandbox path — re-derivable from the job).

## Core Principle

> **Flux declares. Tailscale reconciles. Shell bootstraps. CI validates.**

## Key Findings Summary

1. Official Tailscale Helm repo: `https://pkgs.tailscale.com/helmcharts`; authoritative
   version source is the repo `index.yaml` (NOT the GitHub Chart.yaml, which carries
   packaging placeholders). Current stable **v1.102.3** (2026-08-20) — the audit's pinned
   **1.96.4 is stale** and must be re-verified before commit. [C-001][C-002]
2. Pre-created `operator-oauth` Secret confirmed: keys exactly `client_id` /
   `client_secret` (underscores significant, issue #16776); never place credentials in
   the HelmRelease. [C-003]
3. Chart `1.92.3` regressed the pre-created-Secret path (issues #18236/#18237/#18244);
   "fixed in 1.92.4" is the reported boundary; pin current and verify the rendered
   Deployment. [C-004]
4. OAuth scopes (least privilege): `devices:core` + `auth_keys` write, plus permission to
   use `tag:k8s-operator`. [C-005]
5. L7 Ingress: `ingressClassName: tailscale`, MagicDNS + HTTPS required, HTTPS on 443,
   `tls.hosts` short name → `<name>.<tailnet>.ts.net`; keep `rules[].host` aligned with
   `tls.hosts`. [C-006]
6. **Standalone-first** for a homelab; ProxyGroup/HA only for a real availability
   requirement (no e2e HA if backends/storage/control-plane stay single-instance). [C-007]
7. Tag model: default `tag:k8s-operator` owns `tag:k8s`; every custom proxy tag must be
   owned by the operator tag. Grant admin group `tcp:443` to `tag:k8s` (modern grants
   syntax preferred over legacy ACLs). [C-008][C-009]
8. Tailnet Lock: explicit signing for occasional rebuilds; pre-signed auth keys only for
   unattended enrollment (narrow tag + ephemeral + short expiry + rotation). Pre-signed
   keys are NOT a drop-in for the operator OAuth Secret. Require ≥1 signer + disablement
   secret outside the kind cluster. [C-010]
9. Flux 4-layer graph `bootstrap → platform → policies → apps` with `dependsOn` +
   `wait: true` + targeted `healthChecks`; waiting on **apps Ready** is a sound K8s
   completion signal (not tailnet reachability). Branch-`main` over semver source
   switching. CI validation-only. [C-011][C-012][C-013]
10. OpenBao `tlsDisable: true` (HTTP :8200) behind Tailscale L7 TLS termination is
    compatible; set the external API address to the HTTPS MagicDNS URL, add a
    NetworkPolicy (tailscale-ns → openbao:8200), and use HTTP probes with state-aware
    readiness (sealed-server trap). [C-014]

## Corrections to the Audit (v2)

- ⚠️ Chart version stale: pin `v1.102.3` (verify from index), not `1.96.4`.
- ⚠️ Tag model: audit proposed two custom admin tags; research default is single
  `tag:k8s` + group grant — custom tags need explicit `tagOwners` + per-tag grants.
- ⚠️ OpenBao advertised address must be the HTTPS MagicDNS URL, not internal HTTP.
- ⚠️ Secret storage: research defaults to encrypted Git (SOPS) / external-secret store
  (durable API credentials; GitHub secret-scanning flags them). Audit's "no SOPS now"
  is a scoping choice, flagged for review.

## Wiki Index

- [[hermes/wiki/concepts/tailscale-operator-helm]] — Helm install + `operator-oauth` Secret
- [[hermes/wiki/concepts/tailscale-l7-ingress]] — L7 Ingress, standalone vs ProxyGroup, tags, grants
- [[hermes/wiki/concepts/tailnet-lock-rebuilds]] — Tailnet Lock + ephemeral kind rebuilds
- [[hermes/wiki/concepts/flux-gitops-graph]] — Flux 4-layer graph, bootstrap ownership, branch vs semver
- [[hermes/wiki/concepts/openbao-http-behind-tls]] — OpenBao plain-HTTP behind Tailscale TLS
- [[hermes/wiki/comparisons/deep-research-gap-analysis]] — coverage vs missing (repo-verified + P2 gaps)
- [[hermes/wiki/synthesis/flux-tailscale-redesign]] — consolidated synthesis
- [[hermes/wiki/synthesis/phase2-openbao-scanner-cli]] — Phase-2: OpenBao HCL+mappings, host-driven reconcile, root-token revoke, Trivy+gitleaks gate, Bash retained
- [[hermes/wiki/synthesis/phase345-istio-kyverno-recovery-ci-config]] — Phases 3–5: Istio remove/upgrade, Kyverno PSA+audit-enforce, OpenBao Raft runbook, CI validation-only, config dedup, SHA/digest pinning

## Evidence Ledger

- C-001 | confidence=high | Official chart repo `https://pkgs.tailscale.com/helmcharts`; index is authoritative; GitHub Chart.yaml has release-time placeholders.
  - source: https://pkgs.tailscale.com/helmcharts/index.yaml , https://github.com/tailscale/tailscale/blob/main/cmd/k8s-operator/deploy/chart/Chart.yaml
- C-002 | confidence=high | Current stable chart version reported as v1.102.3 (published 2026-08-20) via Artifact Hub; verify against official index (leading-`v` matters for Flux constraint).
  - source: https://artifacthub.io/packages/helm/tailscale/tailscale-operator
- C-003 | confidence=high | Pre-created Secret `operator-oauth`, keys `client_id` / `client_secret` (underscores significant); not `clientId`/`clientSecret`.
  - source: https://github.com/tailscale/tailscale/issues/16776
- C-004 | confidence=high | Chart 1.92.3 broke pre-created-Secret path (missing CLIENT_ID_FILE/CLIENT_SECRET_FILE + /oauth mount → crash loop); fix reported at 1.92.4.
  - source: https://github.com/tailscale/tailscale/issues/18236 , https://github.com/tailscale/tailscale/issues/18237 , https://github.com/tailscale/tailscale/issues/18244
- C-005 | confidence=high | OAuth client needs devices:core (write), auth_keys (write), permission to use tag:k8s-operator and configured proxy tags.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting
- C-006 | confidence=high | L7 Ingress selected via `ingressClassName: tailscale`; MagicDNS + HTTPS required; hostname in tls.hosts becomes `<name>.<tailnet>.ts.net`.
  - source: https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress
- C-007 | confidence=high | Standalone ingress = one single-replica proxy per resource (least config, lower resources, easiest troubleshooting); ProxyGroup = documented HA mechanism with higher cost; no e2e HA if backends single-instance.
  - source: https://tailscale.com/kb/1445/kubernetes-operator-customization , https://tailscale.com/kb/1541/kubernetes-operator-multi-cluster-ingress
- C-008 | confidence=high | Default tags tag:k8s-operator (operator) and tag:k8s (proxy); operator tag must own proxy tags via tagOwners.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting , https://tailscale.com/docs/kubernetes-operator/reference/tags
- C-009 | confidence=high | Tailscale recommends grants over legacy ACLs for new policy; grants can coexist with ACLs; admin HTTPS access = grant src group → dst tag:k8s, ip tcp:443.
  - source: https://tailscale.com/kb/1324/grants , https://tailscale.com/kb/1538/grants-syntax , https://tailscale.com/kb/1542/grants-migration
- C-010 | confidence=high | Tailnet Lock requires new node keys to be signed; explicit signing recommended for occasional rebuilds; pre-signed auth keys enable unattended enrollment but are high-value credentials and are not a substitute for the operator OAuth Secret.
  - source: https://tailscale.com/kb/1226/tailnet-lock , https://tailscale.com/kb/1085/auth-keys
- C-011 | confidence=high | Flux Kustomization supports dependsOn, wait, healthChecks, timeout for deterministic ordering.
  - source: https://fluxcd.io/flux/components/kustomize/kustomizations/
- C-012 | confidence=high | Branch-main GitOps is right for a homelab; switching GitRepository to semver is for published immutable release configs and creates confusing behavior for a homelab.
  - source: https://fluxcd.io/flux/installation/bootstrap/github/
- C-013 | confidence=high | Flux bootstrap model: bootstrap once → controllers pull → future changes from Git; CI performing flux install / GitRepository delete-recreate / kubectl apply -k / per-layer reconcile violates it.
  - source: https://fluxcd.io/flux/installation/bootstrap/github/
- C-014 | confidence=high | OpenBao tlsDisable:true (HTTP 8200) behind Tailscale L7 TLS termination is compatible; Ingress backend references the Service (name openbao, port 8200); external API address must be the HTTPS MagicDNS URL; NetworkPolicy should restrict :8200 to tailscale-ns.
  - source: https://openbao.org/docs/ , https://tailscale.com/kb/1439/kubernetes-operator-cluster-ingress

## Open Questions / Review Needed

- Tag model decision: single `tag:k8s` vs two custom admin tags (Headlamp vs OpenBao separation).
- Secret storage: SOPS/external-secret now vs "no SOPS" scoping choice.
- Tailnet Lock: confirm ≥1 signer + disablement secret exists outside the kind cluster.
- Verify the exact chart version string from the official index before committing.
