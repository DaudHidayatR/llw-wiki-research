---
schema_version: 2
id: "source-calico-kind-helm-primary"
type: "source"
title: "Calico on kind — Primary-Source Install Facts (OSS 3.32.1)"
Author: "Hermes Deep Research"
Reference: "docs-tigera-io-2026-08-26"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-26"
Captured: "2026-08-26"
Created: "2026-08-26"
Processed: true
tags:
  - "source"
ContentHash: "sha256:80b0f4d58363ea7b422c9363a61e7dbcfe54f42d9a2e6757b17b001df5e06dd5"
---

# Calico on kind — Primary-Source Install Facts (OSS 3.32.1)

## Normalized Content

Verified 2026-08-26 from docs.tigera.io (Calico Open Source 3.32 "latest") and the
projectcalico GitHub releases API. Closes the earlier Calico research-branch timeout.

### Versions

- Calico Open Source latest: **3.32.1** (docs.tigera.io shows 3.32; GitHub latest
  release tag v3.32.1). The Tigera operator Helm chart version matches v3.32.1.

### kind prerequisites

- Docker + kind (do not create the cluster yet) + kubectl.
- kind's default CNI is kindnetd (simple CNI plugins + netlink routes); it must be
  disabled to use the Calico CNI.
- kind config (multi-node example; a single control-plane node works for a homelab):
  `kind: Cluster`, `apiVersion: kind.x-k8s.io/v1alpha4`, `nodes: [{role:
  control-plane}]`, `networking: {disableDefaultCNI: true, podSubnet: 192.168.0.0/16}`.
  The `podSubnet` field is significant — Calico must match the Pod CIDR.
- Create with `kind create cluster --config values.yaml --name dev`.
- After creation, nodes are NotReady and Pods Pending until Calico installs (expected
  bootstrap gap).

### Install — manifest path (kind tutorial default)

1. `kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.32.1/manifests/v1_crd_projectcalico_org.yaml`
2. `kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.32.1/manifests/tigera-operator.yaml`
3. Create the Installation custom resource (`custom-resources.yaml` — set the
   pod-network-cidr to match the kind podSubnet).
4. `kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.32.1/manifests/calico.yaml`
   (large CRD bundle — prefer `kubectl create`/`replace` over `apply` if request limits hit).
5. Verify: `watch kubectl get pods -l k8s-app=calico-node -A` → all Running.

### Install — Helm path

1. `helm repo add projectcalico https://docs.tigera.io/calico/charts`
2. Install CRDs: `helm template calico-crds projectcalico/crd.projectcalico.org.v1 --version v3.32.1 | kubectl apply --server-side -f -`
3. `kubectl create namespace tigera-operator`
4. `helm install calico projectcalico/tigera-operator --version v3.32.1 --namespace tigera-operator`
   (customize with a values.yaml for EKS/GKE/AKS/MKE or TLS; e.g.
   `installation: {kubernetesProvider: EKS}` or AKS example with
   `cni.type: Calico`, `calicoNetwork: {bgp: Disabled, ipPools: [{cidr:
   10.244.0.0/16, encapsulation: VXLAN}]}`).
5. Verify: `watch kubectl get pods -n calico-system` → Running. Tigera operator
   installs Calico resources in `calico-system` (manifest path uses kube-system).

### Single-node homelab notes

- Policy: Calico (Policy), IPAM (Calico), CNI (Calico), Overlay (VXLAN), Routing
  (Calico), Datastore (Kubernetes).
- Real Kubernetes NetworkPolicy ingress+egress enforcement.
- IP-in-IP has little practical value on a one-node cluster (no cross-node path);
  VXLAN is the sensible overlay; a multi-node kind cluster is needed to exercise
  IP-in-IP or overlay transport meaningfully.
- Flux integration: Tigera operator HelmRelease (install.crds Create) + the
  Installation CR applied after the operator CRDs exist (two-stage; separate
  Kustomizations with dependsOn). First install cannot depend on Flux (no CNI yet) —
  bootstrap directly, then hand ownership to Flux.

## References

- https://docs.tigera.io/calico/latest/getting-started/kubernetes/kind
- https://docs.tigera.io/calico/latest/getting-started/kubernetes/helm
- https://docs.tigera.io/calico/latest/reference/installation/api
- https://docs.tigera.io/calico/latest/reference/installation/helm_customization
- https://github.com/projectcalico/calico/releases (v3.32.1)

## Capture Notes

Fetched 2026-08-26. The Helm chart index (docs.tigera.io/calico/charts/index.yaml)
did not respond to curl; version confirmed via the GitHub releases API (v3.32.1) and
the docs' inline `--version v3.32.1` examples.