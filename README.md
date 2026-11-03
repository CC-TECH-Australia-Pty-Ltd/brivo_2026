# Brave Clinical System

Clinical assessment platform for Positive Behaviour Support, built by CC Tech Australia for
Brave Connections. Stage 1 is the assessment foundation: participant record, assessment
planner, content library, form engine, scoring, review and evidence items.

| Part | Technology | Folder |
|---|---|---|
| API and worker | Python 3.12+, FastAPI, SQLAlchemy 2, uv | `backend/` |
| Web app | React, TypeScript, Vite, Tailwind CSS | `frontend/` |
| Database | PostgreSQL 16, plain SQL migrations | `db/` |
| Infrastructure | AWS Sydney from month 3 (Terraform or CDK, TBC) | `infra/` |
| Decisions | Architecture decision records | `docs/adr/` |

**Database hosting:** Supabase (Sydney) in months 1–2 with **test data only**, then Amazon RDS
for PostgreSQL 16 from month 3. See [ADR 0003](docs/adr/0003-database-hosting-and-migrations.md).

## Getting started (macOS)

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/),
[uv](https://docs.astral.sh/uv/) (`brew install uv`) and Node.js 22 (`brew install node@22`).

```bash
make setup     # install dependencies, create backend/.env
make db-up     # start PostgreSQL 16 in Docker (creates brave_owner and brave_app roles)
make migrate   # apply db/migrations
make api       # API on http://localhost:8000  (docs at /docs)
make web       # in a second terminal: web app on http://localhost:5173
```

The web app's home page shows whether the API and database are connected.
Run `make help` for every command and `make check` before opening a pull request.

## Project layout

```
backend/src/brave/
  core/          settings, database sessions, organisation context, IDs
  modules/       participants, assessments, content_library, scoring,
                 evidence, audit, notifications
  worker/        background jobs (reports, messages, rescoring, audit export)
  migrate.py     SQL migration runner
db/
  bootstrap-roles.sql   run once per environment
  migrations/           0001_baseline.sql, 0002_..., applied in order
frontend/src/    React app
```

Module rules (checked in CI by `lint-imports`):
- `scoring` is pure: no database, web framework or network access.
- Feature modules don't import each other directly.
- `core` never imports from `modules`.

## Database rules

- **Four schemas, none public:** `platform`, `content`, `clinical`, `media`.
- **Every tenant table** has `org_id` and calls `SELECT platform.enable_tenant_rls('schema.table');`
  in its migration. The API opens each transaction with `org_session(org_id)`, and the
  `brave_app` role cannot bypass Row-Level Security.
- **Migrations are forward-only.** Never edit a file that has been applied anywhere: add a new
  numbered file. The runner refuses to continue if an applied file has changed.
- **IDs are UUIDv7**, generated in the application (`brave.core.ids.new_id`).
- **Supabase is only a PostgreSQL host.** Don't use Supabase Auth, Storage, Edge Functions,
  its auto-generated API, `auth.uid()`, or make changes in its dashboard.

### Connecting to Supabase (months 1–2)

1. Create the project in the **Sydney** region and check it runs **PostgreSQL 16**.
2. Using the admin connection string, run once:
   `psql "$ADMIN_URL" -v owner_password=... -v app_password=... -f db/bootstrap-roles.sql`
3. Set `BRAVE_DATABASE_URL` (as `brave_app`) and `BRAVE_MIGRATION_DATABASE_URL` (as
   `brave_owner`) using the **direct or session** connection, not the transaction pooler.
4. `make migrate`.

Only made-up data ever goes into Supabase.

## Continuous integration

Every pull request runs:
- **CI:** backend lint, format, types, module boundaries, migrations on an empty PostgreSQL 16,
  tests (including tenant isolation); frontend lint and build.
- **Security:** secret scanning (gitleaks), code scanning (Semgrep), dependency scanning (Trivy).
- **Dependabot** opens weekly update pull requests.

Deployment workflows will be added once hosting for months 1–2 is confirmed.
