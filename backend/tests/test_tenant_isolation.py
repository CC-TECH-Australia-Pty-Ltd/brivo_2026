"""Proves the Row-Level Security pattern from the database plan:
a transaction only sees and writes its own organisation's rows."""

from uuid import UUID

import psycopg
import pytest
from sqlalchemy import text

from brivo.core.config import get_settings
from brivo.core.db import org_session
from brivo.core.ids import new_id

pytestmark = [pytest.mark.db, pytest.mark.usefixtures("database")]


def _owner() -> psycopg.Connection:
    settings = get_settings()
    url = settings.migration_database_url or settings.database_url
    # psycopg wants postgresql://, SQLAlchemy uses postgresql+psycopg://.
    return psycopg.connect(url.replace("postgresql+psycopg://", "postgresql://", 1))


def _set_org(conn: psycopg.Connection, org: UUID) -> None:
    conn.execute("SELECT set_config('app.current_org_id', %s, true)", (str(org),))


def test_enable_tenant_rls_helper_isolates_organisations() -> None:
    org_a, org_b = new_id(), new_id()
    with _owner() as conn, conn.transaction(force_rollback=True):
        conn.execute("CREATE TEMP TABLE note (org_id uuid NOT NULL, body text)")
        conn.execute("SELECT platform.enable_tenant_rls('pg_temp.note')")

        _set_org(conn, org_a)
        conn.execute("INSERT INTO note VALUES (%s, 'mine')", (org_a,))

        # Writing another organisation's row is rejected, even for the table owner (FORCE).
        with pytest.raises(psycopg.errors.InsufficientPrivilege), conn.transaction():
            conn.execute("INSERT INTO note VALUES (%s, 'theirs')", (org_b,))

        assert conn.execute("SELECT body FROM note").fetchall() == [("mine",)]

        _set_org(conn, org_b)
        assert conn.execute("SELECT count(*) FROM note").fetchone() == (0,)


def test_no_organisation_set_means_no_rows() -> None:
    with _owner() as conn, conn.transaction(force_rollback=True):
        conn.execute("CREATE TEMP TABLE note (org_id uuid NOT NULL, body text)")
        conn.execute("INSERT INTO note VALUES (%s, 'x')", (new_id(),))
        conn.execute("SELECT platform.enable_tenant_rls('pg_temp.note')")
        assert conn.execute("SELECT count(*) FROM note").fetchone() == (0,)


def test_app_role_cannot_bypass_rls_or_change_policies() -> None:
    with org_session(new_id()) as session:
        bypass = session.execute(
            text("SELECT rolbypassrls OR rolsuper FROM pg_roles WHERE rolname = current_user")
        ).scalar_one()
        assert bypass is False
        may_run_helper = session.execute(
            text("SELECT has_function_privilege('platform.enable_tenant_rls(regclass)', 'EXECUTE')")
        ).scalar_one()
        assert may_run_helper is False


def test_org_session_sets_current_org() -> None:
    org = new_id()
    with org_session(org) as session:
        assert session.execute(text("SELECT platform.current_org_id()")).scalar_one() == org
