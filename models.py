from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Roles
SUPERADMIN = "SUPERADMIN"
ADMIN = "ADMIN"
NURSE = "NURSE"
PATIENT = "PATIENT"

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship("User", backref="hospital", lazy=True)
    devices = db.relationship("Device", backref="hospital", lazy=True)
    patients = db.relationship("Patient", backref="hospital", lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=NURSE)
    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    device_key = db.Column(db.String(64), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    alerts = db.relationship("Alert", backref="device", lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    bed = db.Column(db.String(50), nullable=True)
    diagnosis = db.Column(db.String(200), nullable=True)
    device = db.relationship("Device", backref="patient", uselist=False)
    alerts = db.relationship("Alert", backref="patient", lazy=True)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("device.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=True)
    need = db.Column(db.String(80), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)  # baja/media/alta
    pathology = db.Column(db.String(120), nullable=True)
    bed = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    done = db.Column(db.Boolean, default=False)

    def urgency_rank(self):
        m = {"alta": 3, "media": 2, "baja": 1}
        return m.get((self.urgency or "").lower(), 1)
