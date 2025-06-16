from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)
app.secret_key = "tcc_secret_2024"

alertas = []

# Login de administrador
USUARIO_ADMIN = "adminTCC"
CLAVE_ADMIN = "4321"

@app.route('/')
def index():
    return render_template('publico.html', alertas=alertas)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html', alertas=alertas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        if usuario == USUARIO_ADMIN and clave == CLAVE_ADMIN:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Credenciales incorrectas"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/datos', methods=['GET', 'POST'])
def datos():
    global alertas
    if request.method == 'POST':
        data = request.json

        if 'hora' not in data or not data['hora']:
            data['hora'] = datetime.now().strftime("%H:%M:%S")

        if 'urgencia' in data:
            data['urgencia'] = data['urgencia'].lower()

        alertas.append(data)
        return jsonify({"mensaje": "Alerta agregada", "alertas_totales": len(alertas)})
    else:
        return jsonify(alertas)

@app.route('/limpiar', methods=['POST'])
def limpiar():
    global alertas
    alertas = []
    return jsonify({"mensaje": "Alertas limpiadas"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
