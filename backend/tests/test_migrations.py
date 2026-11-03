from pathlib import Path

import pytest

from brave import migrate
from brave.core.ids import new_id


def test_files_are_numbered_and_unique() -> None:
    migrations = migrate.load_migrations()
    assert migrations[0].name == "0001_baseline.sql"
    assert [m.version for m in migrations] == sorted({m.version for m in migrations})


def test_bad_file_name_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "1_Bad Name.sql").write_text("SELECT 1;")
    with pytest.raises(migrate.MigrationError):
        migrate.load_migrations(tmp_path)


def test_ids_are_uuid7_and_time_ordered() -> None:
    first, second = new_id(), new_id()
    assert first.version == 7
    assert first < second


@pytest.mark.db
@pytest.mark.usefixtures("database")
def test_all_migrations_applied_and_rerun_is_a_no_op() -> None:
    assert migrate.up() == []
    assert all(is_applied for _, is_applied in migrate.status())


@pytest.mark.db
@pytest.mark.usefixtures("database")
def test_four_schemas_exist_and_nothing_in_public() -> None:
    import psycopg

    from brave.core.config import get_settings

    settings = get_settings()
    url = migrate._plain_url(settings.migration_database_url or settings.database_url)
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
