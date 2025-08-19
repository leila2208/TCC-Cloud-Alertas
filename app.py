from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, Hospital, User, SUPERADMIN

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    with app.app_context():
        db.create_all()
        seed_superadmin()

    return app

def seed_superadmin():
    # Crear hospital si no existe
    h = Hospital.query.filter_by(name="Demo Hospital").first()
    if not h:
        h = Hospital(name="Demo Hospital")
        db.session.add(h)
        db.session.commit()

    # Crear superadmin si no existe
    sa = User.query.filter_by(email="superadmin@example.com").first()
    if not sa:
        sa = User(
            name="Super Admin",
            email="superadmin@example.com",
            role=SUPERADMIN,
            hospital_id=h.id
        )
        sa.set_password("supersecret")  # Cambia la contraseña
        db.session.add(sa)
        db.session.commit()

app = create_app()

# Opcional: ruta de prueba
@app.route("/")
def index():
    return "App corriendo correctamente"
