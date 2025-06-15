from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)

alertas = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datos', methods=['GET'])
def datos():
    return jsonify(alertas)

@app.route('/alerta', methods=['POST'])
def recibir_alerta():
    global alertas
    data = request.json

    if 'hora' not in data or not data['hora']:
        data['hora'] = datetime.now().strftime("%H:%M:%S")

    if 'urgencia' in data:
        data['urgencia'] = data['urgencia'].lower()

    alertas.append(data)
    return jsonify({"mensaje": "Alerta agregada", "alertas_totales": len(alertas)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
