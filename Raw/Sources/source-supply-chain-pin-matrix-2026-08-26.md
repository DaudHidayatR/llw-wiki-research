---
schema_version: 2
id: "source-supply-chain-pin-matrix-2026-08-26"
type: "source"
title: "Supply-Chain Pin Matrix (2026-08-26) — Actions SHAs + Tool Versions"
Author: "Hermes Deep Research"
Reference: "public-github-api-2026-08-26"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-26"
Captured: "2026-08-26"
Created: "2026-08-26"
Processed: true
tags:
  - "source"
ContentHash: "sha256:eebd8503385c7c7f740827717acf4d872ab54c4f06bf4ad3a7ee2aafeff27660"
---

# Supply-Chain Pin Matrix (2026-08-26)

## Normalized Content

Resolved from the public GitHub API on 2026-08-26. Container image digests
(@sha256:) must be resolved at implementation time from the registry (docker
pull -> print digest) — never fabricated.

### GitHub Actions full SHAs (replace major-version refs in IaC.yml)

- actions/checkout@v4 -> 11d5960a326750d5838078e36cf38b85af677262
- actions/setup-python@v5 -> a26af69be951a213d495a4c3e4e4022e16d87065
- actions/upload-artifact@v4 -> ea165f8d65b6e75b540449e92b4886f43607fa02
- github/codeql-action/upload-sarif@v4 -> cdf488f595d80d6e07e03d4674febd5ab45fa938 (dereferenced tag->commit)
- tailscale/github-action@v3 -> 6cae46e2d796f265265cfcf628b72a32b4d7cade
- fluxcd/flux2/action@main -> da2d22d3690191a315822612085f424e4133b06a (FLOATING branch; pin to a release-tag SHA; becomes unnecessary when the Deploy job is removed)

### Tool versions (current 2026-08-26)

- Cilium chart: v1.20.1 (latest)
- Trivy: v0.74.0 (2026-08-14)
- Grype: v0.117.0 (2026-08-10)
- gitleaks: v8.30.1
- Checkov: 3.3.13
- KICS: v2.1.21
- Kyverno: v1.19.0 (supported train; repo pins v1.13.0 - stale)
- Conftest: v0.69.0 (repo pins v0.56.0 - stale)

### Notes

- Enable Dependabot for the github-actions ecosystem.
- Deleting the CI Deploy job removes the fluxcd/flux2 action + Tailscale
  credentials from the workflow.
- Image digest pinning: use docker://publisher/scanner:<version>@sha256:<digest>
  (image-index digest for multi-arch).

## References

- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- https://github.com/aquasecurity/trivy/releases
- https://github.com/anchore/grype/releases
- https://github.com/gitleaks/gitleaks/releases
- https://github.com/bridgecrewio/checkov/releases
- https://github.com/Checkmarx/kics/releases
- https://github.com/cilium/cilium/releases

## Capture Notes

Resolved via public GitHub API on 2026-08-26. Action SHAs are tag-commit
dereferences; fluxcd/flux2/action@main is a floating branch ref and not an
immutable pin. Image digests intentionally deferred to implementation-time
registry pull.