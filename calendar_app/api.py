from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .db import db
from .models import Booking, EventType
from .services import bookings as bookings_service
from .services import slots as slots_service

api_bp = Blueprint("api", __name__)


def accepts_json() -> bool:
    return request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html


def event_type_dict(event_type: EventType) -> dict:
    return {
        "id": event_type.id,
        "name": event_type.name,
        "description": event_type.description,
        "durationMinutes": event_type.duration_minutes,
    }


def booking_dict(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "eventTypeId": booking.event_type_id,
        "guestName": booking.guest_name,
        "phone": booking.phone,
        "email": booking.email,
        "startsAt": booking.starts_at.isoformat(),
        "createdAt": booking.created_at.isoformat(),
    }


def slot_dict(slot) -> dict:
    return {
        "start": slot.start.isoformat(),
        "end": slot.end.isoformat(),
        "available": slot.available,
    }


def error_payload(code: str, message: str, details=None):
    payload = {"code": code, "message": message}
    if details:
        payload["details"] = details
    return jsonify(payload)


def not_found(message="Ресурс не найден."):
    return error_payload("NOT_FOUND", message), 404


def validation_error(message="Некорректные входные данные.", details=None):
    return error_payload("VALIDATION_ERROR", message, details), 400


def conflict(message="Слот занят."):
    return error_payload("SLOT_BUSY", message), 409


def _parse_datetime(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


def _email_valid(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return False
    return True


def validate_event_type_create(payload: dict) -> list[str]:
    errors = []
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name: обязательная строка.")
    elif len(name) > 100:
        errors.append("name: максимум 100 символов.")
    description = payload.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description: обязательная строка.")
    duration = payload.get("durationMinutes")
    if not isinstance(duration, int) or isinstance(duration, bool):
        errors.append("durationMinutes: обязательное целое число.")
    elif duration < 1:
        errors.append("durationMinutes: должно быть больше 0.")
    return errors


def validate_booking_create(payload: dict) -> list[str]:
    errors = []
    event_type_id = payload.get("eventTypeId")
    if not isinstance(event_type_id, int) or isinstance(event_type_id, bool):
        errors.append("eventTypeId: обязательное целое число.")
    starts_at = payload.get("startsAt")
    if not isinstance(starts_at, str) or _parse_datetime(starts_at) is None:
        errors.append("startsAt: обязательное значение в формате ISO 8601.")
    guest_name = payload.get("guestName")
    if not isinstance(guest_name, str) or not guest_name.strip():
        errors.append("guestName: обязательная строка (минимум 1 символ).")
    phone = payload.get("phone")
    if phone is not None and (not isinstance(phone, str) or len(phone) > 50):
        errors.append("phone: строка до 50 символов.")
    email = payload.get("email")
    if email is not None:
        if not isinstance(email, str) or len(email) > 120:
            errors.append("email: строка до 120 символов.")
        elif not _email_valid(email):
            errors.append("email: некорректный email.")
    return errors


def _json_body() -> dict | None:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None
    return payload


@api_bp.get("/event-types")
def event_type_list():
    event_types = EventType.query.order_by(EventType.name.asc()).all()
    return jsonify([event_type_dict(event_type) for event_type in event_types])


def event_type_get(event_type_id: int):
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        return not_found("Тип события не найден.")
    return jsonify(event_type_dict(event_type))


@api_bp.get("/event-types/<int:event_type_id>/slots")
def event_type_slots(event_type_id):
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        return not_found("Тип события не найден.")

    slots = slots_service.available_slots(event_type)
    from_raw = request.args.get("from")
    to_raw = request.args.get("to")
    if from_raw is not None:
        from_dt = _parse_datetime(from_raw)
        if from_dt is None:
            return validation_error("Некорректный формат параметра from.")
        slots = [slot for slot in slots if slot.start >= from_dt]
    if to_raw is not None:
        to_dt = _parse_datetime(to_raw)
        if to_dt is None:
            return validation_error("Некорректный формат параметра to.")
        slots = [slot for slot in slots if slot.start < to_dt]
    return jsonify([slot_dict(slot) for slot in slots])


@api_bp.post("/bookings")
def booking_create():
    payload = _json_body()
    if payload is None:
        return validation_error("Тело запроса должно быть JSON-объектом.")
    errors = validate_booking_create(payload)
    if errors:
        return validation_error("Некорректные входные данные.", details=errors)

    starts_at = _parse_datetime(payload["startsAt"])
    try:
        booking = bookings_service.create_booking(
            event_type_id=payload["eventTypeId"],
            starts_at=starts_at,
            guest_name=payload["guestName"].strip(),
            phone=payload.get("phone"),
            email=payload.get("email"),
        )
    except bookings_service.EventTypeNotFoundError:
        return validation_error("Тип события не найден.")
    except bookings_service.SlotBusyError:
        return conflict("Слот занят: на это время уже есть бронирование.")

    return jsonify(booking_dict(booking)), 201


def booking_get(booking_id: int):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        return not_found("Бронирование не найдено.")
    return jsonify(booking_dict(booking))


def admin_event_types_list():
    event_types = EventType.query.order_by(EventType.created_at.desc(), EventType.id.desc()).all()
    return jsonify([event_type_dict(event_type) for event_type in event_types])


def admin_event_types_create():
    payload = _json_body()
    if payload is None:
        return validation_error("Тело запроса должно быть JSON-объектом.")
    errors = validate_event_type_create(payload)
    if errors:
        return validation_error("Некорректные входные данные.", details=errors)

    event_type = EventType(
        name=payload["name"].strip(),
        description=payload["description"].strip(),
        duration_minutes=payload["durationMinutes"],
    )
    db.session.add(event_type)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return validation_error("Тип события с таким названием уже существует.")
    return jsonify(event_type_dict(event_type)), 201


@api_bp.get("/admin/bookings/upcoming")
def upcoming_bookings():
    bookings = bookings_service.upcoming_bookings()
    from_raw = request.args.get("from")
    if from_raw is not None:
        from_dt = _parse_datetime(from_raw)
        if from_dt is None:
            return validation_error("Некорректный формат параметра from.")
        bookings = [booking for booking in bookings if booking.starts_at >= from_dt]
    return jsonify({"bookings": [booking_dict(booking) for booking in bookings]})
