import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from brivo.core import db
from brivo.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def database() -> None:
    """Skip DB tests when no PostgreSQL is reachable (e.g. a quick local run)."""
    try:
        db.ping()
    except OperationalError:
        pytest.skip("PostgreSQL not reachable - start it with `make db-up`")
