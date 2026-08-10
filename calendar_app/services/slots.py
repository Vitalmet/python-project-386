from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from ..models import Booking, EventType

WORKDAY_START = time(9, 0)
WORKDAY_END = time(18, 0)
SLOT_STEP_MINUTES = 30
WINDOW_DAYS = 14
WEEKDAYS = (0, 1, 2, 3, 4)


@dataclass(frozen=True)
class Slot:
    start: datetime
    end: datetime
    available: bool = True


def window_start() -> datetime:
    return datetime.combine(date.today(), time.min)


def window_end() -> datetime:
    last_day = date.today() + timedelta(days=WINDOW_DAYS - 1)
    return datetime.combine(last_day, WORKDAY_END)


def _candidate_starts(event_type: EventType, now: datetime):
    base = datetime.combine(date.today(), time.min)
    duration = timedelta(minutes=event_type.duration_minutes)
    for offset in range(WINDOW_DAYS):
        day_start = base + timedelta(days=offset)
        if day_start.weekday() not in WEEKDAYS:
            continue
        cursor = datetime.combine(day_start.date(), WORKDAY_START)
        day_end = datetime.combine(day_start.date(), WORKDAY_END)
        while cursor + duration <= day_end:
            if cursor >= now:
                yield cursor
            cursor += timedelta(minutes=SLOT_STEP_MINUTES)


def _overlaps(start: datetime, end: datetime, bookings) -> bool:
    for booking in bookings:
        booking_end = booking.starts_at + timedelta(minutes=booking.event_type.duration_minutes)
        if start < booking_end and booking.starts_at < end:
            return True
    return False


def available_slots(event_type: EventType, now: datetime | None = None) -> list[Slot]:
    now = now or datetime.now()
    duration = timedelta(minutes=event_type.duration_minutes)
    horizon = datetime.combine(date.today() + timedelta(days=WINDOW_DAYS), time.min)
    bookings = Booking.query.join(Booking.event_type).filter(Booking.starts_at < horizon).all()
    slots = []
    for start in _candidate_starts(event_type, now):
        end = start + duration
        if not _overlaps(start, end, bookings):
            slots.append(Slot(start=start, end=end))
    return slots


def is_available(event_type: EventType, start: datetime, now: datetime | None = None) -> bool:
    return start in {slot.start for slot in available_slots(event_type, now=now)}
