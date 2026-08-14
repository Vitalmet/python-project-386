"""WTForms-формы для HTML-страниц.

Используются только серверными HTML-маршрутами (routes/). JSON API
валидирует входные данные отдельно в модуле api (validate_*_create).
"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class EventTypeForm(FlaskForm):
    """Форма создания типа события владельцем."""

    name = StringField(
        "Название",
        validators=[DataRequired(message="Укажите название."), Length(max=100)],
    )
    description = TextAreaField(
        "Описание",
        validators=[DataRequired(message="Укажите описание.")],
    )
    duration_minutes = IntegerField(
        "Длительность (минуты)",
        validators=[
            DataRequired(message="Укажите длительность."),
            NumberRange(min=1, message="Длительность должна быть больше 0."),
        ],
    )
    submit = SubmitField("Создать")


class BookingForm(FlaskForm):
    """Форма бронирования гостя. Выбранный слот передаётся скрытым полем."""

    guest_name = StringField(
        "Имя",
        validators=[DataRequired(message="Укажите имя."), Length(max=100)],
    )
    phone = StringField("Телефон", validators=[Optional(), Length(max=50)])
    email = StringField(
        "Email",
        validators=[Optional(), Email(message="Некорректный email."), Length(max=120)],
    )
    starts_at = HiddenField(
        "Слот",
        validators=[DataRequired(message="Выберите слот.")],
    )
    submit = SubmitField("Забронировать")
