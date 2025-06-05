from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, mapper_registry


@pytest.fixture
def client(session: Session):
    def override_get_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = override_get_session
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    mapper_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    mapper_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(model=User, time=datetime(2025, 4, 6)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session: Session):
    user = User(username='teste', email='teste@teste.com', password='teste')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
