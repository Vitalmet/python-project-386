from datetime import datetime, time, timedelta

import pytest

from calendar_app.models import Booking
from calendar_app.services import bookings as bookings_service


def _noon_today():
    today = datetime.now().date()
    return datetime.combine(today, time(12, 0))


def _next_weekday_slot_start(now):
    start = now + timedelta(days=1)
    while start.weekday() in (5, 6):
        start += timedelta(days=1)
    return start.replace(hour=10, minute=0, second=0, microsecond=0)


def test_create_booking(db, event_type_factory):
    event_type = event_type_factory()
    now = _noon_today()
    start = _next_weekday_slot_start(now)

    booking = bookings_service.create_booking(
        event_type_id=event_type.id,
        starts_at=start,
        guest_name="Иван",
        phone="+7 900 000-00-00",
        email="ivan@example.com",
        now=now,
    )

    assert booking.id is not None
    assert booking.event_type_id == event_type.id
    assert booking.guest_name == "Иван"
    assert Booking.query.count() == 1


def test_create_booking_raises_for_missing_type(db):
    with pytest.raises(bookings_service.EventTypeNotFoundError):
        bookings_service.create_booking(
            event_type_id=999,
            starts_at=_noon_today(),
            guest_name="Иван",
            now=_noon_today(),
        )


def test_same_slot_conflict_across_types(db, event_type_factory):
    first = event_type_factory(name="Тип A", duration_minutes=30)
    second = event_type_factory(name="Тип B", duration_minutes=30)
    now = _noon_today()
    start = _next_weekday_slot_start(now)

    bookings_service.create_booking(
        event_type_id=first.id, starts_at=start, guest_name="Иван", now=now
    )

    with pytest.raises(bookings_service.SlotBusyError):
        bookings_service.create_booking(
            event_type_id=second.id, starts_at=start, guest_name="Пётр", now=now
        )


def test_partial_overlap_conflict(db, event_type_factory):
    first = event_type_factory(name="Тип A", duration_minutes=30)
    second = event_type_factory(name="Тип B", duration_minutes=60)
    now = _noon_today()
    start = _next_weekday_slot_start(now)

    bookings_service.create_booking(
        event_type_id=first.id, starts_at=start, guest_name="Иван", now=now
    )

    later = start + timedelta(minutes=30)
    booking = bookings_service.create_booking(
        event_type_id=second.id, starts_at=later, guest_name="Пётр", now=now
    )
    assert booking.id is not None

    with pytest.raises(bookings_service.SlotBusyError):
        bookings_service.create_booking(
            event_type_id=second.id, starts_at=start, guest_name="Пётр", now=now
        )
