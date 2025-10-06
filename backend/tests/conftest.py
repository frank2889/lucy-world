from __future__ import annotations

from typing import Generator

import pytest  # type: ignore

from backend import create_app
from backend.extensions import db


@pytest.fixture
def app(monkeypatch, tmp_path) -> Generator:
    db_file = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://example.com")
    application = create_app()
    application.config.update(TESTING=True)
    with application.app_context():
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
