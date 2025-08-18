from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime
import uuid
import copy

app = Flask(_name_)
CORS(app)
app.secret_key = "tcc_secret_2024"

# --------- Estado en memoria (simple) ---------
alertas = []  # lista de alertas recibidas
devices = {}  # device_id -> dict(settings)

# Credenciales de admin
USUARIO_ADMIN = "adminTCC"
CLAVE_ADMIN = "4321"

# Config por defecto (si un device no tiene propia)
DEFAULT_SETTINGS = {
    "paciente": "",
    "camilla": 1,
    "patologia": "",

    # Botones (índice 0..3). 'urgencia' en {baja, media, alta}
    "botones": [
        {"label": "AGUA",       "urgencia": "baja"},
        {"label": "SANITARIO",  "urgencia": "media"},
        {"label": "CONSULTA",   "urgencia": "baja"},
        {"label": "URGENCIA",   "urgencia": "alta"}
    ],

    # Reglas extra de prioridad por patología (opcional)
    "prioridad_patologia": {
        "acv": 2,
        "neumonia": 1
    }
}

def get_settings(device_id: str):
    return devices.get(device_id, copy.deepcopy(DEFAULT_SETTINGS))

def prioridad_score(urgencia: str, patologia: str):
    base = {"baja": 1, "media": 2, "alta": 3}.get((urgencia or "").lower(), 1)
    extra = DEFAULT_SETTINGS["prioridad_patologia"].get((patologia or "").lower(), 0)
    return base + extra

# --------- Rutas públicas ---------
@app.route("/")
def index():
    return render_template("publico.html")

@app.route("/datos", methods=["GET"])
def datos():
    # devolvemos las alertas ya existentes (ordenadas por prioridad DESC y luego hora DESC)
    ordenadas = sorted(
        alertas,
        key=lambda a: (a.get("prioridad", 0), a.get("timestamp", "")),
        reverse=True
    )
    return jsonify(ordenadas)

# --------- Dispositivos / API ---------
@app.route("/api/register", methods=["POST"])
def api_register():
    """Registro simple: genera un device_id."""
    new_id = str(uuid.uuid4())[:8]
    if new_id not in devices:
        devices[new_id] = copy.deepcopy(DEFAULT_SETTINGS)
    return jsonify({"device_id": new_id})

@app.route("/api/settings", methods=["GET", "PUT"])
def api_settings():
    device_id = request.args.get("device_id", "default")

    if request.method == "GET":
        s = get_settings(device_id)
        return jsonify(s)

    # PUT (solo admin)
    if not session.get('logged_in'):
        return "No autorizado", 401

    data = request.json or {}
    cur = devices.get(device_id, copy.deepcopy(DEFAULT_SETTINGS))

    # Campos simples
    for k in ["paciente", "camilla", "patologia"]:
        if k in data:
            cur[k] = data[k]

    # Botones
    if "botones" in data and isinstance(data["botones"], list):
        nuevos = []
        for i in range(min(4, len(data["botones"]))):
            b = data["botones"][i]
            label = b.get("label", cur["botones"][i]["label"] if i < len(cur["botones"]) else "BTN")
            urg = (b.get("urgencia", "baja") or "baja").lower()
            if urg not in ["baja", "media", "alta"]:
                urg = "baja"
            nuevos.append({"label": label, "urgencia": urg})
        while len(nuevos) < 4:
            nuevos.append({"label": f"BTN{len(nuevos)+1}", "urgencia": "baja"})
        cur["botones"] = nuevos

    # Reglas por patología
    if "prioridad_patologia" in data and isinstance(data["prioridad_patologia"], dict):
        cur["prioridad_patologia"] = {k.lower(): int(v) for k, v in data["prioridad_patologia"].items()}

    devices[device_id] = cur
    return jsonify({"ok": True, "settings": cur})

@app.route("/api/alerts", methods=["POST"])
def api_alerts():
    data = request.json or {}
    device_id = data.get("device_id", "default")
    s = get_settings(device_id)

    boton_idx = int(data.get("boton_idx", -1))
    if 0 <= boton_idx < 4:
        if not data.get("necesidad"):
            data["necesidad"] = s["botones"][boton_idx]["label"]
        if not data.get("urgencia"):
            data["urgencia"] = s["botones"][boton_idx]["urgencia"]

    if not data.get("camilla"):
        data["camilla"] = s.get("camilla", 1)
    if not data.get("paciente"):
        data["paciente"] = s.get("paciente", "")
    if not data.get("patologia"):
        data["patologia"] = s.get("patologia", "")

    if not data.get("hora"):
        data["hora"] = datetime.now().strftime("%H:%M:%S")
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data["prioridad"] = prioridad_score(data.get("urgencia", "baja"), data.get("patologia", ""))
    data["id"] = f"{device_id}-{data['camilla']}-{data['hora']}-{data.get('necesidad','')}"
    data["tachado"] = False

    alertas.append(data)
    return jsonify({"ok": True, "total": len(alertas)})

# --------- Admin ---------
@app.route("/admin")
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    known = ["default"] + list(devices.keys())
    return render_template("admin.html", device_ids=known)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")
        if usuario == USUARIO_ADMIN and clave == CLAVE_ADMIN:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        return "Credenciales incorrectas"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/limpiar", methods=["POST"])
def limpiar():
    if not session.get('logged_in'):
        return "No autorizado", 401
    alertas.clear()
    return jsonify({"ok": True})

@app.route("/tachar", methods=["POST"])
def tachar():
    if not session.get('logged_in'):
        return "No autorizado", 401
    payload = request.json or {}
    _id = payload.get("id")
    for a in alertas:
        if a.get("id") == _id:
            a["tachado"] = not a.get("tachado", False)
            break
    return jsonify({"ok": True})

# --------- Main ---------
if _name_ == "_main_":
    app.run(debug=True, host="0.0.0.0", port=5000)
