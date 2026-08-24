---
schema_version: 2
id: "concept-tailscale-operator-helm"
type: "concept"
title: "Tailscale Operator — Helm Install and operator-oauth Secret"
topics:
  - "tailscale"
  - "homelab-devsecops"
aliases:
  - "tailscale helm install"
status: "active"
confidence: "high"
sources:
  - "https://pkgs.tailscale.com/helmcharts/index.yaml"
  - "https://github.com/tailscale/tailscale/issues/18236"
  - "https://github.com/tailscale/tailscale/issues/16776"
source_count: 6
related:
  - "concept-tailscale-l7-ingress"
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

# Tailscale Operator — Helm Install and operator-oauth Secret

## Definition

Install and manage the Tailscale Kubernetes Operator through Flux as a HelmRelease,
authenticating via a pre-created `operator-oauth` Secret rather than inlining credentials.

## Official Chart Repository

Official repo: `https://pkgs.tailscale.com/helmcharts`. The **authoritative version
source is the repo `index.yaml`** at `https://pkgs.tailscale.com/helmcharts/index.yaml`,
NOT the GitHub `Chart.yaml` — on `main` it carries release-time placeholders
(`version: 0.1.0`, `appVersion: stable`). [C-001]

**Current stable: `v1.102.3`** (published 2026-08-20, via Artifact Hub — secondary
evidence). Verify the exact version string (incl. leading-`v`) from the official index
before committing, because Flux treats the chart-version constraint literally. [C-002]

```bash
curl -fsSL https://pkgs.tailscale.com/helmcharts/index.yaml |
  yq '.entries.tailscale-operator[0] | {version, appVersion, created, digest, urls}'
```

## Pre-created OAuth Secret

The default static-credential path expects a Secret named `operator-oauth` in the
operator's namespace with **exactly** these keys (underscores significant, NOT
`clientId`/`clientSecret` — issue #16776): [C-003]

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: operator-oauth
  namespace: tailscale
type: Opaque
stringData:
  client_id: <OAUTH_CLIENT_ID>
  client_secret: <OAUTH_CLIENT_SECRET>
```

No OAuth credentials go in the HelmRelease. The chart mounts the pre-created Secret and
reads credentials from files. Do not commit the plaintext Secret — use encrypted Git
(SOPS) or an external-secret store; Tailscale OAuth secrets are durable API credentials
and GitHub secret-scanning flags them. [C-003][C-009]

## OAuth Scopes (Least Privilege)

OAuth client needs: `devices:core` (write), `auth_keys` (write), and permission to use
`tag:k8s-operator` plus any configured proxy tags. [C-004]

## The 1.92.3 Regression

Chart `1.92.3` broke the pre-created-Secret path: rendered Deployment omitted
`CLIENT_ID_FILE`, `CLIENT_SECRET_FILE`, the `/oauth` volumeMount, and the
`operator-oauth` Secret volume → operator crash-looped with
"CLIENT_ID_FILE and CLIENT_SECRET_FILE must be set". Confirmed via issues #18236,
#18237, #18244. "Fixed in 1.92.4" is the **reported** boundary (sources prove the 1.92.3
failure, not the 1.92.4 release note). [C-005]

Safeguard when bumping the chart version:

```bash
helm template tailscale-operator tailscale/tailscale-operator \
  --namespace tailscale --version v1.102.3 |
  grep -E 'CLIENT_(ID|SECRET)_FILE|/oauth|operator-oauth'
```

Expected output shows both credential-file variables and the Secret-backed `/oauth` mount.

## Flux Resources

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: tailscale
  namespace: flux-system
spec:
  interval: 1h
  url: https://pkgs.tailscale.com/helmcharts
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: tailscale-operator
  namespace: flux-system
spec:
  interval: 30m
  releaseName: tailscale-operator
  targetNamespace: tailscale
  chart:
    spec:
      chart: tailscale-operator
      version: "v1.102.3"  # verify exact spelling from index
      sourceRef: { kind: HelmRepository, name: tailscale, namespace: flux-system }
      interval: 1h
  install:
    createNamespace: true
    remediation: { retries: 3 }
  upgrade:
    remediation: { retries: 3, strategy: rollback }
  values:
    operatorConfig:
      defaultTags: ["tag:k8s-operator"]
```

**Secret ordering:** put the namespace + encrypted Secret in a prerequisites
Kustomization (`wait: true`), then the operator Kustomization `dependsOn` it and adds a
`healthChecks` on the HelmRelease. [C-006]

## Upgrade Cautions

Changing release name / namespace / `nameOverride` / `fullnameOverride` / OAuth identity
can make the operator register as a NEW tailnet device (new state Secret). Replacing the
OAuth client requires a full operator reinstall, not routine rotation. [C-007]

## Evidence Ledger

- C-001 | confidence=high | Official repo + index authoritative; GitHub Chart.yaml has placeholders.
  - source: https://pkgs.tailscale.com/helmcharts/index.yaml , https://github.com/tailscale/tailscale/blob/main/cmd/k8s-operator/deploy/chart/Chart.yaml
- C-002 | confidence=high | Current stable v1.102.3 (2026-08-20) via Artifact Hub; verify from index.
  - source: https://artifacthub.io/packages/helm/tailscale/tailscale-operator
- C-003 | confidence=high | operator-oauth Secret keys client_id/client_secret; underscore significant; never plaintext.
  - source: https://github.com/tailscale/tailscale/issues/16776 , https://github.com/tailscale/tailscale/blob/main/cmd/k8s-operator/deploy/chart/values.yaml
- C-004 | confidence=high | OAuth scopes devices:core + auth_keys write + operator tag permission.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting
- C-005 | confidence=high | 1.92.3 regression confirmed; 1.92.4 reported fix.
  - source: https://github.com/tailscale/tailscale/issues/18236 , https://github.com/tailscale/tailscale/issues/18237 , https://github.com/tailscale/tailscale/issues/18244
- C-006 | confidence=high | Flux dependsOn/wait/healthChecks for Secret-before-release ordering.
  - source: https://fluxcd.io/flux/components/kustomize/kustomizations/
- C-007 | confidence=high | Naming/OAuth identity changes register a new device; OAuth replacement = reinstall.
  - source: https://tailscale.com/kb/1446/kubernetes-operator-troubleshooting
- C-009 | confidence=high | Tailscale OAuth secrets are durable API credentials; GitHub secret-scanning flags them.
  - source: https://tailscale.com/blog/github-secret-scanning