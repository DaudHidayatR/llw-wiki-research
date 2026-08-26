---
schema_version: 2
id: "source-deep-research-kind-cni"
type: "source"
title: "Deep Research — Choosing a NetworkPolicy-Enforcing CNI for kind"
Author: "Hermes Deep Research"
Reference: "deep-research-job-0c8b3874"
SourceType: "web"
ContentType:
  - "markdown"
Published: "2026-08-26"
Captured: "2026-08-26"
Created: "2026-08-26"
Processed: true
tags:
  - "source"
ContentHash: "sha256:7dabd3935e6a6f17af34944489367768ec0815a43f8cb35c113a3b29fa591aa8"
---

# Deep Research — Choosing a NetworkPolicy-Enforcing CNI for kind

## Normalized Content

### Executive recommendation

For a single-control-plane-node kind cluster used as a DevSecOps homelab: use Cilium as
the pragmatic default when the lab is meant to exercise real Kubernetes NetworkPolicy,
security identities, policy observability, or eventual L7 controls. Keep the initial
Cilium install deliberately small: retain kube-proxy, one operator replica, normal
tunneled datapath, Hubble/encryption/Cluster Mesh/BGP/service mesh/ingress disabled.
Choose Calico when the goal is conventional NetworkPolicy with a familiar iptables/
nftables model or when Calico matches the target production environment. In either case
configure kind with `disableDefaultCNI: true`. A successfully created NetworkPolicy
object is NOT proof of enforcement — Kubernetes explicitly states the resource has no
effect without an implementing plugin. Verify with fresh TCP connections between two
ordinary Pods before/after a namespace-wide ingress+egress deny-all. PSA and Kyverno are
complementary admission controls but never enforce runtime Pod-to-Pod traffic. For the
smallest cluster where network isolation is not being tested, retaining kindnetd is
reasonable — then either remove NetworkPolicy resources or label the environment
declarative-only/non-enforcing.

Research limitation: the official-documentation research produced substantially more
current Cilium/kind material than Calico; the Calico branch timed out. Calico specifics
must be confirmed against the pinned release's docs (docs.tigera.io). No controlled
Cilium-vs-Calico memory benchmark exists for one-node kind; footprint statements are
qualitative — measure with `kubectl top pods -n kube-system` / `docker stats`.

### What kind requires from a replacement CNI

Default kind installs kindnetd. To replace: `networking: disableDefaultCNI: true` in the
kind config, `kind create cluster --config kind.yaml`. After creation and before the
replacement CNI is healthy, the node may be NotReady, CoreDNS/Pods Pending, containerd
may report no CNI config — expected bootstrap gap. Keep kube-proxy for the minimal config
(kube-proxy-free Cilium requires cluster created without kube-proxy,
kubeProxyReplacement, API server host/port, eBPF/kernel capabilities, extra validation).
Flux bootstrap problem: a fresh kind cluster with default CNI disabled cannot generally
rely on in-cluster Flux controllers to install the first CNI (controllers are Pods and
need CNI). Sequence: create kind → bootstrap the CNI directly (pinned Helm chart/
manifest) → wait ready → install Flux → commit an equivalent HelmRelease for Flux to
adopt/maintain → confirm ready + no unintended drift. This is a bootstrap exception, not
ongoing imperative administration. Alternative (bootstrap Flux with kindnetd then replace
CNI underneath running Pods) is more disruptive.

### Cilium on kind

Installs as one agent per node + operator + CRDs; optional Hubble Relay/UI, Envoy,
Cluster Mesh, SPIRE, ingress. One-node topology: one agent Pod + operator; reduce
operator to one replica. Install from signed OCI chart
(`oci://quay.io/cilium/charts/cilium`) or Helm repo; pin versions. Minimal config:
`operator.replicas: 1`, `kubeProxyReplacement: false`, `hubble.enabled/relay.enabled/
ui.enabled: false`, `encryption.enabled: false`; optional explicit
`routingMode: tunnel, tunnelProtocol: vxlan`. Validate every key against the pinned
release's Helm reference; do not copy values blindly across releases. Features omitted
from minimal: kube-proxy replacement, Hubble, WireGuard, Cluster Mesh, BGP, service mesh,
ingress, L7, XDP, Maglev, bandwidth manager. Same-node encryption is poor value
(WireGuard does not encrypt same-node traffic). Flux ownership: OCIRepository +
HelmRelease with `install.crds: Create`, `upgrade.crds: CreateReplace` (verify against
Cilium upgrade notes per version). Cilium provides real NetworkPolicy ingress+egress
enforcement plus label-derived security identities, CiliumNetworkPolicy, DNS/HTTP L7,
eBPF drop diagnostics, Hubble, optional kube-proxy replacement, host policies.
Troubleshooting: `cilium status`, `cilium connectivity test`, `cilium-dbg endpoint list/
get/monitor`; portions of connectivity test needing multiple nodes may be Pending on a
single node. Footprint: heavier than kindnetd (privileged node agent + operator + CRDs +
eBPF maps); BPF map capacities are limits/defaults, not proof of immediate max memory.
Maintenance: moderate — kernel/Cilium/Kubernetes/chart compatibility, CRD upgrade
attention, eBPF/cgroup host issues; strong first-party diagnostics. For disposable kind,
recreate rather than in-place recovery; pin node image + chart.

### Calico on kind

Preferred install: Tigera operator via Helm chart, then Calico installation custom
resources. Typical deployment: Tigera operator, calico-node DaemonSet, Calico
controllers, CNI config/binaries, CRDs/installation resources, possibly Typha. For
one-node, confirm whether the pinned release enables Typha/extra replicas; disable/reduce
scaling components. kind also needs `disableDefaultCNI: true`; follow the official Calico
kind guide for Pod CIDR + parameters. Minimal design: Tigera operator Helm chart, one
replica where supported, no enterprise/observability add-ons, one IPv4 pool matching
cluster design, one encapsulation mode (VXLAN or IP-in-IP) chosen deliberately, not both.
Representative Installation CR: `ipPools: [{cidr: 10.244.0.0/16, encapsulation: VXLAN,
natOutgoing: Enabled, nodeSelector: all()}]` — confirm enum values against pinned docs.
IP-in-IP is a Calico networking capability (IP-over-IP encapsulation), not a Kubernetes
NetworkPolicy feature; on a one-node cluster all Pods are same-node so IP-in-IP has
little practical benefit — VXLAN is easier to reason about in containerized environments;
for real overlay learning add a worker node. Flux layout is naturally two-stage: install
Tigera operator + CRDs, then apply Installation after CRD exists (separate Kustomizations
with dependsOn, or the shortest supported path). Calico provides real ingress+egress
enforcement plus Calico-specific policy resources, global policy, ordered tiers, host
endpoint policy, policy logging; standard NetworkPolicy stays additive (no explicit deny).
Footprint: heavier than kindnetd; relative ranking vs Cilium is unverified — measure.
Maintenance: moderate — operator/CRD compatibility, IP pools/encapsulation/NAT/
autodetection concepts, iptables/nftables debugging, operator+Installation ordering.

### Direct comparison

| Area | Cilium | Calico |
|---|---|---|
| kind replacement | disableDefaultCNI | disableDefaultCNI |
| First bootstrap | Direct Helm first; Flux can't start without CNI | Same constraint |
| Base node component | Cilium agent DaemonSet | calico-node DaemonSet |
| Base control component | Cilium operator | Tigera operator + controllers |
| Standard NetworkPolicy | Real ingress+egress | Real ingress+egress |
| Differentiation | eBPF, identities, Hubble, optional L7, kube-proxy replacement | Conventional model, global/ordered policy, routing/overlays |
| L7 | Via Cilium policy/proxy | Not the main reason to choose Calico |
| Overlays | VXLAN/Geneve or direct | VXLAN, IP-in-IP, routed |
| Encryption in one node | Low (same-node not encrypted) | Similarly low |
| Troubleshooting | cilium status, endpoint state, eBPF drops, Hubble | Routes, endpoints, controllers, packet-filter rules |
| Complexity ceiling | Higher (eBPF/observability/L7) | Higher (BGP/IP pools/IPIP/tiers) |
| Best fit | Security experimentation, observability/L7 future | Portable L3/L4, conventional networking |

No version-independent "which is lighter" answer exists; measure the exact pinned
configurations. For only standard ingress/egress NetworkPolicy, both are fine; Calico's
policy model feels more conventional, Cilium's small Helm config is straightforward if
optional features are avoided; Calico's operator+CR lifecycle can be more involved in
GitOps.

### End-to-end NetworkPolicy verification

Kubernetes starts with Pods non-isolated; a Pod becomes isolated when a matching policy
includes that direction; policies are additive; Pod-to-Pod requires source egress AND
destination ingress both to allow. Test must prove: traffic worked before policy; fresh
direct TCP connections fail after deny-all; failure in both directions; recovery after
deleting policy; ordinary Pods only (not hostNetwork/loopback/host-to-Pod). Do NOT use
ping as primary proof (ICMP/ARP implementation-dependent). Deny-all:
`podSelector: {}, policyTypes: [Ingress, Egress]` with no allow rules. Default-deny egress
also blocks DNS — a failed name lookup alone does not prove direct Pod-IP TCP blocked;
connect directly to destination Pod IP. Runnable script: create ns, run two nginx Pods,
wait ready, capture Pod IPs, positive-control wget both directions, apply deny-all,
sleep ~5s, verify both directions now FAIL (exit non-zero), delete policy, sleep, verify
recovery. Stronger directional test: deny-all + only source-egress allow (still blocked),
only destination-ingress allow (still blocked), both allows (works). Cilium diagnostics
while denied: cilium status, endpoint list, monitor. Calico: node/operator readiness,
endpoint state, routes, packet-filter state, logs. Single-node caveat: validates same-node
enforcement only; add a worker node for cross-node/overlay/encryption paths.

### Alternative: retain kindnetd

Declarative-only NetworkPolicies — acceptable when manifests are shared with a
policy-enforcing production cluster, the lab validates schema/GitOps rendering, policies
document intended communication, or a CNI migration is planned. Must label the environment
(`homelab.example.com/network-policy-mode: declarative-only`), state in README/security
reviews that Pod traffic is unrestricted at runtime, and run a negative control (apply
deny-all and confirm traffic STILL succeeds) to prevent false claims. OR remove the
policies — a visibly absent control beats a security object that appears active but does
nothing. PSA and Kyverno enforce admission-time workload-specification controls
(privileged containers, host namespaces, capabilities, escalation, root, seccomp, unsafe
volumes; require security contexts, reject hostNetwork, require NetworkPolicy manifest,
validate labels/images) but never implement the NetworkPolicy data plane — they cannot
turn kindnetd into a policy-enforcing CNI. Defense-in-depth lab: PSA/Kyverno for workload
spec + Cilium/Calico for runtime isolation + end-to-end connectivity tests.

### Final decision

Recommended default: minimal Cilium (genuine standard NetworkPolicy, small usable base,
strong diagnostics, path to identity/L7, optional Hubble, eBPF exposure relevant to
security engineering). Keep first version boring (operator 1 replica, no kube-proxy
replacement, no Hubble, no encryption); add Hubble only when flow observability is used,
L7 only for a concrete exercise. Choose Calico when production/coursework uses Calico,
the goal is IP pools/routed networking/VXLAN/IPIP/BGP/tiers, conventional L3/L4
enforcement suffices, or Cilium features would be unused — use ≥2 kind nodes for
meaningful IP-in-IP/overlay testing. Keep kindnetd when host resources are tight, no
runtime network-isolation claim is made, or the lab focuses on admission policy/workload
hardening/deployments/GitOps — mark policies declarative-only or remove them; do not
count them as a security control.

## References

- https://kind.sigs.k8s.io/docs/user/configuration
- https://kind.sigs.k8s.io/docs/user/known-issues
- https://docs.cilium.io/en/stable/installation/k8s-install-helm
- https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free
- https://docs.cilium.io/en/stable/helm-reference
- https://kubernetes.io/docs/concepts/services-networking/network-policies
- https://docs.cilium.io/en/stable/operations/troubleshooting
- https://docs.cilium.io/en/stable/security/network/encryption-wireguard
- https://fluxcd.io/flux/components/helm/api/v2
- https://docs.tigera.io/calico/latest/getting-started/kubernetes/kind
- https://docs.tigera.io/calico/latest/getting-started/kubernetes/helm
- https://kubernetes.io/docs/concepts/security/pod-security-standards
- https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels

## Capture Notes

Deep-research job 0c8b387463894878ad0045ae136f93b5 (2026-08-26, model gpt-5.6-sol).
Calico branch timed out — Calico specifics need pin verification against docs.tigera.io.
No controlled one-node memory benchmark exists; footprint claims are qualitative.
Kindnetd does not enforce NetworkPolicy (confirmed repo-verified in Phase 6).