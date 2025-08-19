from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS

app = Flask(_name_)
CORS(app)
app.secret_key = "supersecretkey"

# Lista de tareas inicial
tareas = [
    {"id": 1, "titulo": "Tarea de ejemplo 1", "completada": False},
    {"id": 2, "titulo": "Tarea de ejemplo 2", "completada": True},
]

# --------------------
# RUTAS DE PÁGINAS
# --------------------

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Login simple de ejemplo
        if username == "admin" and password == "1234":
            session["usuario"] = "admin"
            return redirect(url_for("admin"))
        elif username == "user" and password == "1234":
            session["usuario"] = "user"
            return redirect(url_for("publico"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

# Página pública
@app.route("/publico")
def publico():
    if "usuario" not in session or session["usuario"] != "user":
        return redirect(url_for("login"))
    return render_template("publico.html")

# Página admin
@app.route("/admin")
def admin():
    if "usuario" not in session or session["usuario"] != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("index"))

# --------------------
# RUTAS DE TAREAS
# --------------------

@app.route("/tareas", methods=["GET"])
def obtener_tareas():
    return jsonify(tareas)

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

@app.route("/editar/<int:tarea_id>", methods=["PUT"])
def editar_tarea(tarea_id):
    datos = request.json
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["titulo"] = datos.get("titulo", tarea["titulo"])
            tarea["completada"] = datos.get("completada", tarea["completada"])
            return jsonify(tarea)
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route("/eliminar/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    global tareas
    tareas = [t for t in tareas if t["id"] != tarea_id]
    return jsonify({"mensaje": "Tarea eliminada"})

@app.route("/tachar/<int:tarea_id>", methods=["PUT"])
def tachar_tarea(tarea_id):
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["completada"] = not tarea["completada"]
            return jsonify(tarea)
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route("/reset", methods=["POST"])
def reset_tareas():
    global tareas
    tareas = []
    return jsonify({"mensaje": "Lista de tareas vaciada"})


if _name_ == "_main_":
    app.run(debug=True, host="0.0.0.0", port=5000)
