# Security checklist

Where each control in [ADR 0005](../adr/0005-security-baseline.md) is implemented, and what is
still to do. Update this file in the same pull request that changes a control.

**Status:** ✅ done · 🟡 partly done · ⏳ planned · 🏢 CC Tech (outside this repository)

## Pipeline and supply chain

| Control | Status | Evidence / where |
|---|---|---|
| CI on every pull request: lint, types, module boundaries, tests | ✅ | `.github/workflows/ci.yml` |
| Migrations tested on an empty PostgreSQL 17 in CI | ✅ | `ci.yml` → "Migrations on an empty database" |
| Only one migration head allowed | ✅ | `ci.yml` → "Single migration head" |
| SQL of new migrations shown on the PR before merge | ✅ | `ci.yml` → "Migration preview" |
| Secret scanning of full git history (gitleaks CLI, values redacted; fails if nothing was scanned) | ✅ | `.github/workflows/security.yml` → `secrets` |
| Code scanning incl. OWASP Top 10 rules (Semgrep) | ✅ | `security.yml` → `code` (`p/owasp-top-ten`) |
| Dependency and config scanning (Trivy), weekly as well as per PR | ✅ | `security.yml` → `dependencies` |
| Dependency updates with a 7-day cooldown | ✅ | `.github/dependabot.yml` |
| GitHub Actions pinned to commit SHAs | ✅ | all workflows (`uses: …@<sha> # vX`) |
| CI container images pinned by digest | ✅ | `security.yml` Semgrep and gitleaks images; bump by hand, Dependabot does not cover them |
| Workflow inputs passed via `env:`, not inlined into scripts | ✅ | `ci.yml` "Migration preview" (`BASE_REF`) |
| Supabase migrations need a person to approve | ✅ | `.github/workflows/migrate.yml` (manual run on `main`, typed `migrate`) |
| Migration secret only usable by the migrate job | ⏳ | Needs GitHub environments (paid plan / organisation) |
| Branch protection on `main`: PR + passing CI required | 🏢 | Needs organisation and plan |
| CODEOWNERS enforced for `db/`, `backend/src/brivo/core/`, `.github/` | ⏳ | `.github/CODEOWNERS` (commented out until branch protection) |
| Container images: non-root, minimal, scanned, SBOM | ⏳ | With the Dockerfiles |
| Dynamic scan of the running app (OWASP ZAP baseline) | ⏳ | With the Dockerfiles |

## Application (OWASP ASVS Level 2)

| Area | Status | Evidence / where |
|---|---|---|
| Tenant isolation: Row-Level Security on every tenant table | ✅ | ADR 0003; `platform.enable_tenant_rls`; `backend/tests/test_tenant_isolation.py` |
| API role cannot bypass RLS or change policies | ✅ | `db/bootstrap-roles.sql` (`NOBYPASSRLS`); tenant isolation tests |
| SQL built with bound parameters / SQLAlchemy, never string formatting | ✅ | Semgrep rules; code review |
| Input validation on every endpoint (Pydantic models) | 🟡 | Pattern in place; check as endpoints are added |
| Object-level authorisation (OWASP API #1) | 🟡 | RLS gives the base; add per-endpoint checks and tests |
| Authentication to ASVS L2 with MFA | ⏳ | **Must be done before any real user signs in** |
| Session management (secure cookies or tokens, expiry, revocation) | ⏳ | With authentication |
| Security headers (CSP, HSTS, X-Content-Type-Options, frame-ancestors) | ⏳ | Nginx now, CloudFront later |
| CORS limited to known origins | ✅ | `backend/src/brivo/core/config.py` (`cors_origins`) |
| No participant or health data in logs, errors, fixtures | 🟡 | Rule in PR template and SECURITY.md; add log redaction with logging |
| Encryption in transit (TLS) | 🟡 | Supabase `sslmode=require`; HTTPS with hosting |
| Encryption at rest | 🟡 | Supabase and RDS encrypt storage; confirm for RDS in month 3 |
| Audit log of access to clinical records | ⏳ | `brivo.modules.audit` (placeholder) |

## ACSC Essential Eight (target Maturity Level 2, to be confirmed)

| Strategy | Our part | Status | CC Tech part |
|---|---|---|---|
| Patch applications | Dependabot, weekly Trivy, 48 h / 2 week timeframes (SECURITY.md) | 🟡 timeframes need an owner | Staff apps 🏢 |
| Patch operating systems | Managed services (Supabase, RDS, Fargate); base images via Dependabot | 🟡 | Staff devices 🏢 |
| Multi-factor authentication | 2FA on each person's GitHub, Supabase, Docker, AWS; MFA in Brivo login | ⏳ | Enforce org-wide 🏢 |
| Restrict administrative privileges | `brivo_app` least privilege ✅; no shared logins; secrets per environment ⏳ | 🟡 | Repo in an organisation with roles 🏢 |
| Application control | Pinned actions and images ✅; minimal images ⏳ | 🟡 | Workstations 🏢 |
| Restrict Microsoft Office macros | Not applicable to this repository | — | 🏢 |
| User application hardening | Security headers / CSP in the web app ⏳ | ⏳ | Browsers on devices 🏢 |
| Regular backups | Supabase holds test data only; RDS backups, point-in-time recovery and restore tests in month 3 | ⏳ | Backup policy 🏢 |

## Accounts and secrets

| Item | Status | Notes |
|---|---|---|
| Repository owned by a GitHub organisation with required 2FA | 🏢 | Currently a personal account (`CC-Tech2026`) |
| `BRIVO_OWNER_PASSWORD` repository secret (migrate workflow builds the URL from it) | 🏢 | Needs a repo admin |
| Unused `SUPABASE_*` repository secrets removed (incl. `SUPABASE_SECRET_KEY`) | 🏢 | Nothing uses them |
| Database passwords only in the password manager and secret stores | ✅ | Never in the repo, chat or shell history |
