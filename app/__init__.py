from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # IMPORTANT: Import all models before initializing SQLAlchemy
    from app import models

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Register blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.customer import customer_bp
    from app.api import api_bp
    from app.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(api_bp, url_prefix="/api")

    register_error_handlers(app)
    register_context_processors(app)

    Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template(
                "error.html",
                error_code=404,
                error_message="Page not found."
            ),
            404,
        )

    @app.errorhandler(403)
    def forbidden(error):
        return (
            render_template(
                "error.html",
                error_code=403,
                error_message="Access denied."
            ),
            403,
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return (
            render_template(
                "error.html",
                error_code=500,
                error_message="Internal server error."
            ),
            500,
        )


def register_context_processors(app):
    @app.context_processor
    def inject_cart_count():
        from flask_login import current_user

        count = 0

        if current_user.is_authenticated and not current_user.is_admin:
            from app.models import CartItem

            count = (
                db.session.query(
                    db.func.coalesce(db.func.sum(CartItem.quantity), 0)
                )
                .filter_by(user_id=current_user.id)
                .scalar()
            )

        return {"cart_count": count or 0}