---
schema_version: 2
id: "synthesis-phase345-istio-kyverno-recovery-ci-config"
type: "synthesis"
title: "Phases 3–5 Synthesis — Istio, Kyverno, OpenBao Recovery, CI, config, Pinning"
topics:
  - "homelab-devsecops"
  - "istio"
  - "kyverno"
  - "openbao"
  - "ci"
aliases:
  - "phase 3"
  - "phase 4"
  - "phase 5"
status: "active"
confidence: "high"
sources:
  - "https://istio.io/latest/docs/releases/supported-releases"
  - "https://kyverno.io/docs/policy-types/cluster-policy/validate/"
  - "https://openbao.org/docs/commands/operator/raft"
  - "https://fluxcd.io/flux/components/helm/helmreleases/"
  - "https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions"
source_count: 30
related:
  - "synthesis-phase2-openbao-scanner-cli"
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

# Phases 3–5 Synthesis — Istio, Kyverno, OpenBao Recovery, CI, config, Pinning

## Overview

Deep-research jobs filling gaps 1–6 (Phase 3: Istio + Kyverno; Phase 4: OpenBao Raft
recovery + CI diff; Phase 5: config.env dedup + scanner/action pinning). Job IDs:
`a481a680…` (Istio), `c3f6c0e7…` (Kyverno), `5831a940…` (OpenBao Raft),
`1043eccb…` (CI diff), `c2d4b912…` (config.env), `2101bba4…` (scanner pinning).

## 1. Istio (gap 1) — REMOVE unless learning is explicit

- **Not load-bearing**: Headlamp/OpenBao/Flux/Tailscale work via plain Services +
  Tailscale operator + NetworkPolicies + Kyverno. base+istiod+CNI meshes nothing
  automatically (needs injection labels + Pod recreation).
- **⚠️ mTLS × Tailscale**: non-injected Tailscale proxy → sidecar-injected STRICT
  backend = FAILS (destination Envoy rejects plaintext). Keep tailscale/headlamp/openbao
  OUT of injection; don't apply mesh-wide STRICT blindly.
- **⚠️ 1.24.3 is unsupported (Aug 2026)**; current = 1.30.x. Decision binary: upgrade
  to supported 1.30.x OR remove. Removing is the default recommendation unless
  service-mesh learning is an explicit repo objective (then: dedicated mesh-demo ns,
  one client+server, STRICT + one AuthorizationPolicy, one smoke check, no gateway).

## 2. Kyverno (gap 2) — PSA + Kyverno, one authoritative implementation

- **PSA owns PSS** (Baseline enforce / Restricted audit-warn in app namespaces, version
  pinned to K8s minor); **Kyverno owns non-PSS K8s admission rules**; **Conftest only
  unique repo/aggregate/non-K8s checks**. Do NOT maintain equivalent rules in Rego AND
  Kyverno (review rule-by-rule, not tool-by-tool).
- **Enforce immediately**: disallow-latest, require explicit tags, minimal labels.
  **Audit first**: runAsNonRoot, read-only rootfs, drop-all-caps, resource requests,
  registry allowlist, default-deny netpol. Promote individually after reports clean.
- **No broad Flux exclusion** — Flux-applied resources ARE admission requests; exclude
  specific ns/kinds/SA per-policy only. Kyverno mutation can fight Flux (drift) — prefer
  explicit Git values.
- **Graph**: Kyverno engine in `platform`; ClusterPolicies in `policies`;
  `policies dependsOn platform`; `apps dependsOn policies`. Kyverno NOT in bootstrap.
- **⚠️ research could NOT inspect the repo** — verify current Kyverno install/version,
  IaC.yml policy steps, existing Rego/PSA, kind CNI NetworkPolicy support first.

## 3. OpenBao Raft recovery (gap 3) — snapshot API, not file copies

- `bao operator raft snapshot save/restore`; add `sha256sum`; **`-force`/`-stage`
  semantics unverified — check `-help` of the installed version**. Snapshot = encrypted
  storage state (policies, auth, roles, KV, Transit) — NOT a substitute for unseal/
  recovery material. Sealed/unsealed is runtime state, not restored.
- **Shamir preferred for homelab** (manual unseal OK; no circular dependency).
- **Runbook**: daily + pre/post-change snapshots, off-cluster storage (≥2 failure
  domains), quarterly destructive drill; rebuild kind → Flux prerequisites only →
  validate PVC==Raft path → restore via snapshot API (never file-copy; never reinit over
  old data) → unseal → verify (canary KV/policy/Transit + pod-deletion persistence) →
  secret-consumers → tailnet workloads → apps. **Diagnose, don't reinit.**
- **Tailnet Lock cycle**: recovery must not depend on both OpenBao AND Tailnet Lock;
  keep external signer offline, use `kubectl port-forward` for recovery.

## 4. CI diff (gap 4) — DELETE the Deploy job

- Remove: Tailscale connect, kubeconfig, `flux install`, GitRepository delete/recreate,
  `--tag-semver`, `kubectl apply -k`, per-layer `flux reconcile`. **Rendering ≠
  deploying** (keep `kustomize build`; drop `kubectl apply -k`).
- Add: dedicated render-and-schema job (kustomize build all overlays + kubeconform
  strict + Flux CRD schemas), `flux check --pre` (offline; live `flux check` = separate
  health workflow), tracked-secret/`.gitignore` checks, report-vs-fail independence
  (`if: always()` upload then enforce), SARIF with unique categories + artifact upload.
- **Least privilege**: `contents: read` workflow-level; `security-events: write` only on
  SARIF job; remove all cluster/Tailscale creds. Validation works with homelab OFFLINE.
- **Branch-main**: `GitRepository.spec.ref.branch: main`; remove tag triggers/semver;
  protect main (required checks, block direct pushes). README currently says tags deploy
  → intentional release-policy change.
- **Action pinning**: full-SHA everywhere + dependabot.

## 5. config.env dedup (gap 5) — one-value-one-owner

- Keep in config.env: CLUSTER_NAME, bootstrap flags, local secrets (never plaintext).
- Move out: image tags → Deployment/Kustomize `images.newTag`; chart versions →
  HelmRelease; app image → Helm values; namespaces → manifests; scanner/action versions
  → workflow; script defaults `${VAR:-x}` → delete.
- **Single source of truth ≠ one versions.yaml** (adds indirection). Migration: freeze →
  inventory by names AND literals → one semantic value at a time, kind reconcile as
  acceptance test → remove script defaults last → narrow CI guardrail check.

## 6. Scanner/action pinning (gap 6) — policy solid, pins UNRESOLVED

- **Full-40-char-SHA pinning for actions** (with version comment); digest pinning for
  scanner images (tag@sha256). Dependabot for github-actions. Trivy+gitleaks mandatory;
  Grype + Checkov-OR-KICS scheduled; Conftest/TFLint exit-status gates.
- **⚠️ Rate-limited research: NO primary sources retrieved — no version/SHA/digest can
  be responsibly stated.** Concrete pins must be verified manually against official
  release pages before merge. SARIF 2.1.0 expected, revalidate; per-scanner SARIF must
  be validated in GitHub, not assumed.

## Cross-cutting notes

- Multiple Phase-3/4/5 jobs could NOT retrieve the repo (rate limits) → repo-specific
  verification is owed before implementation on: Kyverno current state, OpenBao Raft
  path/mount/node_id/seal, exact config.env occurrences, workflow file line-level steps,
  kind CNI NetworkPolicy support.
- All findings feed: `t_be08f1f7` (Kyverno), `t_e1543bed` (layer collapse), `t_bad33959`
  (CI), `t_56366f53` (branch main), `t_88807336` (P2 umbrella), `t_4f48fe1d`/`t_419e00e5`
  (pinning), `t_92a0a39d` (OpenBao persistence docs).