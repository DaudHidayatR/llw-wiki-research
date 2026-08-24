---
schema_version: 2
id: "source-deep-research-config-pinning"
type: "source"
title: "Deep Research — config.env Ownership and Scanner/Action Pinning"
Author: "Hermes Deep Research"
Reference: "deep-research-jobs-c2d4b912-2101bba4"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:c6d36afb6e62c54134216cf26a12fddc783e8b28e31a1d58363f4d866608d317"
---

# Deep Research — config.env Ownership and Scanner/Action Pinning

## Normalized Content

### config.env single-source-of-truth

One-value-one-owner rule: a value is declared where the system that consumes and
reconciles it is defined; other files may reference that declaration but should not
independently restate its value. Twelve-Factor supports environment variables for
deploy-varying application configuration and credentials, but chart versions, Kubernetes
image tags, namespaces, and CI tool versions are declarative desired state or
implementation details in a GitOps repository and should be owned by the corresponding
declarative resource.

Keep in config.env: CLUSTER_NAME (identifies the local kind cluster before Flux exists),
bootstrap behavior flags that genuinely vary per invocation/machine, local kubeconfig/
path selection, GitHub bootstrap token (secret), Flux bootstrap repo owner/name (only if
multi-fork; otherwise hard-code), Tailscale/OpenBao credentials as SECRET inputs (never
committed plaintext), local registry credentials.

Move OUT of config.env to canonical owner: Deployment/StatefulSet image tag → workload
manifest or Kustomize `images.newTag` overlay; Helm chart version →
`HelmRelease.spec.chart.spec.version`; Helm-managed application image tag →
`HelmRelease.spec.values` (chart version and application version are different concepts
and should not be forced to share one variable); namespaces → Namespace manifests/
Kustomize; CI scanner and action versions → workflow or one shared reusable workflow/
composite action; Flux component version → whichever mechanism actually installs it;
Tailnet domain → manifest/Helm values if in-cluster, GitHub variable if CI-only; script
defaults duplicating manifest versions (`${VAR:-1.2.3}`) → delete.

Do NOT create a universal `versions.yaml`/`versions.env`: single source of truth means
one authoritative owner per semantic value, not all values in one file; a global version
catalog adds indirection and incorrectly couples unrelated versions. GitHub Actions
`vars` should not become an invisible global version catalog; versions that determine the
reviewed CI implementation belong committed beside the workflow.

Drift-prone values: Helm chart versions (HelmRelease must be authoritative), container
image tags (Kustomize `images` for overlay changes; Flux ImageUpdateAutomation can update
marked Git fields — automation changes who updates the canonical field, not where it
lives), CI scanner/action versions (old versions lack databases/checks; floating tags
change without review), Flux/bootstrap tool versions (CLI vs controller vs action are not
always the same artifact), secrets (worst — stale credentials remain active; rotating one
copy only is incomplete; if a real credential was ever committed, revoke/rotate it, not
just delete from HEAD).

Migration mechanics: freeze new version variables in config.env.example; inventory by
variable names AND literal values (`git grep -nF '1.2.3'` catches semantically-duplicated
values with different labels); classify each occurrence as authoritative/consumer/
obsolete/generated/uncertain; separate secrets first; migrate one semantic value at a
time with kind reconciliation as the acceptance test; remove script defaults LAST
(require bootstrap inputs explicitly with `${VAR:?required}`); add a narrow CI guardrail
(`grep -Eq '^[A-Z0-9_]*(VERSION|IMAGE_TAG|CHART_VERSION)=' config.env.example` → fail).

### Scanner and CI-action pinning

Pinning model: branch and tag references are mutable; a full 40-character commit SHA is
immutable and the appropriate form for security-sensitive workflows. Use
`uses: owner/action@<full-sha> # <verified-release-tag>`. Pin scanner container images by
immutable digest (`docker://publisher/scanner:<version>@sha256:<digest>`); the digest,
not the tag, determines the pulled image; pin the image-index digest for multi-arch or a
platform-specific manifest for exact platform bytes. Digest pinning creates an update
burden (a rebuilt image under the same tag has a new digest) — manage via PRs that change
version comment + digest together. Enable Dependabot for the `github-actions` ecosystem.

GitHub code scanning accepts SARIF (historically SARIF 2.1.0 — revalidate current docs).
"Produces SARIF" is not enough: test that GitHub accepts the file without warnings, file
URIs resolve, findings land on the correct lines, rule identifiers are stable between
runs, secrets are redacted, a resolved issue transitions correctly, multiple scanners do
not overwrite one another, and exit-code behavior is independent from upload behavior.
Use a distinct SARIF category per scanner and scan target; do not hide a failed mandatory
scan behind `continue-on-error` merely to reach upload (run + capture status + upload
under `if: always()` + fail after upload).

Recommended gate model: Trivy + gitleaks = mandatory pull-request gates (Trivy limited to
explicitly selected severities/finding classes to avoid noise; gitleaks scans sufficient
history, redacts secret values, keeps allowlists narrow, fails on confirmed findings —
treat any discovered live credential as compromised and rotate it); Grype = scheduled
independent second opinion, advisory until differences are understood; Checkov OR KICS =
one scheduled secondary IaC scanner selected by coverage, SARIF quality, customization,
runtime cost, overlap with Trivy, and false-positive rate; Conftest and TFLint gate pull
requests via exit status (SARIF optional unless native stable output is verified).

As of the research date, no primary release pages could be retrieved (search provider
rate limit) — therefore no concrete version, SHA, or digest can be responsibly stated.
Concrete pins must be verified manually against official release pages before merge.

## References

- https://12factor.net/config
- https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
- https://fluxcd.io/flux/components/helm/helmreleases/
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/store-information-in-variables
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets
- https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning
- https://github.com/aquasecurity/trivy/releases
- https://github.com/anchore/grype/releases
- https://github.com/gitleaks/gitleaks/releases

## Capture Notes

Consolidated from deep-research jobs c2d4b912026c4e18924527e9a708768a (Phase 5,
config.env) and 2101bba45ab64e98a0d94ea44300952c (Phase 5, pinning). The config.env job
hit a repository-search quota and could not verify exact duplicate occurrences; the
pinning job could not retrieve any primary release pages — both require manual
repo/upstream verification before implementation.
