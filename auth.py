from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("views.admin_dashboard"))
            elif user.role == "nurse":
                return redirect(url_for("views.nurse_dashboard"))
            else:
                return redirect(url_for("views.patient_dashboard"))
        flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth_bp.route("/register_admin", methods=["GET", "POST"])
def register_admin():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            flash("El usuario ya existe")
        else:
            user = User(username=username, password=password, role="admin")
            db.session.add(user)
            db.session.commit()
            flash("Admin registrado correctamente")
            return redirect(url_for("auth.login"))
    return render_template("register_admin.html")
