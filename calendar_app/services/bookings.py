"""Бизнес-логика бронирований.

Порядок создания бронирования:
1. проверяем, что тип события существует;
2. проверяем, что слот свободен (is_available в services/slots.py);
3. вставляем запись. Дубликат на уровне БД (одинаковый starts_at)
   обрабатывается как занятый слот — это защита от гонки при параллельных
   запросах.
"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError

from ..db import db
from ..models import Booking, EventType
from ..timeutil import parse_datetime_utc
from .slots import is_available


class SlotBusyError(Exception):
    """Слот занят: на это время уже есть бронирование (любого типа события)."""


class EventTypeNotFoundError(Exception):
    """Тип события не существует."""


def create_booking(
    event_type_id: int,
    starts_at: datetime,
    guest_name: str,
    phone: str | None = None,
    email: str | None = None,
    now: datetime | None = None,
) -> Booking:
    """Создаёт бронирование, если слот свободен, иначе бросает SlotBusyError.

    starts_at принимает naive datetime или ISO-строку; таймзона в строке
    нормализуется к UTC (см. timeutil.parse_datetime_utc).
    """
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        raise EventTypeNotFoundError()

    if isinstance(starts_at, str):
        parsed = parse_datetime_utc(starts_at)
        if parsed is None:
            raise SlotBusyError()
        starts_at = parsed

    if not is_available(event_type, starts_at, now=now):
        raise SlotBusyError()

    booking = Booking(
        event_type=event_type,
        starts_at=starts_at,
        guest_name=guest_name,
        phone=phone or None,
        email=email or None,
    )
    db.session.add(booking)
    try:
        db.session.commit()
    except IntegrityError:
        # Барьер модели: одинаковый starts_at недопустим на уровне БД.
        # Достижимо только при параллельных запросах — трактуем как занятый слот.
        db.session.rollback()
        raise SlotBusyError() from None
    return booking


def upcoming_bookings() -> list[Booking]:
    """Предстоящие встречи: будущие бронирования всех типов по возрастанию времени."""
    return (
        Booking.query.join(Booking.event_type)
        .filter(Booking.starts_at >= datetime.now())
        .order_by(Booking.starts_at.asc())
        .all()
    )
