# Сборка образа «Календарь звонков» (бэкенд Flask).
# Приложение стартует автоматически при запуске контейнера
# и слушает порт из переменной окружения PORT (по умолчанию 5000).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Устанавливаем Poetry — зависимости ставятся строго по poetry.lock.
RUN pip install poetry

# Отключаем виртуальное окружение: пакеты ставятся в системный Python,
# поэтому gunicorn попадает на PATH и запускается из CMD напрямую.
RUN poetry config virtualenvs.create false

# Сначала копируем манифесты: слой кэшируется и не пересобирается при изменении кода.
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

# Копируем исходники приложения.
COPY calendar_app ./calendar_app

# Порт по умолчанию; на деплое переопределяется переменной окружения PORT.
EXPOSE 5000

# Автозапуск приложения: gunicorn слушает 0.0.0.0:$PORT.
# workers=1 — SQLite не рассчитан на конкурентную запись из нескольких процессов.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 'calendar_app:create_app()'"]