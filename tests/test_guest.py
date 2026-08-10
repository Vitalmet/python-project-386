from datetime import datetime, timedelta

from calendar_app.models import Booking


def _next_weekday_slot_start():
    now = datetime.now()
    start = now + timedelta(days=1)
    while start.weekday() in (5, 6):
        start += timedelta(days=1)
    return start.replace(hour=10, minute=0, second=0, microsecond=0)


def test_index_lists_event_types(client, event_type_factory):
    event_type_factory(name="Консультация")
    event_type_factory(name="Стратегическая сессия")

    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Консультация" in body
    assert "Стратегическая сессия" in body


def test_calendar_shows_slots(client, event_type_factory):
    event_type = event_type_factory(duration_minutes=30)

    response = client.get(f"/event-types/{event_type.id}")
    assert response.status_code == 200
    assert "Доступные слоты" in response.get_data(as_text=True)


def test_booking_flow(client, event_type_factory):
    event_type = event_type_factory(duration_minutes=30)
    start = _next_weekday_slot_start()

    response = client.get(f"/event-types/{event_type.id}/book?start={start.isoformat()}")
    assert response.status_code == 200
    assert "Бронирование" in response.get_data(as_text=True)

    response = client.post(
        f"/event-types/{event_type.id}/book",
        data={"guest_name": "Иван", "phone": "", "email": "", "starts_at": start.isoformat()},
        follow_redirects=True,
    )
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Бронирование подтверждено" in body
    assert "Иван" in body


def test_duplicate_booking_conflict(client, event_type_factory):
    first = event_type_factory(name="Тип A", duration_minutes=30)
    second = event_type_factory(name="Тип B", duration_minutes=30)
    start = _next_weekday_slot_start()

    client.post(
        f"/event-types/{first.id}/book",
        data={"guest_name": "Иван", "starts_at": start.isoformat()},
    )
    response = client.post(
        f"/event-types/{second.id}/book",
        data={"guest_name": "Пётр", "starts_at": start.isoformat()},
        follow_redirects=True,
    )
    assert "уже занят" in response.get_data(as_text=True)
    assert Booking.query.count() == 1


def test_booking_requires_guest_name(client, event_type_factory):
    event_type = event_type_factory(duration_minutes=30)
    start = _next_weekday_slot_start()

    response = client.post(
        f"/event-types/{event_type.id}/book",
        data={"guest_name": "", "starts_at": start.isoformat()},
    )
    assert response.status_code == 200
    assert "Укажите имя" in response.get_data(as_text=True)
