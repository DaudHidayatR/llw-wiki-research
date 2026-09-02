# YAGNI — You Aren't Gonna Need It

> Wiki/Concepts/principle-yagni.md · part of the [engineering principles series](../Projects/homelab-devsecops.md)
> Code findings verified against `DaudHidayatR/homelab-devsecops` @ `e863f90` (re-grepped 2026-09-02).

## TL;DR

Build what is needed now; defer what is not. Unused code is not free — it is read, linted, tested, documented, and *trusted* (dangerously) by future maintainers. In this repo, YAGNI violations are **dead helpers with zero callers** and **orphaned configuration/manifests left behind after a redesign**.

## Origin & canonical references

**Facts (documented):**
- YAGNI arose from **Extreme Programming** (Kent Beck, Chrysler C3 project, mid-1990s): "Always implement things when you actually need them, never when you just foresee that you need them." ([Wikipedia: You aren't gonna need it](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it); [Wikipedia: Extreme programming](https://en.wikipedia.org/wiki/Extreme_programming))
- Ron Jeffries (XP coach on C3, co-author *Extreme Programming Installed*, 2000) popularized the phrase on the C2 wiki; the canonical C2 page frames it as the counter to speculative generality ([c2.com: YouArentGonnaNeedIt](http://c2.com/cgi/wiki?YouArentGonnaNeedIt)).
- XP pairs YAGNI with "Do the Simplest Thing That Could Possibly Work" and refactoring: you add capability *when* the need appears, and refactor to admit it then.

**Inference:** YAGNI in declarative/infra repos maps to "no manifest, key, or flag without a consumer" — the consumer is the proof of need.

## Core rules

1. No abstraction, wrapper, or config key without at least one real caller/consumer.
2. When a redesign removes the consumer, remove the artifact in the same change.
3. Growth is additive-on-demand, not speculative-on-foresight.
4. "We might need it later" is a TODO comment, not code.

## Code smells / anti-patterns

- Wrappers with zero callers ("just in case" API surface).
- Config keys declared but read by nothing (grep finds no consumer).
- Orphaned manifests surviving the subsystem that used them.
- Flags/options that everything ignores.

## Application to homelab-devsecops (verified @ e863f90)

| # | Finding | Location | Evidence |
|---|---------|----------|----------|
| Y1 | `k8s::annotate_service` — thin kubectl wrapper with **zero callers** repo-wide (grep over `scripts/` excluding the definition: 0 hits). | `scripts/lib/kubernetes.sh:~60–63` | re-grepped 2026-09-02 |
| Y2 | `common::confirm` and `json::escape` — unused outside tests or entirely unused; speculative API surface in `common.sh`. | `scripts/lib/common.sh` | grep |
| Y3 | Dead config keys: `HEADLAMP_VERSION`, `SAMPLE_APP_IMAGE`, `TAILSCALE_OPERATOR_VERSION` declared in `config.env.example` but consumed by nothing — the manifests pin their own digests (which is correct); the keys are leftovers of a previous pinning scheme. | `config.env.example` | grep over scripts/, Makefile, kubernetes/ |
| Y4 | Orphaned manifest: `tailscale/serve-watcher.yaml` (~69 lines of SA/RBAC) — the only reference to "serve-watcher" in the repo is the file itself; the Serve watcher was removed in the redesign (board cards t_09e09e/t_09e1b97e intent). | `tailscale/serve-watcher.yaml` | repo-wide grep: single hit |
| Y5 | `make openbao-create-approle` carries an env-var usage block for a flow the redesign simplified away. | `Makefile` | grep |
| Y6 | **Positive:** `scripts/lib/tailscale.sh` explicitly documents that the shell layer does *not* apply upstream manifests (no speculative install path); the test suite asserts only real contracts. | `scripts/lib/tailscale.sh` | read |

**Proposals (PROPOSAL):** delete Y1/Y2 wrappers, Y3 keys, Y4 manifest, Y5 block — each is a one-file (or few-file) removal PR. Removals overlap with the P1/P2 simplification cards already on the board (t_b30f4c98, t_88807336); this doc is the principle-level justification for them.

## When to break the rule

- Public interfaces consumed by parties you cannot see (none here — all consumers are in-repo, which is why Y1–Y5 are safely deletable).
- Cheap, reversible groundwork with explicit expiry dates (rarely worth it even then).

## Review checklist

- [ ] For every helper: `grep -rn "<name>" --exclude=lib` ≥ 1 caller?
- [ ] For every config key: a consumer outside `config.env.example`?
- [ ] For every manifest: referenced by a kustomization, workflow, or doc?
- [ ] After any removal: did its config/doc/manifest siblings get removed too?
