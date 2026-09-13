from flask import Flask
import os


def create_app():
    """Application factory — creates and configures the Flask app."""
    root_dir     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template_dir = os.path.join(root_dir, "frontend", "templates")
    static_dir   = os.path.join(root_dir, "frontend", "static")

    flask_app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

    # Initialise SQLite users table
    from .models import init_db
    init_db()

    # Register blueprints
    from .routes import bp
    from .auth import auth_bp
    flask_app.register_blueprint(bp)
    flask_app.register_blueprint(auth_bp)

    return flask_app
