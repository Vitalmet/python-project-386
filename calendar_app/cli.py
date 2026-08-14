"""Flask CLI-команды приложения (команда seed для демо-данных)."""

import click
from flask.cli import with_appcontext

from .db import db
from .models import EventType

# Демо-типы событий для локальной разработки и E2E-тестов.
# Команда seed использует эти данные, если типы ещё не добавлены.
SAMPLE_EVENT_TYPES = [
    {
        "name": "Консультация",
        "description": "Разговор с экспертом по вашему вопросу.",
        "duration_minutes": 30,
    },
    {
        "name": "Стратегическая сессия",
        "description": "Обсуждение целей и плана действий.",
        "duration_minutes": 60,
    },
    {
        "name": "Глубокий разбор",
        "description": "Подробный анализ вашей ситуации.",
        "duration_minutes": 90,
    },
]


@click.command("seed")
@with_appcontext
def seed_command():
    """Заполняет базу демо-типами событий (идемпотентно)."""
    if EventType.query.first():
        click.echo("Демо-данные уже добавлены.")
        return
    for item in SAMPLE_EVENT_TYPES:
        db.session.add(EventType(**item))
    db.session.commit()
    click.echo("Демо-типы событий добавлены.")


def init_app(app):
    """Регистрирует CLI-команды в приложении."""
    app.cli.add_command(seed_command)
