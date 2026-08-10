from datetime import datetime, timedelta

from calendar_app.models import Booking


def test_admin_new_form(client):
    response = client.get("/admin/event-types/new")
    assert response.status_code == 200


def test_admin_creates_event_type(client):
    response = client.post(
        "/admin/event-types",
        data={"name": "Консультация", "description": "Описание", "duration_minutes": 30},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Консультация" in response.get_data(as_text=True)


def test_admin_rejects_duplicate_name(client, event_type_factory):
    event_type_factory(name="Консультация")

    response = client.post(
        "/admin/event-types",
        data={"name": "Консультация", "description": "Другое описание", "duration_minutes": 60},
    )
    assert response.status_code == 409


def test_admin_rejects_invalid_duration(client):
    response = client.post(
        "/admin/event-types",
        data={"name": "Тест", "description": "Описание", "duration_minutes": 0},
    )
    assert response.status_code == 400


def test_upcoming_bookings_list_only_future(client, event_type_factory, db):
    event_type = event_type_factory(duration_minutes=30)
    future = datetime.now() + timedelta(days=1)
    past = datetime.now() - timedelta(days=1)
    db.session.add(Booking(event_type=event_type, guest_name="Иван", starts_at=future))
    db.session.add(Booking(event_type=event_type, guest_name="Пётр", starts_at=past))
    db.session.commit()

    response = client.get("/admin/bookings")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Иван" in body
    assert "Пётр" not in body
