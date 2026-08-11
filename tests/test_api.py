from datetime import datetime, time, timedelta

from calendar_app.models import Booking


def _noon_today():
    today = datetime.now().date()
    return datetime.combine(today, time(12, 0))


def _next_weekday_slot_start():
    now = datetime.now()
    start = now + timedelta(days=1)
    while start.weekday() in (5, 6):
        start += timedelta(days=1)
    return start.replace(hour=10, minute=0, second=0, microsecond=0)


def _json_headers():
    return {"Accept": "application/json"}


def test_api_list_event_types(client, event_type_factory):
    event_type_factory(name="Консультация")
    event_type_factory(name="Стратегическая сессия")

    response = client.get("/event-types", headers=_json_headers())
    assert response.status_code == 200
    assert response.is_json
    names = [item["name"] for item in response.get_json()]
    assert names == ["Консультация", "Стратегическая сессия"]


def test_api_get_event_type(client, event_type_factory):
    event_type = event_type_factory(duration_minutes=45)

    response = client.get(f"/event-types/{event_type.id}", headers=_json_headers())
    assert response.status_code == 200
    assert response.get_json() == {
        "id": event_type.id,
        "name": "Консультация",
        "description": "Описание",
        "durationMinutes": 45,
    }


def test_api_get_event_type_missing(client):
    response = client.get("/event-types/999", headers=_json_headers())
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_api_slots(client, event_type_factory):
    event_type = event_type_factory(duration_minutes=30)

    response = client.get(f"/event-types/{event_type.id}/slots", headers=_json_headers())
    assert response.status_code == 200
    slots = response.get_json()
    assert slots
    for slot in slots:
        assert set(slot.keys()) == {"start", "end", "available"}
        assert slot["available"] is True


def test_api_slots_missing(client):
    response = client.get("/event-types/999/slots", headers=_json_headers())
    assert response.status_code == 404


def test_api_create_booking(client, event_type_factory, db):
    event_type = event_type_factory(duration_minutes=30)
    start = _next_weekday_slot_start()

    response = client.post(
        "/bookings",
        json={
            "eventTypeId": event_type.id,
            "startsAt": start.isoformat(),
            "guestName": "Иван",
            "phone": "+7 900 000-00-00",
            "email": "ivan@example.com",
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["eventTypeId"] == event_type.id
    assert body["guestName"] == "Иван"
    assert Booking.query.count() == 1


def test_api_create_booking_busy(client, event_type_factory, db):
    first = event_type_factory(name="Тип A", duration_minutes=30)
    second = event_type_factory(name="Тип B", duration_minutes=30)
    start = _next_weekday_slot_start()
    db.session.add(Booking(event_type=first, guest_name="Иван", starts_at=start))
    db.session.commit()

    response = client.post(
        "/bookings",
        json={"eventTypeId": second.id, "startsAt": start.isoformat(), "guestName": "Пётр"},
    )
    assert response.status_code == 409
    assert response.get_json()["code"] == "SLOT_BUSY"


def test_api_create_booking_validation(client):
    response = client.post("/bookings", json={"guestName": "Иван"})
    assert response.status_code == 400
    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    assert isinstance(body["details"], list)


def test_api_create_booking_unknown_type(client):
    start = _next_weekday_slot_start().isoformat()
    response = client.post(
        "/bookings",
        json={"eventTypeId": 999, "startsAt": start, "guestName": "Иван"},
    )
    assert response.status_code == 400
    assert response.get_json()["code"] == "VALIDATION_ERROR"


def test_api_get_booking(client, event_type_factory, db):
    event_type = event_type_factory(duration_minutes=30)
    start = _next_weekday_slot_start()
    db.session.add(Booking(event_type=event_type, guest_name="Иван", starts_at=start))
    db.session.commit()
    booking = Booking.query.first()

    response = client.get(f"/bookings/{booking.id}", headers=_json_headers())
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == booking.id
    assert body["guestName"] == "Иван"


def test_api_get_booking_missing(client):
    response = client.get("/bookings/999", headers=_json_headers())
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_api_admin_list(client, event_type_factory):
    event_type_factory(name="Консультация")

    response = client.get("/admin/event-types", headers=_json_headers())
    assert response.status_code == 200
    assert response.is_json
    assert [item["name"] for item in response.get_json()] == ["Консультация"]


def test_api_admin_create(client):
    response = client.post(
        "/admin/event-types",
        json={"name": "Разбор", "description": "Описание", "durationMinutes": 60},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Разбор"
    assert body["durationMinutes"] == 60


def test_api_admin_create_duplicate(client, event_type_factory):
    event_type_factory(name="Консультация")

    response = client.post(
        "/admin/event-types",
        json={"name": "Консультация", "description": "Другое описание", "durationMinutes": 30},
    )
    assert response.status_code == 400
    assert response.get_json()["code"] == "VALIDATION_ERROR"


def test_api_admin_create_invalid_duration(client):
    response = client.post(
        "/admin/event-types",
        json={"name": "Тест", "description": "Описание", "durationMinutes": 0},
    )
    assert response.status_code == 400


def test_api_admin_upcoming(client, event_type_factory, db):
    event_type = event_type_factory(duration_minutes=30)
    future = datetime.now() + timedelta(days=1)
    past = datetime.now() - timedelta(days=1)
    db.session.add(Booking(event_type=event_type, guest_name="Иван", starts_at=future))
    db.session.add(Booking(event_type=event_type, guest_name="Пётр", starts_at=past))
    db.session.commit()

    response = client.get("/admin/bookings/upcoming", headers=_json_headers())
    assert response.status_code == 200
    body = response.get_json()
    names = [item["guestName"] for item in body["bookings"]]
    assert names == ["Иван"]
