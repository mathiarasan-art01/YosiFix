import os
from flask import Flask, session
from config import Config
from extensions import db, login_manager
from modules.i18n import t as translate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    instance_dir = os.path.join(app.root_path, "instance")
    os.makedirs(instance_dir, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.main import bp as main_bp
    from routes.auth import bp as auth_bp
    from routes.idea import bp as idea_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(idea_bp)

    @app.context_processor
    def inject_globals():
        return {"app_name": "YosiFix", "lang": session.get("lang", "en"), "t": translate}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
