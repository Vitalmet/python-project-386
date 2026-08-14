"""Конфигурация приложения.

Настройки читаются из переменных окружения, чтобы одно и то же приложение
работало локально, в контейнере (PORT задаёт запускающий сервер) и в тестах.
"""

import os
from pathlib import Path

from sqlalchemy.pool import StaticPool

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Боевая конфигурация: SQLite-файл в корне проекта."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.sqlite'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None


class TestConfig(Config):
    """Конфигурация тестов: in-memory SQLite, единый пул соединений."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }
    WTF_CSRF_ENABLED = False
