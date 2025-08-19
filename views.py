from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Alert

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def landing():
    return render_template("landing.html")

@views_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "No autorizado", 403
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    return render_template("admin_dashboard.html", alerts=alerts)

@views_bp.route("/nurse_dashboard")
@login_required
def nurse_dashboard():
    if current_user.role != "nurse":
        return "No autorizado", 403
    alerts = Alert.query.filter_by(status="pending").order_by(Alert.timestamp.desc()).all()
    return render_template("nurse_dashboard.html", alerts=alerts)

@views_bp.route("/patient_dashboard")
@login_required
def patient_dashboard():
    return render_template("patient_dashboard.html")
