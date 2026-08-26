---
schema_version: 2
id: "source-deep-research-phase6-verification"
type: "source"
title: "Deep Research — Phase 6 Verification Findings (repo + primary sources)"
Author: "Hermes Deep Research"
Reference: "deep-research-phase6-2026-08-24"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:7631d46a5bd8831b9099c9bb11acd6bd19333cecb86e0bc957d82fdc9bf2198f"
---

# Deep Research — Phase 6 Verification Findings (repo + primary sources)

## Normalized Content

Phase 6 closed the knowledge gaps by verifying against the live repo
(DaudHidayatR/homelab-devsecops) and primary upstream sources on 2026-08-24.

### Tailscale operator chart (primary source)

Official index `https://pkgs.tailscale.com/helmcharts/index.yaml`:
latest stable chart `1.102.3`, `appVersion v1.102.3`, published 2026-08-20,
chart digest `c2440014df04fdf1b67b53daa4290d7b878584cf4702f9b1b50f51ba64499a6a`.
The audit's earlier pin (1.96.4) is stale (1.96.5 exists; latest is 1.102.3).
The deep-research v1.102.3 claim is confirmed exactly (leading `v` only in
appVersion, not the chart version). Version chain visible: 1.102.3, 1.102.2,
1.98.9, 1.98.4, 1.98.3, 1.96.5, 1.94.2, 1.94.1, 1.92.5, 1.92.4, 1.92.3.

### Kyverno (primary source)

Latest Kyverno release v1.19.0 (Aug 2026; supported release train). The repo
pins `KYVERNO_IMAGE: ghcr.io/kyverno/kyverno-cli:v1.13.0` — outdated by ~6
minor versions. Kyverno Helm chart current ~3.9.0 (Artifact Hub).

### Conftest (primary source)

Latest Conftest v0.69.0. The repo pins `CONFTEST_IMAGE:
docker.io/openpolicyagent/conftest:v0.56.0` — outdated.

### kind NetworkPolicy enforcement (repo-verified)

`bootstrap/controllers/kind-cluster.yaml` has no `networking.cni` /
`disableDefaultCNI` override (only `apiServerAddress`). Default kind CNI is
kindnetd, which does NOT implement NetworkPolicy. The repo's
NetworkPolicies (openbao/network-policy.yaml, headlamp/network-policy.yaml)
therefore render but have zero runtime enforcement. Manifests rendering
successfully is not runtime enforcement.

### Kyverno engine absent (repo-verified)

Kyverno ClusterPolicies exist (`cluster-policies/pod-security/
disallow-privileged.yaml` with `validationFailureAction: Enforce` and
background: true; `resource-governance/require-labels.yaml`), but no Kyverno
engine is deployed anywhere in Flux (no HelmRelease, no namespace). CI runs
only the Kyverno CLI check (`kyverno-cli:v1.13.0 apply ... --resource
rendered-manifests.yaml`). The ClusterPolicies are dead manifests — they
render in CI but no admission controller enforces them in-cluster.

### Istio removal impact (repo-verified)

Istio 1.24.3 on all three HelmReleases (istiod/base/cni) — far outside
upstream support (current 1.30.x). Only the `demo` namespace (sample-app)
has `istio-injection: enabled`; `istio-system` and `openbao` are disabled;
Headlamp has no injection label. PeerAuthentication STRICT is scoped to
`istio-system` only, not global. Removing Istio = delete 3 HelmReleases +
istio-system namespace + the demo injection label; sample-app (plain nginx)
has no sidecar-enforced dependency, so traffic is unaffected. No learning
scenario blocks removal unless service-mesh learning is an explicit goal.

### OpenBao recovery (repo-verified)

Raft storage path IS aligned: `values.yaml` renders `storage "raft" { path =
"/openbao/data" }`, matching the chart mount at /openbao/data (the earlier
alignment P0 was fixed). tlsDisable: true; readiness uses
`/v1/sys/health?standbyok=true&sealedcode=204&uninitcode=204`. Backup is
file-based metadata (`.runtime-backups/openbao` — root-token.txt + metadata
via scripts/commands/openbao.sh), NOT `bao operator raft snapshot save`; no
retention, scheduling, integrity check, or restore drill.

### CI evidence contract (repo-verified)

IaC.yml `secrets` job: gitleaks `continue-on-error: true` then "Fail on
GitLeaks findings" `if: always()` then "Validate report" then upload-artifact
— report-vs-fail independence implemented. `misconfig` job: Trivy + Checkov
`continue-on-error`, "Validate reports", "Fail on HIGH/CRITICAL"
`if: always()`, SARIF upload (`github/codeql-action/upload-sarif@v4`
continue-on-error), artifact upload — implemented. The `deploy` job STILL
EXISTS (line ~237): triggered on `refs/tags/v*`, connects Tailscale
(`tailscale/github-action@v3`), installs Flux CLI (`fluxcd/flux2/action@main`),
`flux install` if CRDs absent, deletes/recreates GitRepository with
`--tag-semver=">=0.0.0"`, `kubectl apply -k` — exactly the second
cluster-manager behavior to remove. Actions use major-version refs
(`@v4`, `@v5`, `@main`, `@v3`), not full SHAs.

### config.env ownership (repo-verified)

`HEADLAMP_VERSION="v0.30.0"` and `SAMPLE_APP_IMAGE="nginx:1.30.1-alpine"`
duplicate manifest pins (Headlamp deployment already pins digest
`sha256:5b46b8bd...`). `FLUX_GIT_TAG=">=0.0.0"` enables semver deployment
mode. Keep CLUSTER_NAME / GITHUB_USER / GITHUB_TOKEN / namespaces /
OPENBAO_BACKUP_DIR. Drift confirmed between config.env and manifests.

## References

- https://pkgs.tailscale.com/helmcharts/index.yaml
- https://github.com/kyverno/kyverno/releases
- https://kyverno.io/docs/installation/releases/
- https://github.com/open-policy-agent/conftest/releases
- https://github.com/DaudHidayatR/homelab-devsecops (repo inspection)
- https://kind.sigs.k8s.io/docs/user/configuration/

## Capture Notes

All repo facts verified by direct clone inspection at commit HEAD (2026-08-24).
Version facts verified against primary release pages/indexes. Some items
require a live cluster to verify (OpenBao seal state, Raft node_id, real
restore behavior, L7 Ingress runtime behavior, Tailnet Lock signer
placement) — recorded as Research/Open items.