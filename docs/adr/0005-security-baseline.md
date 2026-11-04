# ADR 0005: Security baseline (OWASP and Essential Eight)

**Status:** Proposed · 2026-11-04 · Target levels to be confirmed by CC Tech

## Context

Brivo will hold participant and health information for Brave Connections. We need a named
standard for how the application is built and a named standard for how the accounts, cloud
and pipeline around it are run, so that security work can be planned, checked and evidenced.

## Decision

- **Application:** build to **OWASP ASVS Level 2** (Application Security Verification
  Standard), use the **OWASP Top 10** and **OWASP API Security Top 10** as review checklists,
  and scan code with Semgrep's OWASP Top 10 rules in CI.
- **Accounts, cloud and pipeline:** meet the **ACSC Essential Eight at Maturity Level 2**
  for the parts this project controls (patching, MFA, admin privileges, application control
  in images and CI, backups). Device controls (Office macros, workstation application
  control, browser hardening) belong to CC Tech's IT.
- **Patching** follows Essential Eight timeframes for internet-facing services: within
  **48 hours** when a vulnerability is critical or a working exploit exists, otherwise within
  **two weeks**.
- **Supply chain:** GitHub Actions and CI container images are pinned to commit SHAs or image
  digests; Dependabot waits a 7-day cooldown before proposing new releases.
- **Least privilege by default:** the API connects as `brivo_app` (cannot bypass Row-Level
  Security); only migrations use `brivo_owner`; secrets live in GitHub or AWS secret stores,
  never in the repository.
- **Login (not built yet)** must meet ASVS Level 2 with **MFA** before any real user signs in.
- Each control, its status and where it is implemented are tracked in
  [docs/security/checklist.md](../security/checklist.md). [SECURITY.md](../../SECURITY.md)
  holds the reporting policy and the team's day-to-day rules.

## Consequences

Security work has a clear target and an evidence trail for CC Tech or an assessor. Some
controls depend on account-level changes outside the code (a GitHub organisation with
required 2FA, a plan with branch protection), which CC Tech must make. Pinned actions and
images need Dependabot or a periodic manual bump to stay current.

## Open

- CC Tech to confirm the Essential Eight maturity level (ML2 proposed) and ASVS level (L2
  proposed), and whether an existing Essential Eight programme should be aligned with.
- Security contact for vulnerability reports (see SECURITY.md).
