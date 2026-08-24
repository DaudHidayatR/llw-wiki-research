---
schema_version: 2
id: "concept-tailscale-operator-helm"
type: "concept"
title: "Tailscale Operator — Helm Install and operator-oauth Secret"
topics:
  - "homelab-devsecops"
  - "tailscale"
aliases: []
status: "active"
confidence: "high"
sources:
  - "Raw/Sources/deep-research-tailscale-operator.md"
source_count: 1
related:
  - "concept-tailscale-l7-ingress"
  - "project-homelab-devsecops"
relationships:
  - "requires|concept-tailscale-l7-ingress"
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
authenticating via a pre-created `operator-oauth` Secret rather than inlining credentials
in the release. [C-001]

## Official Chart Repository

Official repo: `https://pkgs.tailscale.com/helmcharts`. The authoritative version source
is the repository index (`index.yaml`), not the GitHub Chart.yaml, which carries
release-time placeholders. Current stable was reported as v1.102.3 (2026-08-20); verify
the exact version string (including leading `v`) against the index before committing
because Flux treats the chart-version constraint literally. [C-001]

## Pre-created OAuth Secret

The default static-credential path expects a Secret named `operator-oauth` in the
operator's namespace with exactly the keys `client_id` and `client_secret` (underscores
significant). OAuth credentials must never be placed in the HelmRelease, and the plaintext
Secret must not be committed — Tailscale OAuth secrets are durable API credentials and
GitHub secret-scanning flags them. [C-001]

## OAuth Scopes and the 1.92.3 Regression

The OAuth client needs `devices:core` (write), `auth_keys` (write), and permission to use
`tag:k8s-operator` plus configured proxy tags. Chart `1.92.3` regressed the
pre-created-Secret path (rendered Deployment omitted `CLIENT_ID_FILE`/
`CLIENT_SECRET_FILE` and the `/oauth` mount, causing a crash loop); "fixed in 1.92.4" is
the reported boundary — pin a current release and inspect the rendered Deployment. [C-001]

## Flux Resources

A `HelmRepository` (sourceRef to `pkgs.tailscale.com/helmcharts`) plus a `HelmRelease`
with `targetNamespace: tailscale`, `install.createNamespace: true`,
`install/upgrade.remediation.retries: 3`, and `values.operatorConfig.defaultTags:
[tag:k8s-operator]`. Secret ordering: prerequisites Kustomization (namespace + encrypted
Secret, `wait: true`) → operator Kustomization `dependsOn` it + `healthChecks` on the
HelmRelease. [C-001]

## Evidence Ledger

- C-001 | confidence=high | The Tailscale operator is installed via the official Helm chart with a pre-created operator-oauth Secret (client_id/client_secret), least-privilege OAuth scopes, and the documented Flux resource shapes; chart 1.92.3 regressed the pre-created-Secret path.
  - source: [[Raw/Sources/deep-research-tailscale-operator.md#Normalized Content]]
