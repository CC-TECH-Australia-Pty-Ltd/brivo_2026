"""Alembic environment.

Connects as the schema owner (BRIVO_MIGRATION_DATABASE_URL, falling back to
BRIVO_DATABASE_URL) and applies all pending revisions in one transaction. The same
revisions run unchanged on local Postgres, Supabase (testing only) and Amazon RDS.

Alembic's own bookkeeping table lives in the ``migrations`` schema, so ``public``
stays empty. Only the four application schemas are compared by autogenerate, so
Supabase's built-in schemas (auth, storage, ...) are never touched.
"""

from alembic import context
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema

from brivo.core.config import get_settings
from brivo.core.db import Base

APP_SCHEMAS = {"platform", "content", "clinical", "media"}
VERSION_SCHEMA = "migrations"
LOCK_KEY = 7_424_100  # any constant; stops two deploys migrating at once

target_metadata = Base.metadata


def _url() -> str:
    settings = get_settings()
    return settings.migration_database_url or settings.database_url


def _include_name(name: str | None, type_: str, _parents: object) -> bool:
    if type_ == "schema":
        return name in APP_SCHEMAS
    return True


_options = {
    "target_metadata": target_metadata,
    "version_table_schema": VERSION_SCHEMA,
    "include_schemas": True,
    "include_name": _include_name,
}


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: print the SQL instead of running it."""
    context.configure(
        url=_url(), literal_binds=True, dialect_opts={"paramstyle": "named"}, **_options
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url())
    with engine.connect() as connection:
        connection.execute(CreateSchema(VERSION_SCHEMA, if_not_exists=True))
        connection.commit()

        context.configure(connection=connection, **_options)
        with context.begin_transaction():
            connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": LOCK_KEY})
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
