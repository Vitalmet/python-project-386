"""Инициализация SQLAlchemy: единый объект db для моделей и запросов."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
