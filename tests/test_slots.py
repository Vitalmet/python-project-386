from datetime import datetime, time, timedelta

from calendar_app.models import Booking
from calendar_app.services import slots


def _noon_today():
    today = datetime.now().date()
    return datetime.combine(today, time(12, 0))


def _next_weekday_slot_start(now):
    start = now + timedelta(days=1)
    while start.weekday() in (5, 6):
        start += timedelta(days=1)
    return start.replace(hour=10, minute=0, second=0, microsecond=0)


def test_slots_are_within_14_day_window(db, event_type_factory):
    event_type = event_type_factory()
    result = slots.available_slots(event_type, now=_noon_today())
    assert result
    dates = {slot.start.date() for slot in result}
    assert max(dates) - min(dates) <= timedelta(days=13)
    today = datetime.now().date()
    assert all(today <= day <= today + timedelta(days=13) for day in dates)


def test_slots_only_on_weekdays(db, event_type_factory):
    event_type = event_type_factory()
    result = slots.available_slots(event_type, now=_noon_today())
    assert result
    assert all(slot.start.weekday() not in (5, 6) for slot in result)


def test_slots_within_working_hours(db, event_type_factory):
    event_type = event_type_factory(duration_minutes=60)
    result = slots.available_slots(event_type, now=_noon_today())
    assert result
    for slot in result:
        assert slot.start.time() >= slots.WORKDAY_START
        assert slot.end.time() <= slots.WORKDAY_END
        assert slot.end == slot.start + timedelta(minutes=60)


def test_slot_step_is_30_minutes(db, event_type_factory):
    event_type = event_type_factory()
    result = slots.available_slots(event_type, now=_noon_today())
    assert result
    for slot in result:
        assert slot.start.minute in (0, 30)
        assert slot.start.second == 0


def test_past_slots_excluded(db, event_type_factory):
    event_type = event_type_factory()
    now = _noon_today()
    result = slots.available_slots(event_type, now=now)
    assert result
    assert all(slot.start >= now for slot in result)


def test_booked_slot_is_excluded(db, event_type_factory):
    event_type = event_type_factory(duration_minutes=30)
    now = _noon_today()
    target = _next_weekday_slot_start(now)
    db.session.add(Booking(event_type=event_type, guest_name="Иван", starts_at=target))
    db.session.commit()

    result = slots.available_slots(event_type, now=now)
    starts = {slot.start for slot in result}
    assert target not in starts
    assert target - timedelta(minutes=30) in starts
    assert target + timedelta(minutes=30) in starts


def test_overlapping_booking_of_another_type_blocks_slot(db, event_type_factory):
    first = event_type_factory(name="Тип A", duration_minutes=30)
    second = event_type_factory(name="Тип B", duration_minutes=60)
    now = _noon_today()
    target = _next_weekday_slot_start(now)
    db.session.add(Booking(event_type=first, guest_name="Иван", starts_at=target))
    db.session.commit()

    result = slots.available_slots(second, now=now)
    starts = {slot.start for slot in result}
    assert target not in starts
    assert target + timedelta(minutes=30) in starts
