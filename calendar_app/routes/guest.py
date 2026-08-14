"""HTML-маршруты гостя.

Гость не регистрируется: выбирает тип события, свободный слот и бронирует.
Если клиент запрашивает JSON (Accept: application/json), те же обработчики
возвращают JSON из модуля api — HTML и API не дублируют бизнес-логику.
"""

from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..api import accepts_json, booking_get, event_type_get
from ..db import db
from ..models import Booking, EventType
from ..schemas import BookingForm
from ..services import bookings as bookings_service
from ..services import slots as slots_service
from ..services.bookings import EventTypeNotFoundError, SlotBusyError

guest_bp = Blueprint("guest", __name__)


def _group_slots_by_day(slots):
    """Группирует слоты по дням для постраничного отображения календаря."""
    days = {}
    for slot in slots:
        days.setdefault(slot.start.date(), []).append(slot)
    return [(day, days[day]) for day in sorted(days)]


@guest_bp.get("/")
def index():
    """Главная страница гостя: список доступных типов событий."""
    event_types = EventType.query.order_by(EventType.name.asc()).all()
    return render_template("guest/index.html", event_types=event_types)


@guest_bp.get("/event-types/<int:event_type_id>")
def event_type_calendar(event_type_id):
    """Календарь свободных слотов конкретного типа события."""
    if accepts_json():
        return event_type_get(event_type_id)
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        abort(404)
    slots = slots_service.available_slots(event_type)
    days = _group_slots_by_day(slots)
    return render_template("guest/calendar.html", event_type=event_type, days=days)


@guest_bp.route("/event-types/<int:event_type_id>/book", methods=["GET", "POST"])
def booking(event_type_id):
    """Форма бронирования: GET показывает форму, POST создаёт бронирование.

    Выбранный слот передаётся через query-параметр start. Если слот к моменту
    POST уже занят, гость возвращается в календарь с сообщением об ошибке.
    """
    event_type = db.session.get(EventType, event_type_id)
    if event_type is None:
        abort(404)

    form = BookingForm()

    if request.method == "GET":
        start_raw = request.args.get("start")
        if start_raw is None:
            flash("Выберите свободный слот в календаре.", "warning")
            return redirect(url_for("guest.event_type_calendar", event_type_id=event_type.id))
        try:
            starts_at = datetime.fromisoformat(start_raw)
        except ValueError:
            abort(400)
        if not slots_service.is_available(event_type, starts_at):
            flash("Этот слот уже занят или недоступен.", "warning")
            return redirect(url_for("guest.event_type_calendar", event_type_id=event_type.id))
        form.starts_at.data = starts_at.isoformat()
        slot_label = starts_at.strftime("%d.%m.%Y в %H:%M")
        return render_template(
            "guest/booking_form.html",
            form=form,
            event_type=event_type,
            slot_label=slot_label,
        )

    if not form.validate_on_submit():
        return render_template(
            "guest/booking_form.html",
            form=form,
            event_type=event_type,
            slot_label=form.starts_at.data or "",
        )

    try:
        booking = bookings_service.create_booking(
            event_type_id=event_type.id,
            starts_at=form.starts_at.data,
            guest_name=form.guest_name.data,
            phone=form.phone.data,
            email=form.email.data,
        )
    except (SlotBusyError, EventTypeNotFoundError):
        flash("Этот слот уже занят. Выберите другой слот.", "danger")
        return redirect(url_for("guest.event_type_calendar", event_type_id=event_type.id))

    return redirect(url_for("guest.booking_success", booking_id=booking.id))


@guest_bp.get("/bookings/<int:booking_id>")
def booking_success(booking_id):
    """Страница подтверждения бронирования."""
    if accepts_json():
        return booking_get(booking_id)
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        abort(404)
    return render_template("guest/success.html", booking=booking)
