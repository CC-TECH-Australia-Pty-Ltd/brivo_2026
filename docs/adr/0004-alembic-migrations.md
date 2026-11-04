# ADR 0004: Alembic migrations

**Status:** Accepted · 2026-11-03 · Supersedes the migrations part of [ADR 0003](0003-database-hosting-and-migrations.md)

## Decision

- Schema changes are **Alembic** revisions in `backend/migrations/versions`, applied with
  `alembic upgrade head` (`make migrate`) as `brave_owner`. They run against Supabase while it
  is the test database (months 1-2) and against Amazon RDS from month 3.
- Revisions are **numbered** `0001`, `0002`, ... in a single line (`make migration name="..."`).
  CI fails if two revisions share a parent.
- Alembic's version table lives in the `migrations` schema, so `public` stays empty.
- Autogenerate compares only `platform`, `content`, `clinical` and `media`, never Supabase's
  own schemas. Its output is always reviewed and edited by hand.
- **Forward-only:** `downgrade()` raises; to undo something, add a new revision. Applied
  revisions are never edited.
- Each run takes a PostgreSQL advisory lock, so two deploys cannot migrate at once.

Everything else in ADR 0003 (schemas, roles, Row-Level Security, UUIDv7, Supabase only as a
plain PostgreSQL host) still applies.

## Consequences

The team uses a standard, well-documented tool with autogenerate from SQLAlchemy models.
Unlike the previous runner, Alembic does not checksum applied files, so "never edit an applied
migration" is enforced by review (PR template) rather than by the tool.
