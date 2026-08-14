"""Расчёт свободных слотов для бронирования.

Слоты не хранятся в БД — они вычисляются по текущей дате и существующим
бронированиям. Правила сетки:
- окно бронирования: 14 дней начиная с текущей даты;
- рабочие часы: будни 09:00–18:00, шаг сетки 30 минут;
- сегодня доступны только слоты, которые ещё не начались;
- слот свободен, если интервал [start, end) не пересекается ни с одним
  бронированием (любого типа события).
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from ..db import db
from ..models import Booking, EventType

WORKDAY_START = time(9, 0)
WORKDAY_END = time(18, 0)
SLOT_STEP_MINUTES = 30
WINDOW_DAYS = 14
WEEKDAYS = (0, 1, 2, 3, 4)


@dataclass(frozen=True)
class Slot:
    """Свободный слот: начало, конец и признак доступности."""

    start: datetime
    end: datetime
    available: bool = True


def _candidate_starts(event_type: EventType, now: datetime):
    """Генератор потенциальных начал слотов по правилам сетки.

    Отсеивает выходные, слоты, выходящие за границы рабочего дня, и слоты,
    которые уже начались к моменту `now`.
    """
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
    """Есть ли среди бронирований интервал, пересекающий [start, end)."""
    for booking in bookings:
        booking_end = booking.starts_at + timedelta(minutes=booking.event_type.duration_minutes)
        if start < booking_end and booking.starts_at < end:
            return True
    return False


def available_slots(event_type: EventType, now: datetime | None = None) -> list[Slot]:
    """Все свободные слоты типа события в окне 14 дней.

    Используется для отображения календаря гостю.
    """
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
    """Свободен ли конкретный слот [start, start + длительность].

    Используется при попытке бронирования (точечная проверка). Вместо
    пересчёта всего календаря запрашиваем только брони, которые физически
    могут пересечься: они начинаются в промежутке
    [start - максимальная длительность события, start + длительность текущего).
    Бронь, начавшаяся раньше этого промежутка, заведомо завершится до start.
    """
    now = now or datetime.now()
    if start < now:
        return False
    end = start + timedelta(minutes=event_type.duration_minutes)
    max_duration_minutes = db.session.query(db.func.max(EventType.duration_minutes)).scalar() or 0
    start_limit = start - timedelta(minutes=max_duration_minutes)
    bookings = (
        Booking.query.join(Booking.event_type)
        .filter(Booking.starts_at < end, Booking.starts_at >= start_limit)
        .all()
    )
    return not _overlaps(start, end, bookings)
