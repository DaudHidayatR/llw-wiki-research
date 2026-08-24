---
schema_version: 2
id: "source-deep-research-ci-validation"
type: "source"
title: "Deep Research — CI Validation-Only GitOps Pipeline"
Author: "Hermes Deep Research"
Reference: "deep-research-job-1043eccb"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-24"
Captured: "2026-08-24"
Created: "2026-08-24"
Processed: true
tags:
  - "source"
ContentHash: "sha256:0945c22ad80bed14ff11a01796c2dd7db28a814ee6b1b59f2924b54e29972347"
---

# Deep Research — CI Validation-Only GitOps Pipeline

## Normalized Content

The target operating model: CI validates proposed Git changes; Flux continuously deploys
the accepted state from Git. The current Deploy job in the target repo crosses the GitOps
ownership boundary by connecting GitHub Actions to the cluster and installing Flux,
replacing its source, applying manifests, or forcing layer reconciliations.

Steps to REMOVE from CI: connect to Tailscale, configure kubeconfig, install Flux CLI
(retain only if used offline), `flux install` if CRDs are absent (conditional install
hides bootstrap incidents and grants a validation token administrative power), delete/
recreate the `flux-system` GitRepository, `--tag-semver >=0.0.0` source switching,
`kubectl apply -k` (rendering = `kustomize build` is validation; applying = deployment,
remove), per-layer `flux reconcile`, and runtime waits. A missing CRD is an operational
incident or incomplete bootstrap, not something CI should silently repair.

Validation-only additions: a dedicated render-and-schema job (`kustomize build` every
deployable overlay as a first-class required check, then `kubeconform -strict` against
the target Kubernetes version + Flux CRD schemas; maintain a narrow explicit skip list for
unresolvable CRDs — `--ignore-missing-schemas` is a validation ceiling, not success);
Flux-specific validation via `flux check --pre` (offline preflight; live `flux check`
requires a cluster and belongs in a separate manually-dispatched health workflow); secret
and `.gitignore` validation (gitleaks + tracked-sensitive-file check such as
`git ls-files '.runtime-backups/**' '*.tfstate' '.env'` + `git check-ignore`; `.gitignore`
verification is supplementary, not a gitleaks substitute); report-vs-fail independence
(run scanner with `continue-on-error`, upload reports under `if: always()`, then enforce
the exit status); SARIF upload with a unique `category` per scanner/target
(`trivy-kubernetes-rendered`, `checkov-iac`) plus full artifact upload (retention ~14
days). Uploading a `.sarif` via upload-artifact does not create code-scanning results.

Recommended job structure: `lint` / `secrets` / `render-and-schema` / `misconfiguration` /
`policy`. No deploy job. Validation works with the homelab offline and needs no Tailscale,
kubeconfig, or cluster credentials. An ephemeral in-runner kind cluster is the only
legitimate future end-to-end option.

Least privilege: `permissions: contents: read` at workflow level; `security-events:
write` only on the SARIF-uploading job. Avoid `pull_request_target` for untrusted code.
Remove Tailscale OAuth credentials, kubeconfig, Kubernetes service-account tokens, Flux
bootstrap credentials, GitHub PATs, and OpenBao root/unseal material from the workflow.

Action pinning: GitHub's security hardening guidance recommends pinning third-party
actions to a full commit SHA (immutable) rather than a mutable tag; use
`uses: owner/action@<full-40-char-sha> # vX.Y.Z` and enable Dependabot for the
`github-actions` ecosystem. Floating references such as `fluxcd/flux2/action@main` and
major-version references such as `github/codeql-action/upload-sarif@v4` are mutable and
should be replaced with full SHAs.

Branch-based main GitOps: `GitRepository.spec.ref.branch: main` declaratively; remove
`on.push.tags: ['v*']` deployment triggers, `--tag-semver`, `FLUX_GIT_TAG` semantics, and
documentation claiming tags deploy. Protect main (require pull request, required status
checks, block direct pushes, prevent force-push/delete; skip mandatory independent
approval for a single-maintainer homelab). CI interaction: PR → validation → review →
merge main → Flux observes new commit → Flux reconciles.

## References

- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- https://fluxcd.io/flux/components/source/gitrepositories/
- https://fluxcd.io/flux/cmd/flux_check/
- https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
- https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github
- https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#permissions
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://tailscale.com/kb/1276/tailscale-github-action

## Capture Notes

Consolidated from deep-research job 1043eccbd1a546509cf30a9c22c11988 (Phase 4, card 2/2).
The research used the supplied step list + accessible README; the workflow file itself was
not independently retrieved. The README currently documents semver-tag deployment, so
moving to branch-main is an intentional release-policy change.
