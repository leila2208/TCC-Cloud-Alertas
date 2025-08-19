from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, Hospital, User, Role
from functools import wraps
import logging
from flask_restx import Api, Resource, fields

# ====================== LOGGING ======================
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# ====================== CREACIÓN DE APP ======================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    api = Api(app, version='1.0', title='TCC API',
              description='API de ejemplo profesional con Flask, JWT y Swagger')

    with app.app_context():
        db.create_all()
        seed_superadmin()

    # ====================== MODELOS PARA SWAGGER ======================
    hospital_model = api.model('Hospital', {
        'id': fields.Integer(readonly=True),
        'name': fields.String(required=True)
    })

    user_model = api.model('User', {
        'id': fields.Integer(readonly=True),
        'username': fields.String(required=True),
        'role': fields.String(required=True)
    })

    # ====================== DECORADOR DE ROLES ======================
    def role_required(required_role):
        def decorator(func):
            @wraps(func)
            @jwt_required()
            def wrapper(*args, **kwargs):
                username = get_jwt_identity()
                user = User.query.filter_by(username=username).first()
                if not user or user.role.name != required_role:
                    return jsonify({"error": "No autorizado"}), 403
                return func(*args, **kwargs)
            return wrapper
        return decorator

    # ====================== RUTAS ======================
    @app.route("/")
    def index():
        return jsonify({"message": "App corriendo correctamente"})

    # ---------- HOSPITALES ----------
    @api.route('/hospitals')
    class HospitalList(Resource):
        @jwt_required()
        @api.marshal_list_with(hospital_model)
        def get(self):
            hospitals = Hospital.query.all()
            return hospitals

        @role_required("superadmin")
        @api.expect(hospital_model)
        def post(self):
            data = request.get_json()
            name = data.get("name")
            if not name:
                return {"error": "Falta el nombre"}, 400
            if Hospital.query.filter_by(name=name).first():
                return {"error": "Hospital ya existe"}, 400
            hospital = Hospital(name=name)
            db.session.add(hospital)
            db.session.commit()
            logging.info(f"Hospital creado: {name}")
            return {"message": "Hospital creado", "id": hospital.id}, 201

    @api.route('/hospitals/<int:hospital_id>')
    class HospitalDetail(Resource):
        @jwt_required()
        @api.marshal_with(hospital_model)
        def get(self, hospital_id):
            hospital = Hospital.query.get_or_404(hospital_id)
            return hospital

        @role_required("superadmin")
        @api.expect(hospital_model)
        def put(self, hospital_id):
            hospital = Hospital.query.get_or_404(hospital_id)
            data = request.get_json()
            name = data.get("name")
            if name:
                hospital.name = name
                db.session.commit()
                logging.info(f"Hospital actualizado: {name}")
            return {"message": "Hospital actualizado", "id": hospital.id}

        @role_required("superadmin")
        def delete(self, hospital_id):
            hospital = Hospital.query.get_or_404(hospital_id)
            db.session.delete(hospital)
            db.session.commit()
            logging.info(f"Hospital eliminado: {hospital.name}")
            return {"message": "Hospital eliminado"}

    # ---------- USUARIOS ----------
    @api.route('/users')
    class UserList(Resource):
        @role_required("superadmin")
        @api.marshal_list_with(user_model)
        def get(self):
            users = User.query.all()
            return [{"id": u.id, "username": u.username, "role": u.role.name} for u in users]

        @role_required("superadmin")
        @api.expect(user_model)
        def post(self):
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            role_name = data.get("role", "user")
            if not username or not password:
                return {"error": "Falta username o password"}, 400
            if User.query.filter_by(username=username).first():
                return {"error": "Usuario ya existe"}, 400
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
                db.session.commit()
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logging.info(f"Usuario creado: {username}")
            return {"message": "Usuario creado", "id": user.id}, 201

    # ---------- LOGIN ----------
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            logging.warning(f"Login fallido: {username}")
            return {"error": "Usuario o contraseña incorrecta"}, 401
        access_token = create_access_token(identity=username)
        logging.info(f"Login exitoso: {username}")
        return {"access_token": access_token, "role": user.role.name}

    # ====================== MANEJO GLOBAL DE ERRORES ======================
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="Solicitud incorrecta"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error="No autorizado"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error="Prohibido"), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="No encontrado"), 404

    @app.errorhandler(500)
    def server_error(e):
        logging.error(f"Error interno: {e}")
        return jsonify(error="Error interno del servidor"), 500

    return app

# ====================== SEED INICIAL ======================
def seed_superadmin():
    admin_role = Role.query.filter_by(name="superadmin").first()
    if not admin_role:
        admin_role = Role(name="superadmin")
        db.session.add(admin_role)
        db.session.commit()
    superadmin = User.query.filter_by(username="superadmin").first()
    if not superadmin:
        superadmin = User(username="superadmin", role=admin_role)
        superadmin.set_password("admin123")
        db.session.add(superadmin)
        db.session.commit()

# ====================== RUN ======================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
