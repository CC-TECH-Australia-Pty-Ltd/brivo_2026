import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from brivo import __version__
from brivo.core import db


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_health_db_unavailable(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail() -> bool:
        raise OperationalError("SELECT 1", {}, Exception("down"))

    monkeypatch.setattr(db, "ping", fail)
    response = client.get("/health/db")
    assert response.status_code == 503


@pytest.mark.db
@pytest.mark.usefixtures("database")
def test_health_db_ok(client: TestClient) -> None:
    assert client.get("/health/db").json() == {"status": "ok"}
