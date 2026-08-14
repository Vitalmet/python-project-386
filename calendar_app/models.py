from datetime import datetime, timezone

from .db import db


def utcnow():
    """Текущее время в UTC без таймзоны.

    В БД все даты хранятся как naive datetime в UTC: так их сравнивают между
    собой без учёта часового пояса сервера, а наружу отдают в ISO 8601.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EventType(db.Model):
    """Тип события (вид брони), который владелец предлагает гостям.

    Название уникально — дубликат отклоняется на уровне БД.
    """

    __tablename__ = "event_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    bookings = db.relationship("Booking", back_populates="event_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EventType {self.name}>"


class Booking(db.Model):
    """Бронирование гостя на слот конкретного типа события.

    Правило занятости: на одно и то же время нельзя создать две записи,
    даже если это разные типы событий.
    """

    __tablename__ = "bookings"
    # Барьер на уровне БД: две брони с одинаковым starts_at невозможны даже при
    # параллельных запросах. Частичные пересечения интервалов (разные starts_at)
    # проверяются бизнес-логикой в services/bookings.py и services/slots.py.
    __table_args__ = (db.UniqueConstraint("starts_at", name="uq_booking_starts_at"),)

    id = db.Column(db.Integer, primary_key=True)
    event_type_id = db.Column(db.Integer, db.ForeignKey("event_types.id"), nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    event_type = db.relationship("EventType", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.starts_at} {self.guest_name}>"
