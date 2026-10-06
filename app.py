import os
from flask import Flask, session
from config import Config
from extensions import db, login_manager
from modules.i18n import t as translate


def create_app(config_class=Config):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    template_dir = os.path.join(base_dir, "templates")

    app = Flask(
        __name__,
        static_folder=static_dir,
        static_url_path="/static",
        template_folder=template_dir,
    )
    app.config.from_object(config_class)

    from flask import send_from_directory

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(static_dir, filename)

    try:
        instance_dir = os.path.join(app.root_path, "instance")
        os.makedirs(instance_dir, exist_ok=True)
    except Exception:
        pass

    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.main import bp as main_bp
    from routes.auth import bp as auth_bp
    from routes.idea import bp as idea_bp
    from api.analysis import bp as analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(idea_bp)
    app.register_blueprint(analysis_bp)

    @app.context_processor
    def inject_globals():
        return {"app_name": "YosiFix", "lang": session.get("lang", "en"), "t": translate}

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")
        try:
            from migrate_db import upgrade_db
            upgrade_db()
        except Exception:
            pass

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
