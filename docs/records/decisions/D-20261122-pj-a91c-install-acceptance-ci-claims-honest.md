---
id: D-20261122-pj-a91c
title: "Install acceptance: CI-automated gates; no platform claims without proof; Mac untested"
date: 2026-11-22T13:10:00Z
author: pj
decided-by: pj
status: accepted
mode: own
domain: scope & success criteria
task: T-20261122-pj-b94d
concepts: [release evidence, distribution acceptance]
supersedes: []
relates: [D-20261118-pj-fc4d, D-20261118-pj-de70, D-20261118-pj-d99f, D-20261118-pj-23ab, D-20261122-pj-b591]
ai: exposition+record
---
# Install acceptance: CI-automated gates; no platform claims without proof; Mac untested

## Context

Audit §6 and `D-fc4d` assumed **manual** installer testing per OS on clean hardware before announcement. pj (2026-11-22) has **no Mac** to test on, and local Windows/Linux machines are weak; relying on pj's laptop as the only gate does not scale and would block honest releases. Today CI (`desktop-release.yml`) builds each OS and runs a **bundled-engine** smoke (`/health`, mock `/site` local search); `docs/release-checklist.md` notes real Win/Mac UI was not exercised and v0.1.0 shipped with partial evidence.

pj: do not promise what cannot be tested; ship a **Mac installer** if CI builds it, but **say clearly it was not tested** on maintainer hardware; lean on **extensive automated CI** for everything that can be proven in automation; **no claims** without that proof.

## Framing

Same honesty pillar as `D-de70` and `D-b591`: green CI must mean something ran; README and release notes must not imply Mac (or any OS) is "supported" beyond what the acceptance job covers.

## Decision

### Claims vs artifacts

| Output | Rule |
|--------|------|
| **Installer artifact** (draft release / CI upload) | May exist for Linux, Windows, macOS when the build job is green |
| **"Supported" / "tested" wording** (README, site, release notes) | **Only** for a platform/OS leg that has a **passing install-acceptance CI job** defined below |
| **macOS** | Artifact allowed; **no claim** that macOS is tested or supported on real user hardware by pj; release/README must state **Mac installer not validated** (CI build + engine smoke on GitHub `macos-latest` does **not** count as "tested by maintainer") |

Linux and Windows: claims allowed only when that platform's **acceptance CI** is green on the release tag; pj's weak local machines are **not** the gate.

### Install acceptance CI (v1 bar)

- **One workflow** (extend `desktop-release.yml` or sibling `desktop-acceptance.yml`) running on **every** release tag and on demand.
- **Per matrix leg** (`linux`, `windows`, `macos`): after `deploy/build-desktop.sh`, run an **automated acceptance bundle** (no manual steps). Minimum v1 bundle **includes** existing engine smoke **plus** expanded checks added in build (examples: bundled binary starts; mock `/site` and mock `/deep-search` or health endpoints; failure if engine exits; optional headless UI smoke when feasible).
- Scenarios from the audit (interrupted download, offline, disk full, engine restart, old saved file) are **in scope for automation** where CI can simulate them; **no README promise** for a scenario until it is in the acceptance job **or** explicitly listed as unverified.
- Job **fails** (non-zero) if a required step fails — not `SKIP` as success (`D-b591` spirit).

### Manual testing

- **Not required** for platform claims in v1 when the acceptance CI leg passes.
- Optional manual notes in `docs/release-checklist.md` do not replace CI for claims.

### Offline / first-run

- `D-d99f` and `D-23ab` unchanged; offline acceptance tests join the CI bundle **when implemented**; until then, offline stays "not claimed beyond `D-d99f` text".

### Unsigned binaries

- `D-fc4d` wording for unsigned installers still applies when publishing; hashes when publishing remains deferred to release moment.

## Rationale

(Translated from pj's Spanish, 2026-11-22.) I do not have Mac hardware; my Windows and Linux are poor. Do not promise what we cannot test — Mac installer can exist with a clear "not tested" message. Make CI fairly extensive; all tests automatic; claim nothing that cannot be proven.

## Provenance

| Who | Contribution |
|-----|----------------|
| **pj** | Claims tied to proof; Mac honest non-claim; automation-first acceptance; no manual hardware gate for v1. |
| **ai** | Mapped gap vs `D-fc4d` manual checklist and current `desktop-release.yml` smoke; structured CI vs artifact vs claim. |

## Values

| Name | Value |
|------|-------|
| platform_claim_gate | install_acceptance_ci_leg_green |
| macos_maintainer_tested | no |
| macos_claim_supported | no |
| macos_installer_ship | yes_when_ci_build_green |
| macos_disclaimer_required | yes |
| linux_claim_supported | yes_when_linux_acceptance_ci_green |
| windows_claim_supported | yes_when_windows_acceptance_ci_green |
| manual_per_os_checklist_required | no_v1 |
| acceptance_ci_fail_on_missing_step | yes |
| audit_scenarios_claim_rule | in_ci_or_not_claimed |

## Expected behavior and validation

Wrong: README says "works on macOS" or "tested on Mac" without pj maintainer validation and without matching disclaimer.
Wrong: README says Linux/Windows supported while the acceptance job for that OS failed or was skipped.

## Consequences

- Narrow `D-fc4d` in practice: announcement per OS follows **CI acceptance**, not pj manual walkthrough; Mac gets **no support claim**.
- Implement expanded acceptance steps in CI; document job name and steps in `docs/release-checklist.md` or `docs/install-acceptance.md` when build lands.
- README/release copy pass before next public claim.