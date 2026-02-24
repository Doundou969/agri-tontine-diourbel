from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__)

    from app.config import config
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.tontines import tontines_bp
    from app.routes.cotisations import cotisations_bp
    from app.routes.credits import credits_bp

    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(tontines_bp,    url_prefix="/api/tontines")
    app.register_blueprint(cotisations_bp, url_prefix="/api/cotisations")
    app.register_blueprint(credits_bp,     url_prefix="/api/credits")

    with app.app_context():
        db.create_all()

    return app
