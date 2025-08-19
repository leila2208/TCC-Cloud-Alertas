from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config
from models import db
from auth import auth_bp
from views import views_bp
from api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)
app.register_blueprint(api_bp, url_prefix="/api")

# Crear la base de datos
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
