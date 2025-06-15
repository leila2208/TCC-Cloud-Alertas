from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

alertas = []

@app.route("/")
def home():
    return render_template("index.html", alertas=alertas)

@app.route("/alerta", methods=["POST"])
def recibir_alerta():
    data = request.get_json()
    alertas.append(data)
    return jsonify({"mensaje": "Alerta recibida"}), 200

@app.route("/visualizacion")
def visualizacion():
    return render_template("visual.html", alertas=alertas)

@app.route("/reset", methods=["POST"])
def reset_alertas():
    alertas.clear()
    return jsonify({"mensaje": "Alertas limpiadas"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)