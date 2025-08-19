from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from models import db, User, Hospital, SUPERADMIN, ADMIN, NURSE, PATIENT

auth_bp = Blueprint("auth", __name__)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"

class LoginUser(UserMixin):
    def _init_(self, user): self.user = user
    @property
    def id(self): return str(self.user.id)
    @property
    def role(self): return self.user.role
    @property
    def hospital_id(self): return self.user.hospital_id

@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(int(user_id))
    return LoginUser(u) if u else None

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        pw = request.form.get("password","")
        u = User.query.filter_by(email=email).first()
        if u and u.check_password(pw) and u.active:
            login_user(LoginUser(u))
            # redirección según rol
            if u.role == SUPERADMIN: return redirect(url_for("views.superadmin_home"))
            if u.role == ADMIN: return redirect(url_for("views.admin_home"))
            if u.role == NURSE: return redirect(url_for("views.nurse_home"))
            return redirect(url_for("views.patient_home"))
        flash("Credenciales inválidas o usuario inactivo.")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.landing"))

# Registro de admin hospital – SOLO SUPERADMIN
@auth_bp.route("/register-admin", methods=["GET","POST"])
def register_admin():
    from flask_login import current_user
    if not current_user.is_authenticated or current_user.role != SUPERADMIN:
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        hosp_name = request.form.get("hospital").strip()
        name = request.form.get("name").strip()
        email = request.form.get("email").strip().lower()
        pw = request.form.get("password")
        hosp = Hospital.query.filter_by(name=hosp_name).first()
        if not hosp:
            hosp = Hospital(name=hosp_name)
            db.session.add(hosp)
            db.session.flush()
        if User.query.filter_by(email=email).first():
            flash("Ese email ya existe.")
            return render_template("register_admin.html")
        u = User(hospital_id=hosp.id, email=email, name=name, role=ADMIN, active=True)
        u.set_password(pw)
        db.session.add(u)
        db.session.commit()
        flash("Admin creado.")
        return redirect(url_for("views.superadmin_home"))
    return render_template("register_admin.html")
