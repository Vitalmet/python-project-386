from datetime import datetime

from sqlalchemy.exc import IntegrityError

from ..db import db
from ..models import Booking, EventType
from .slots import is_available


class SlotBusyError(Exception):
    pass


class EventTypeNotFoundError(Exception):
    pass


def create_booking(
    event_type_id: int,
    starts_at: datetime,
    guest_name: str,
    phone: str | None = None,
    email: str | None = None,
    now: datetime | None = None,
) -> Booking:
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        raise EventTypeNotFoundError()

    if isinstance(starts_at, str):
        starts_at = datetime.fromisoformat(starts_at)

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
        db.session.rollback()
        raise SlotBusyError() from None
    return booking


def upcoming_bookings() -> list[Booking]:
    return (
        Booking.query.join(Booking.event_type)
        .filter(Booking.starts_at >= datetime.now())
        .order_by(Booking.starts_at.asc())
        .all()
    )
