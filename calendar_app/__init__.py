"""Фабрика Flask-приложения «Календарь звонков».

create_app подключает БД, CORS, JSON API и HTML-маршруты (гость, владелец)
и создаёт таблицы при старте — поэтому в контейнере приложение готово к работе
сразу после запуска (миграции не требуются).
"""

from flask import Flask
from flask_cors import CORS

from .api import api_bp
from .cli import init_app as init_cli
from .config import Config
from .db import db
from .routes.admin import admin_bp
from .routes.guest import guest_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)
    app.register_blueprint(api_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(admin_bp)
    init_cli(app)

    with app.app_context():
        db.create_all()

    return app
