from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tcc_secret_final"
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --------------------
# MODELOS
# --------------------
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    clave = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), default='enfermera')

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    patologia = db.Column(db.String(200))
    tcc_id = db.Column(db.String(50))
    alertas = db.relationship('Alerta', backref='paciente', lazy=True)

class Alerta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    camilla = db.Column(db.String(10))
    hora = db.Column(db.String(10))
    urgencia = db.Column(db.String(10))
    necesidad = db.Column(db.String(200))
    tachado = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.now)

# --------------------
# LOGIN
# --------------------
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --------------------
# RUTAS
# --------------------
@app.route('/')
@login_required
def index():
    pacientes = Paciente.query.all()
    return render_template('index.html', pacientes=pacientes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        user = Usuario.query.filter_by(nombre=usuario, clave=clave).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = "Usuario o clave incorrectos"
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/paciente', methods=['GET', 'POST'])
@login_required
def paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        patologia = request.form['patologia']
        tcc_id = request.form['tcc_id']
        p = Paciente(nombre=nombre, patologia=patologia, tcc_id=tcc_id)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('paciente.html')

@app.route('/alertas/<int:paciente_id>')
@login_required
def alertas_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    alertas = Alerta.query.filter_by(paciente_id=paciente.id).order_by(Alerta.fecha.desc()).all()
    return render_template('historial.html', paciente=paciente, alertas=alertas)

@app.route('/api/alerta', methods=['POST'])
@login_required
def api_alerta():
    data = request.json
    alerta = Alerta(
        paciente_id=data['paciente_id'],
        camilla=data.get('camilla'),
        hora=data.get('hora', datetime.now().strftime("%H:%M:%S")),
        urgencia=data.get('urgencia', 'baja').lower(),
        necesidad=data.get('necesidad')
    )
    db.session.add(alerta)
    db.session.commit()
    return jsonify({"mensaje": "Alerta agregada"})

@app.route('/api/tachar/<int:alerta_id>', methods=['POST'])
@login_required
def tachar_alerta(alerta_id):
    alerta = Alerta.query.get_or_404(alerta_id)
    alerta.tachado = not alerta.tachado
    db.session.commit()
    return jsonify({"mensaje": "Alerta actualizada"})

@app.route('/admin/stats')
@login_required
def stats():
    if current_user.rol != 'admin':
        return "No autorizado", 403
    totales = Alerta.query.count()
    alto = Alerta.query.filter_by(urgencia='alta').count()
    medio = Alerta.query.filter_by(urgencia='media').count()
    bajo = Alerta.query.filter_by(urgencia='baja').count()
    return jsonify({"total": totales, "alta": alto, "media": medio, "baja": bajo})

# --------------------
# INICIALIZAR DB
# --------------------
@app.before_first_request
def crear_bd():
    db.create_all()
    if not Usuario.query.filter_by(nombre='adminTCC').first():
        admin = Usuario(nombre='adminTCC', clave='4321', rol='admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
