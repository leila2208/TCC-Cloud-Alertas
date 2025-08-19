from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Hospital, SUPERADMIN
from auth import auth_bp, login_manager
from views import views_bp
from api import api_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/": {"origins": ""}})

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        seed_superadmin()

    return app

def seed_superadmin():
    # Superadmin por defecto (cambiar en producción vía ENV)
    email = "superadmin@tcc.local"
    name = "Super Admin"
    if not User.query.filter_by(email=email).first():
        h = Hospital.query.filter_by(name="Demo Hospital").first()
        if not h:
            from models import Hospital
            h = Hospital(name="Demo Hospital")
            db.session.add(h)
            db.session.flush()
        u = User(name=name, email=email, role=SUPERADMIN, active=True)
        u.set_password("admin123")
        db.session.add(u)
        db.session.commit()

app = create_app()

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)

