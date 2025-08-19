from flask import Blueprint, request, jsonify
from models import db, Alert, Device

api_bp = Blueprint("api", __name__)

@api_bp.route("/alert", methods=["POST"])
def create_alert():
    data = request.json
    device_id = data.get("device_id")
    message = data.get("message")
    alert = Alert(device_id=device_id, message=message)
    db.session.add(alert)
    db.session.commit()
    return jsonify({"success": True, "alert_id": alert.id})

@api_bp.route("/alert/<int:alert_id>/attend", methods=["POST"])
def attend_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.status = "attended"
    db.session.commit()
    return jsonify({"success": True, "alert_id": alert.id})
