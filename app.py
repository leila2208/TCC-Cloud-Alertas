# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ---------------------
# Configuración básica
# ---------------------
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///app.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")

# ---------------------
# Extensiones
# ---------------------
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
jwt = JWTManager(app)
api = Api(app, title="Tienda API", version="1.0", description="API lista para producción")

# ---------------------
# Modelos
# ---------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="user")  # user o admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, completed, cancelled

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------
# Serializadores Flask-RESTx
# ---------------------
auth_ns = Namespace('auth', description='Autenticación')
products_ns = Namespace('products', description='Productos')
orders_ns = Namespace('orders', description='Pedidos')

user_model = auth_ns.model('User', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

product_model = products_ns.model('Product', {
    'name': fields.String(required=True),
    'description': fields.String(),
    'price': fields.Float(required=True),
    'stock': fields.Integer(required=True)
})

order_model = orders_ns.model('Order', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True)
})

# ---------------------
# Endpoints Auth
# ---------------------
@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return {"message": "Usuario ya existe"}, 400
        user = User(username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return {"message": "Usuario registrado"}, 201

@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token, "role": user.role}, 200
        return {"message": "Usuario o contraseña incorrectos"}, 401

@auth_ns.route("/logout")
class Logout(Resource):
    @login_required
    def post(self):
        logout_user()
        return {"message": "Sesión cerrada"}, 200

# ---------------------
# Endpoints Productos
# ---------------------
@products_ns.route("/")
class ProductList(Resource):
    @products_ns.marshal_list_with(product_model)
    def get(self):
        return Product.query.all()

    @jwt_required()
    @products_ns.expect(product_model)
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Solo admins pueden agregar productos"}, 403
        data = request.json
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return {"message": "Producto agregado"}, 201

@products_ns.route("/<int:id>")
class ProductDetail(Resource):
    @products_ns.marshal_with(product_model)
    def get(self, id):
        product = Product.query.get_or_404(id)
        return product

    @jwt_required()
    @products_ns.expect(product_model)
    def put(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Solo admins pueden editar productos"}, 403
        product = Product.query.get_or_404(id)
        for key, value in request.json.items():
            setattr(product, key, value)
        db.session.commit()
        return {"message": "Producto actualizado"}

    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != "admin":
            return {"message": "Solo admins pueden eliminar productos"}, 403
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return {"message": "Producto eliminado"}

# ---------------------
# Endpoints Pedidos
# ---------------------
@orders_ns.route("/")
class OrderList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return Order.query.filter_by(user_id=user_id).all()

    @jwt_required()
    @orders_ns.expect(order_model)
    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        product = Product.query.get_or_404(data['product_id'])
        if product.stock < data['quantity']:
            return {"message": "Stock insuficiente"}, 400
        product.stock -= data['quantity']
        order = Order(user_id=user_id, product_id=product.id, quantity=data['quantity'])
        db.session.add(order)
        db.session.commit()
        return {"message": "Pedido creado"}, 201

# ---------------------
# Registrar Namespaces
# ---------------------
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(products_ns, path="/products")
api.add_namespace(orders_ns, path="/orders")

# ---------------------
# Ping de prueba
# ---------------------
@app.route("/ping")
def ping():
    return {"message": "pong"}

# ---------------------
# Ejecutar app
# ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
