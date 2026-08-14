"""Хелперы работы с датой и временем.

Конвенция проекта: в БД и при сравнениях используются naive datetime в UTC.
Входные данные (ISO 8601) могут содержать таймзону — при разборе приводим её
к UTC и срезаем смещение, чтобы все значения сравнивались единообразно.
"""

from datetime import datetime, timezone


def parse_datetime_utc(value: str) -> datetime | None:
    """Разбирает строку ISO 8601 в naive datetime (UTC).

    Возвращает None, если строка не является корректной датой.
    """
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed
