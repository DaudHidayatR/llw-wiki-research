---
schema_version: 2
id: "source-deep-research-flux-gitops"
type: "source"
title: "Deep Research — Flux 4-Layer Graph, Bootstrap Ownership, Branch vs Semver"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-f5139ca8-1043eccb"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:7810f414007d7884fdda5e98cb75e33093fe4b01efd90d8efa45e33316540aee"
---

# Deep Research — Flux 4-Layer Graph, Bootstrap Ownership, Branch vs Semver

## Normalized Content

Flux Kustomization supports `dependsOn`, `wait: true`, `healthChecks`, and `timeout` for
deterministic dependency ordering. A 4-layer graph `bootstrap → platform → policies →
apps` is the recommended shape.

Contents: **bootstrap** = Flux controllers + source, namespaces, secret-decryption
bootstrap (SOPS age key / external secret), essential CRD prerequisites that cannot be
introduced later (keep small — everything depends on it). **platform** = reusable infra —
Tailscale operator, ingress controllers, OpenBao, storage provisioners, cert/DNS
controllers, their CRDs and prerequisite Secrets. **policies** = controls depending on
platform APIs — NetworkPolicies, admission policies, RBAC overlays, pod-security labels
(do not apply before their CRDs/controllers exist; don't introduce default-deny before
required connectivity is described). **apps** = user workloads + their Tailscale Ingress.

With `wait: true` on the apps Kustomization, it stays non-Ready until reconciled
workloads pass Flux's health assessment — waiting on **apps Ready** is a sound Kubernetes
completion signal (shell does not need the layer list). Caveat: Flux readiness is
Kubernetes controller health, NOT full tailnet DNS, certificate issuance,
access-policy correctness, or app-login success; final tailnet reachability still needs
Ingress-status/tailnet checks.

Use explicit `healthChecks` for especially important or out-of-inventory objects (e.g. a
Deployment + Ingress by name). Do not over-serialize: unrelated platform components
(Tailscale vs storage vs OpenBao) can reconcile independently via per-component platform
Kustomizations only where independent failure domains add real value.

Keep `GitRepository.spec.ref.branch: main` for a homelab; promotion is a merge/commit to
main. Switching the whole GitRepository to semver source selection is appropriate only
for intentionally published immutable semantic-release configuration; for a homelab it
causes: commits to main do not deploy until tagged, the highest matching tag can
auto-activate, emergency fixes require a new tag, and source-level release semantics
become coupled to all apps. Prefer main + pinned Helm chart versions + pinned container
image tags/digests + automated PRs + git revert for rollback.

Flux bootstrap model: bootstrap once → controllers pull desired state → future changes
come from Git. CI performing `flux install` / GitRepository delete-recreate /
`kubectl apply -k` / per-layer reconcile violates that model and makes CI a second
controller. CI should validate/scan/render/test/report and upload SARIF; Flux
deploys/reconciles/repairs drift.

A reference defect in the target repo: the shell hard-codes `flux reconcile kustomization
infrastructure`, but no Kustomization named `infrastructure` exists (actual set:
bootstrap, cluster-resources, platform, openbao-config, cluster-policies, operations,
apps). Shell should not own the Flux dependency graph; `flux::reconcile()` should not
enumerate cluster layers.

## References

- https://fluxcd.io/flux/components/kustomize/kustomizations/
- https://fluxcd.io/flux/components/source/gitrepositories/
- https://fluxcd.io/flux/installation/bootstrap/github/
- https://fluxcd.io/flux/guides/repository-structure/

## Capture Notes

Consolidated from deep-research jobs f5139ca8a1534ac2b1f92fb1ce6c323d (Phase 1, card 4/5)
and 1043eccbd1a546509cf30a9c22c11988 (Phase 4, CI diff). Repo-specific layer names and
Kustomization layout must be verified against the deployed repository.
