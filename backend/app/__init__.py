from flask import Flask
import os


def create_app():
    """Application factory — creates and configures the Flask app."""
    # Resolve paths to the frontend folder (sibling of backend/)
    root_dir      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template_dir  = os.path.join(root_dir, "frontend", "templates")
    static_dir    = os.path.join(root_dir, "frontend", "static")

    flask_app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

    from .routes import bp
    flask_app.register_blueprint(bp)

    return flask_app
