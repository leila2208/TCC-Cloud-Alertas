from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Hospital, User, Device, Patient, Alert, SUPERADMIN, ADMIN, NURSE, PATIENT
from utils import require_roles

views_bp = Blueprint("views", _name_)

@views_bp.route("/")
def landing():
    return render_template("landing.html")

@views_bp.route("/alerts")
def alerts_public():
    # página pública con stream de un hospital si se pasa ?hospital_id=#
    hosp_id = request.args.get("hospital_id", type=int)
    hospital = Hospital.query.get(hosp_id) if hosp_id else None
    return render_template("alerts_public.html", hospital=hospital)

# Homes por rol
@views_bp.route("/superadmin")
@login_required
@require_roles(SUPERADMIN)
def superadmin_home():
    hospitals = Hospital.query.all()
    return render_template("admin_dashboard.html", superadmin=True, hospitals=hospitals)

@views_bp.route("/admin")
@login_required
@require_roles(ADMIN)
def admin_home():
    hospital = Hospital.query.get(current_user.hospital_id)
    nurses = User.query.filter_by(hospital_id=hospital.id, role=NURSE).all()
    patients = Patient.query.filter_by(hospital_id=hospital.id).all()
    devices = Device.query.filter_by(hospital_id=hospital.id).all()
    alerts_count = Alert.query.filter_by(hospital_id=hospital.id).count()
    return render_template("admin_dashboard.html", hospital=hospital,
                           nurses=nurses, patients=patients, devices=devices,
                           alerts_count=alerts_count)

@views_bp.route("/nurse")
@login_required
@require_roles(NURSE)
def nurse_home():
    hospital = Hospital.query.get(current_user.hospital_id)
    return render_template("nurse_dashboard.html", hospital=hospital)

@views_bp.route("/patient")
@login_required
@require_roles(PATIENT)
def patient_home():
    hospital = Hospital.query.get(current_user.hospital_id)
    # en un futuro: filtrar por patient vinculado al usuario
    return render_template("patient_dashboard.html", hospital=hospital)

# CRUD mínimos (ADMIN)
@views_bp.route("/admin/create-nurse", methods=["POST"])
@login_required
@require_roles(ADMIN)
def create_nurse():
    name = request.form.get("name").strip()
    email = request.form.get("email").strip().lower()
    pw = request.form.get("password")
    if User.query.filter_by(email=email).first():
        flash("Email ya registrado.")
        return redirect(url_for("views.admin_home"))
    u = User(hospital_id=current_user.hospital_id, name=name, email=email, role=NURSE, active=True)
    u.set_password(pw)
    db.session.add(u)
    db.session.commit()
    flash("Enfermera creada.")
    return redirect(url_for("views.admin_home"))

@views_bp.route("/admin/create-patient", methods=["POST"])
@login_required
@require_roles(ADMIN)
def create_patient():
    name = request.form.get("name").strip()
    bed = request.form.get("bed","").strip()
    diag = request.form.get("diagnosis","").strip()
    p = Patient(hospital_id=current_user.hospital_id, full_name=name, bed=bed, diagnosis=diag)
    db.session.add(p)
    db.session.commit()
    flash("Paciente creado.")
    return redirect(url_for("views.admin_home"))

@views_bp.route("/admin/create-device", methods=["POST"])
@login_required
@require_roles(ADMIN)
def create_device():
    name = request.form.get("name").strip()
    device_key = request.form.get("device_key").strip()
    patient_id = request.form.get("patient_id", type=int)
    d = Device(hospital_id=current_user.hospital_id, name=name, device_key=device_key, patient_id=patient_id or None)
    db.session.add(d)
    db.session.commit()
    flash("TCC registrado.")
    return redirect(url_for("views.admin_home"))
