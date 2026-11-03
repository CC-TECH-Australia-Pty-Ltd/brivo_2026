from pathlib import Path

import psycopg
import pytest
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from brave.core.config import get_settings
from brave.core.ids import new_id

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def _script() -> ScriptDirectory:
    return ScriptDirectory.from_config(Config(ALEMBIC_INI))


def _owner_url() -> str:
    settings = get_settings()
    return settings.migration_database_url or settings.database_url


def test_revisions_are_numbered_in_one_line() -> None:
    script = _script()
    assert len(script.get_heads()) == 1, "Two migrations share a parent: renumber one"
    revisions = list(reversed(list(script.walk_revisions())))
    assert revisions[0].revision == "0001"
    assert [r.revision for r in revisions] == [f"{i:04d}" for i in range(1, len(revisions) + 1)]


def test_ids_are_uuid7_and_time_ordered() -> None:
    first, second = new_id(), new_id()
    assert first.version == 7
    assert first < second


@pytest.mark.db
@pytest.mark.usefixtures("database")
def test_database_is_at_head() -> None:
    engine = create_engine(_owner_url())
    with engine.connect() as conn:
        current = MigrationContext.configure(
            conn, opts={"version_table_schema": "migrations"}
        ).get_current_heads()
    engine.dispose()
    assert set(current) == set(_script().get_heads())


@pytest.mark.db
@pytest.mark.usefixtures("database")
def test_four_schemas_exist_and_nothing_in_public() -> None:
    url = _owner_url().replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(url) as conn:
        schemas = {
            r[0]
            for r in conn.execute(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name IN ('platform', 'content', 'clinical', 'media')"
            )
        }
        public_tables = conn.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchone()
    assert schemas == {"platform", "content", "clinical", "media"}
    assert public_tables == (0,)
