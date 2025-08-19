from flask import Blueprint, request, jsonify
from models import db, Device, Alert, Patient, Hospital
from datetime import datetime

api_bp = Blueprint("api", _name_, url_prefix="/api")

# POST /api/alerts
# BODY JSON: { device_key, necesidad, urgencia, patologia, cama, hora? }
@api_bp.route("/alerts", methods=["POST"])
def post_alert():
    data = request.get_json(force=True, silent=True) or {}
    key = (data.get("device_key") or "").strip()
    dev = Device.query.filter_by(device_key=key, active=True).first()
    if not dev:
        return jsonify({"error":"device_key inválida"}), 401

    need = (data.get("necesidad") or "").strip()
    urg = (data.get("urgencia") or "baja").strip().lower()
    pat = (data.get("patologia") or "").strip()
    bed = (data.get("cama") or "").strip()
    hora = data.get("hora")

    alert = Alert(
        hospital_id=dev.hospital_id,
        device_id=dev.id,
        patient_id=dev.patient_id,
        need=need,
        urgency=urg,
        pathology=pat,
        bed=bed or (dev.patient.bed if dev.patient else None),
        timestamp=datetime.strptime(hora, "%H:%M:%S") if hora else datetime.utcnow()
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({"ok": True, "alert_id": alert.id})

# GET /api/alerts?hospital_id=...&role=... (simple feed)
@api_bp.route("/alerts", methods=["GET"])
def list_alerts():
    hosp_id = request.args.get("hospital_id", type=int)
    if not hosp_id: return jsonify([])
    alerts = (Alert.query
              .filter_by(hospital_id=hosp_id)
              .order_by(Alert.timestamp.desc())
              .limit(200).all())
    def s(a):
        return {
            "id": a.id,
            "need": a.need,
            "urgency": a.urgency,
            "pathology": a.pathology,
            "bed": a.bed,
            "timestamp": a.timestamp.isoformat(),
            "done": a.done,
            "device_id": a.device_id,
            "patient": a.patient.full_name if a.patient else None
        }
    return jsonify([s(a) for a in alerts])

# POST /api/alerts/<id>/toggle-done
@api_bp.route("/alerts/<int:alert_id>/toggle-done", methods=["POST"])
def toggle_done(alert_id):
    a = Alert.query.get_or_404(alert_id)
    a.done = not a.done
    db.session.commit()
    return jsonify({"ok": True, "done": a.done})

# DEMO: provisión (flujo futuro – el TCC pide credenciales por pairing_code)
@api_bp.route("/provision", methods=["POST"])
def provision():
    # SOLO DEMO – aquí guardarías mapping pairing_code -> wifi_ssid/wifi_pass por hospital
    # y devolverías cuando el dispositivo lo pida. No expone credenciales reales.
    return jsonify({"ok": True, "message": "Endpoint de demo para provisión."})
