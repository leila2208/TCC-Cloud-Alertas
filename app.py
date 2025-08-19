from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import copy

app = Flask(_name_)
CORS(app)
app.secret_key = "supersecretkey"

# Lista de tareas inicial
tareas = [
    {"id": 1, "titulo": "Tarea de ejemplo 1", "completada": False},
    {"id": 2, "titulo": "Tarea de ejemplo 2", "completada": True},
]

# Página principal
@app.route("/")
def index():
    return render_template("index.html", tareas=tareas)

# Obtener todas las tareas
@app.route("/tareas", methods=["GET"])
def obtener_tareas():
    return jsonify(tareas)

# Agregar nueva tarea
@app.route("/agregar", methods=["POST"])
def agregar_tarea():
    nueva = request.json
    if not nueva or "titulo" not in nueva:
        return jsonify({"error": "Falta el título"}), 400
    
    nueva_tarea = {
        "id": len(tareas) + 1,
        "titulo": nueva["titulo"],
        "completada": False
    }
    tareas.append(nueva_tarea)
    return jsonify(nueva_tarea)

# Editar tarea
@app.route("/editar/<int:tarea_id>", methods=["PUT"])
def editar_tarea(tarea_id):
    datos = request.json
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["titulo"] = datos.get("titulo", tarea["titulo"])
            tarea["completada"] = datos.get("completada", tarea["completada"])
            return jsonify(tarea)
    return jsonify({"error": "Tarea no encontrada"}), 404

# Eliminar tarea
@app.route("/eliminar/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    global tareas
    tareas = [t for t in tareas if t["id"] != tarea_id]
    return jsonify({"mensaje": "Tarea eliminada"})

# Marcar tarea como completada o no
@app.route("/tachar/<int:tarea_id>", methods=["PUT"])
def tachar_tarea(tarea_id):
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["completada"] = not tarea["completada"]
            return jsonify(tarea)
    return jsonify({"error": "Tarea no encontrada"}), 404

# Resetear lista de tareas (opcional)
@app.route("/reset", methods=["POST"])
def reset_tareas():
    global tareas
    tareas = []
    return jsonify({"mensaje": "Lista de tareas vaciada"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

