"""Plain SQL migration runner.

Applies the numbered files in db/migrations (0001_baseline.sql, 0002_....sql) in
order, each in its own transaction, and records them in migrations.applied with a
SHA-256 checksum. The same files run unchanged on local Postgres, Supabase and RDS.

    uv run python -m brave.migrate status
    uv run python -m brave.migrate up

Rules: never edit a file that has been applied anywhere - add a new file instead.
Migrations are forward-only; to undo something, write a new migration.
"""

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import psycopg

from brave.core.config import get_settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "db" / "migrations"
FILE_PATTERN = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")
LOCK_KEY = 7_424_100  # any constant; stops two deploys migrating at once


class MigrationError(Exception):
    pass


@dataclass(frozen=True)
class Migration:
    version: str
    name: str
    sql: str

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode()).hexdigest()


def load_migrations(directory: Path = MIGRATIONS_DIR) -> list[Migration]:
    migrations = []
    for path in sorted(directory.glob("*.sql")):
        match = FILE_PATTERN.match(path.name)
        if not match:
            raise MigrationError(f"Bad file name {path.name}: use NNNN_lower_snake_case.sql")
        migrations.append(Migration(match.group(1), path.name, path.read_text()))
    versions = [m.version for m in migrations]
    if len(versions) != len(set(versions)):
        raise MigrationError("Two migration files share a number")
    return migrations


def _plain_url(url: str) -> str:
    """psycopg wants postgresql://, SQLAlchemy uses postgresql+psycopg://."""
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def _connect() -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(_plain_url(settings.migration_database_url or settings.database_url))


def _ensure_table(conn: psycopg.Connection) -> None:
    conn.execute("CREATE SCHEMA IF NOT EXISTS migrations")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations.applied (
            version    text PRIMARY KEY,
            name       text NOT NULL,
            checksum   text NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )


def _applied(conn: psycopg.Connection) -> dict[str, str]:
    rows = conn.execute("SELECT version, checksum FROM migrations.applied").fetchall()
    return {version: checksum for version, checksum in rows}


def _check_unchanged(migrations: list[Migration], applied: dict[str, str]) -> None:
    for m in migrations:
        if m.version in applied and applied[m.version] != m.checksum:
            raise MigrationError(
                f"{m.name} was changed after it was applied. Revert it and add a new migration."
            )


def status() -> list[tuple[str, bool]]:
    migrations = load_migrations()
    with _connect() as conn:
        _ensure_table(conn)
        applied = _applied(conn)
    _check_unchanged(migrations, applied)
    return [(m.name, m.version in applied) for m in migrations]


def up() -> list[str]:
    """Apply all pending migrations. Returns the names applied."""
    migrations = load_migrations()
    done: list[str] = []
    with _connect() as conn:
        with conn.transaction():
            conn.execute("SELECT pg_advisory_xact_lock(%s)", (LOCK_KEY,))
            _ensure_table(conn)
            applied = _applied(conn)
            _check_unchanged(migrations, applied)
        for m in migrations:
            if m.version in applied:
                continue
            with conn.transaction():
                conn.execute("SELECT pg_advisory_xact_lock(%s)", (LOCK_KEY,))
                if conn.execute(
                    "SELECT 1 FROM migrations.applied WHERE version = %s", (m.version,)
                ).fetchone():
                    continue  # another process applied it meanwhile
                conn.execute(m.sql.encode())  # whole file, simple query protocol
                conn.execute(
                    "INSERT INTO migrations.applied (version, name, checksum) VALUES (%s, %s, %s)",
                    (m.version, m.name, m.checksum),
                )
            done.append(m.name)
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m brave.migrate", description=__doc__)
    parser.add_argument("command", choices=["status", "up"])
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            for name, is_applied in status():
                print(f"{'applied' if is_applied else 'PENDING':8} {name}")
        else:
            names = up()
            print("\n".join(f"applied  {n}" for n in names) or "Up to date.")
    except MigrationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
