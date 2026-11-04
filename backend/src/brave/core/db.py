"""Database engine, sessions and the organisation (tenant) context.

Every request that touches clinical data runs inside a transaction that sets
``app.current_org_id``. PostgreSQL Row-Level Security policies read it through
the ``platform.current_org_id()`` function from migrations/versions/0001_baseline.py, so
one organisation can never read another's rows, even if application code has
a bug. This uses only plain PostgreSQL - no Supabase-specific roles or
``auth.uid()`` - so the same policies run on local Postgres, Supabase and RDS.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, MetaData, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from brave.core.config import get_settings

# Predictable constraint names, so Alembic migrations can refer to them.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def org_session(org_id: UUID) -> Iterator[Session]:
    """A transaction scoped to one organisation. Commits on success, rolls back on error."""
    with _session_factory().begin() as session:
        # SET LOCAL lasts only for this transaction, so pooled connections never leak it.
        session.execute(
            text("SELECT set_config('app.current_org_id', :org_id, true)"),
            {"org_id": str(org_id)},
        )
        yield session


def ping() -> bool:
    """True if the database answers a trivial query."""
    with get_engine().connect() as conn:
        return bool(conn.execute(text("SELECT 1")).scalar_one() == 1)
