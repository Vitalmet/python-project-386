from flask import Flask

from .cli import init_app as init_cli
from .config import Config
from .db import db
from .routes.admin import admin_bp
from .routes.guest import guest_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(guest_bp)
    app.register_blueprint(admin_bp)
    init_cli(app)

    with app.app_context():
        db.create_all()

    return app
