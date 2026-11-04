# Security policy

Brivo Clinical System will hold participant and health information for Brave Connections.
This file says how to report a security problem and the rules everyone working on the code
follows. The security baseline is [ADR 0005](docs/adr/0005-security-baseline.md); progress is
tracked in [docs/security/checklist.md](docs/security/checklist.md).

## Reporting a vulnerability

**Do not open a GitHub issue, pull request or chat thread about it.** Report privately to:

- **Security contact:** _to be confirmed by CC Tech_ (email or password-manager-shared channel)

Include what you found, where (file, URL or endpoint), how to reproduce it, and what an
attacker could do. **Never include real participant data**, passwords, keys or tokens; describe
them instead.

What happens next:

| Step | Target |
|---|---|
| Acknowledge the report | 2 business days |
| Assess severity and agree a fix | 5 business days |
| Fix critical issues, or any issue with a working exploit | 48 hours |
| Fix other issues | 2 weeks, or the next planned release if lower risk |

If a secret was exposed, it is **rotated first**, then investigated.

## Supported versions

Only the current `main` branch is supported. There are no released versions yet.

## Rules for everyone working on Brivo

**Data**
- Only made-up data in development, tests, Supabase, screenshots and tickets. Never copy real
  participant or health data out of production.
- No participant or health data in logs, error messages, analytics or test fixtures.

**Secrets**
- Secrets live in a password manager and in GitHub or AWS secret stores, nowhere else: not in
  the repository, `.env` files you commit, chat, email, screenshots or shell history.
- `.env` files stay local and are gitignored. Check `git status` before every commit.
- A leaked secret is rotated immediately, even if the leak looks harmless.

**Accounts**
- Turn on 2FA for GitHub, Supabase, Docker and AWS. Use your own account; never share logins.
- Use the least privilege that works: the API runs as `brivo_app`, migrations as
  `brivo_owner`, and the Supabase admin login is for one-off setup only.

**Code and changes**
- All changes go through a pull request into `dev`, then `main`, with CI and security scans
  passing. Fix findings rather than suppressing them; any suppression needs a reason in the
  code and a reviewer's agreement.
- Database changes are new numbered Alembic migrations. Review the SQL in the PR's
  "Migration preview" before merging. Nothing is changed by hand in the Supabase or RDS
  consoles.
- New tenant tables have `org_id` and Row-Level Security (`platform.enable_tenant_rls`).
- Build to OWASP ASVS Level 2. Validate all input, authorise every object access, and use
  SQLAlchemy or bound parameters for SQL, never string formatting.
- GitHub Actions and CI images are pinned to commit SHAs or digests. When adding one, pin it
  the same way.

**Dependencies**
- Dependabot proposes updates after a 7-day cooldown; review and merge them promptly within
  the timeframes above. Add a new dependency only when needed, and check who publishes it.

## Scope

In scope: this repository, its CI/CD workflows, and the Brivo databases and services built
from it. Out of scope: third-party services themselves (GitHub, Supabase, AWS), which have
their own reporting programmes, and CC Tech's devices and office IT.
