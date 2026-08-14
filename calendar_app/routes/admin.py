"""HTML-маршруты владельца календаря.

Владелец — единый предзаданный профиль, авторизация в системе отсутствует.
Владелец создаёт типы событий и просматривает предстоящие встречи.
JSON-версии операций переиспользуют функции модуля api.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from ..api import accepts_json, admin_event_types_create, admin_event_types_list
from ..db import db
from ..models import EventType
from ..schemas import EventTypeForm
from ..services.bookings import upcoming_bookings

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/admin/event-types")
def event_types_index():
    """Список типов событий владельца (сначала новые)."""
    if accepts_json():
        return admin_event_types_list()
    event_types = EventType.query.order_by(EventType.created_at.desc(), EventType.id.desc()).all()
    return render_template("admin/event_types/index.html", event_types=event_types)


@admin_bp.get("/admin/event-types/new")
def event_types_new():
    """Форма создания нового типа события."""
    form = EventTypeForm()
    return render_template("admin/event_types/form.html", form=form)


@admin_bp.post("/admin/event-types")
def event_types_create():
    """Создание типа события. JSON-запросы обрабатывает api-функция."""
    if request.is_json:
        return admin_event_types_create()
    form = EventTypeForm()
    if not form.validate_on_submit():
        return render_template("admin/event_types/form.html", form=form), 400

    event_type = EventType(
        name=form.name.data,
        description=form.description.data,
        duration_minutes=form.duration_minutes.data,
    )
    db.session.add(event_type)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Тип события с таким названием уже существует.", "danger")
        return render_template("admin/event_types/form.html", form=form), 409

    flash("Тип события создан.", "success")
    return redirect(url_for("admin.event_types_index"))


@admin_bp.get("/admin/bookings")
def bookings_index():
    """Страница предстоящих встреч владельца (все типы событий)."""
    bookings = upcoming_bookings()
    return render_template("admin/bookings.html", bookings=bookings)
