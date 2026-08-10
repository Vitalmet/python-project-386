from datetime import datetime, timezone

from .db import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EventType(db.Model):
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
    __tablename__ = "bookings"

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
