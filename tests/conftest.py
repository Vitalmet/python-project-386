import pytest

from calendar_app import create_app
from calendar_app.config import TestConfig
from calendar_app.db import db as _db


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture()
def event_type_factory(db):
    from calendar_app.models import EventType

    def make(**kwargs):
        data = {"name": "Консультация", "description": "Описание", "duration_minutes": 30}
        data.update(kwargs)
        event_type = EventType(**data)
        db.session.add(event_type)
        db.session.commit()
        return event_type

    return make
