-- Run ONCE per environment, as the database superuser/admin, before the first migration.
-- Creates the two roles every environment uses (local, CI, Supabase, RDS):
--   brave_owner  owns the four schemas and runs migrations
--   brave_app    used by the API and worker; cannot bypass Row-Level Security
--
-- Local/CI:  psql -f db/bootstrap-roles.sql   (uses the default dev passwords)
-- Supabase/RDS: pass real passwords, e.g.
--   psql "$ADMIN_URL" -v owner_password="..." -v app_password="..." -f db/bootstrap-roles.sql
\set ON_ERROR_STOP on
\if :{?owner_password}
\else
  \set owner_password brave_owner
\endif
\if :{?app_password}
\else
  \set app_password brave_app
\endif

CREATE ROLE brave_owner LOGIN PASSWORD :'owner_password';
CREATE ROLE brave_app LOGIN PASSWORD :'app_password' NOSUPERUSER NOBYPASSRLS;

-- The owner may create the platform, content, clinical and media schemas.
SELECT format('GRANT CREATE, CONNECT ON DATABASE %I TO brave_owner', current_database()) \gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO brave_app', current_database()) \gexec
