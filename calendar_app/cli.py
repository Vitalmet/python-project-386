import click
from flask.cli import with_appcontext

from .db import db
from .models import EventType

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
    if EventType.query.first():
        click.echo("Демо-данные уже добавлены.")
        return
    for item in SAMPLE_EVENT_TYPES:
        db.session.add(EventType(**item))
    db.session.commit()
    click.echo("Демо-типы событий добавлены.")


def init_app(app):
    app.cli.add_command(seed_command)
